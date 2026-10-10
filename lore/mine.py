"""F1–F3: mine maintainer PR review comments, filter, and split train/holdout by date."""
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .common import parse_repo, progress, save

API = "https://api.github.com"
MAINTAINERS = {"OWNER", "MEMBER", "COLLABORATOR"}
MIN_CHARS = 20


def token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok:
        try:
            tok = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            tok = None
    return tok


def session():
    s = requests.Session()
    retry = Retry(total=5, connect=5, read=5, backoff_factor=1, status_forcelist=[502, 503, 504],
                  allowed_methods=["GET"])
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=16))
    s.headers["Accept"] = "application/vnd.github+json"
    tok = token()
    if tok:
        s.headers["Authorization"] = f"Bearer {tok}"
    return s


def get(s, url, **params):
    """GET with retries on dropped connections and truncated bodies (flaky venue Wi-Fi)."""
    for attempt in range(5):
        try:
            return s.get(url, params=params, timeout=30)
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def is_bot(user):
    return not user or user.get("type") == "Bot" or user.get("login", "").endswith("[bot]")


def clean(body):
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)  # markdown images
    body = re.sub(r"<[^>]+>", "", body).replace("&nbsp;", " ")
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def keep(item):
    body = clean(item.get("body"))
    return item.get("author_association") in MAINTAINERS and not is_bot(item.get("user")) and len(body) >= MIN_CHARS


def to_record(item, pr, kind):
    return {
        "id": item["id"],
        "pr": pr,
        "author": item["user"]["login"],
        "assoc": item["author_association"],
        "created_at": (item.get("created_at") or item.get("submitted_at"))[:10],
        "path": item.get("path"),
        "body": clean(item["body"]),
        "url": item["html_url"],
        "kind": kind,
    }


def pr_number(item):
    return int(re.search(r"/pulls/(\d+)$", item["pull_request_url"]).group(1))


def mine_inline(s, repo, max_comments, max_pages):
    """Newest-first inline review comments, keeping maintainers only, until max_comments are kept."""
    kept, url = [], f"{API}/repos/{repo}/pulls/comments"
    params = {"sort": "created", "direction": "desc", "per_page": 100}
    for page in range(1, max_pages + 1):
        r = get(s, url, **params, page=page)
        r.raise_for_status()
        items = r.json()
        if not items:
            break
        kept += [to_record(i, pr_number(i), "inline") for i in items if keep(i)]
        progress(repo, "mine", f"page {page}: {len(kept)} maintainer comments", len(kept), max_comments)
        if len(kept) >= max_comments:
            break
    return kept[:max_comments]


def mine_reviews(s, repo, prs, workers=8):
    """Review summary bodies (approve / request changes text) for the given PRs."""
    def fetch(pr):
        try:
            r = get(s, f"{API}/repos/{repo}/pulls/{pr}/reviews", per_page=100)
        except requests.RequestException:
            return []  # review bodies are a bonus; inline comments carry most rules
        if r.status_code != 200:
            return []
        return [to_record(i, pr, "review") for i in r.json() if keep(i)]

    out = []
    with ThreadPoolExecutor(workers) as pool:
        for n, recs in enumerate(pool.map(fetch, prs), 1):
            out += recs
            if n % 25 == 0 or n == len(prs):
                progress(repo, "mine", f"review bodies: {n} PRs scanned", n, len(prs))
    return out


def split(comments, holdout_days, now=None):
    """Holdout = last `holdout_days` days. If that window holds <20 or >30% of comments
    (quiet or very busy repo), fall back to the newest 20% in time order. `comments` must be
    sorted oldest first. Returns split metadata."""
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=holdout_days)).strftime("%Y-%m-%d")
    first = next((i for i, c in enumerate(comments) if c["created_at"] >= cutoff), len(comments))
    method = f"last {holdout_days} days"
    if len(comments) - first < 20 or len(comments) - first > 0.3 * len(comments):
        first, method = int(len(comments) * 0.8), "newest 20% by time"
    for i, c in enumerate(comments):
        c["split"] = "holdout" if i >= first else "train"
    return {"holdout_since": comments[first]["created_at"] if first < len(comments) else None,
            "split_method": method}


def pr_authors(s, repo, prs, max_pages=40):
    """PR number -> author login, newest PRs first, until every PR in `prs` is seen."""
    need, authors = set(prs), {}
    for page in range(1, max_pages + 1):
        try:
            r = get(s, f"{API}/repos/{repo}/pulls", state="all", sort="created", direction="desc",
                    per_page=100, page=page)
        except requests.RequestException:
            break  # best effort: comments on PRs we could not resolve are kept
        if r.status_code != 200 or not r.json():
            break
        for pr in r.json():
            authors[pr["number"]] = (pr.get("user") or {}).get("login")
        if need <= authors.keys() or min(authors) <= min(need):
            break
    return authors


def run(repo, max_comments=3000, max_pages=100, review_prs=300, holdout_days=60):
    repo = parse_repo(repo)
    s = session()
    meta = get(s, f"{API}/repos/{repo}")
    meta.raise_for_status()
    meta = meta.json()

    comments = mine_inline(s, repo, max_comments, max_pages)
    if review_prs:
        prs = list(dict.fromkeys(c["pr"] for c in comments))[:review_prs]
        seen = {c["id"] for c in comments}
        comments += [r for r in mine_reviews(s, repo, prs) if r["id"] not in seen]
    # A maintainer replying on their own PR is explaining, not enforcing a rule on a contributor.
    authors = pr_authors(s, repo, {c["pr"] for c in comments})
    comments = [c for c in comments if authors.get(c["pr"]) != c["author"]]
    comments.sort(key=lambda c: (c["created_at"], c["id"]))

    info = split(comments, holdout_days)
    save(repo, "comments.json", comments)
    stats = {
        "repo": repo,
        "default_branch": meta.get("default_branch", "main"),
        "license": (meta.get("license") or {}).get("spdx_id"),
        "mined": len(comments),
        "train": sum(c["split"] == "train" for c in comments),
        "holdout": sum(c["split"] == "holdout" for c in comments),
        "prs": len({c["pr"] for c in comments}),
        "first": comments[0]["created_at"] if comments else None,
        "last": comments[-1]["created_at"] if comments else None,
        **info,
    }
    save(repo, "meta.json", stats)
    progress(repo, "mine", f"{stats['mined']} comments from {stats['prs']} PRs; "
             f"train {stats['train']}, holdout {stats['holdout']} ({info['split_method']})")
    return stats
