"""F5 + F6: citation check, reduce (merge duplicate rules), grounding check, support threshold."""
import re
from concurrent.futures import ThreadPoolExecutor

from . import llm
from .common import load, workers as default_workers, progress, save

MIN_COMMENTS = 3
MIN_PRS = 2
CHUNK = 200
MAX_EVIDENCE = 30

MERGE_SYSTEM = """You merge duplicate house rules extracted from a project's code-review comments.
Group candidate rules that state the same convention (even if worded differently). Do not group rules \
that are merely related. Every candidate index must appear in exactly one group.

Reply with JSON only:
{"groups": [{"id": "<short-kebab-case-id>", "rule": "<best imperative one-sentence wording>", \
"why": "<one sentence>", "members": [<candidate index>, ...]}]}"""

VERIFY_SYSTEM = """You check evidence for a proposed code-review house rule.
For each numbered maintainer comment, decide whether the comment itself asks for, enforces, or states \
this rule (not merely mentions the same topic).

Reply with JSON only: {"supporting": [<comment id>, ...]}"""


def ids_of(rule):
    out = []
    for x in rule.get("comment_ids") or []:
        try:
            out.append(int(x))
        except (TypeError, ValueError):
            out.append(None)
    return out


def citation_check(candidates, known):
    """F6: a rule citing any comment id that is not in the mined training set is rejected outright."""
    kept, rejected = [], []
    for r in candidates:
        ids = ids_of(r)
        if not ids or any(i not in known for i in ids):
            rejected.append(r)
        else:
            kept.append({"rule": str(r["rule"]).strip(), "why": str(r.get("why") or "").strip(),
                         "comment_ids": sorted(set(ids))})
    return kept, rejected


def merge_chunk(items):
    listing = "\n".join(f"{i}: {r['rule']}" for i, r in enumerate(items))
    out = llm.chat_json(MERGE_SYSTEM, listing, max_tokens=8192)
    groups = (out or {}).get("groups") if isinstance(out, dict) else None
    if not isinstance(groups, list):
        return items
    merged, used = [], set()
    for g in groups:
        members = [m for m in g.get("members") or [] if isinstance(m, int) and 0 <= m < len(items) and m not in used]
        if not members:
            continue
        used.update(members)
        merged.append({"id": g.get("id"), "rule": g.get("rule") or items[members[0]]["rule"],
                       "why": g.get("why") or items[members[0]]["why"],
                       "comment_ids": sorted({i for m in members for i in items[m]["comment_ids"]})})
    merged += [items[i] for i in range(len(items)) if i not in used]  # never drop what the model skipped
    return merged


def reduce(items, repo):
    """Merge in chunks; repeat on the merged output while it keeps shrinking."""
    while True:
        progress(repo, "merge", f"merging {len(items)} rules")
        chunks = [items[i:i + CHUNK] for i in range(0, len(items), CHUNK)]
        with ThreadPoolExecutor(4) as pool:
            merged = [r for chunk in pool.map(merge_chunk, chunks) for r in chunk]
        if len(chunks) == 1 or len(merged) >= len(items):
            return merged
        items = sorted(merged, key=lambda r: r["rule"].lower())


def verify(rule, by_id):
    """Grounding check: keep only cited comments that actually state the rule."""
    kept = []
    for k in range(0, len(rule["comment_ids"]), MAX_EVIDENCE):
        ids = rule["comment_ids"][k:k + MAX_EVIDENCE]
        listing = "\n\n".join(f"[{i}] {by_id[i]['body'][:500]}" for i in ids)
        out = llm.chat_json(VERIFY_SYSTEM, f"Rule: {rule['rule']}\n\nComments:\n{listing}")
        sup = (out or {}).get("supporting") if isinstance(out, dict) else None
        if not isinstance(sup, list):
            kept += ids  # verifier failed: fall back to the citation-checked ids
            continue
        sup = {int(x) for x in sup if str(x).isdigit()}
        kept += [i for i in ids if i in sup]
    return kept


def slug(text, taken):
    base = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:40].strip("-") or "rule"
    s, n = base, 2
    while s in taken:
        s, n = f"{base}-{n}", n + 1
    taken.add(s)
    return s


def supported(ids, by_id):
    return len(ids) >= MIN_COMMENTS and len({by_id[i]["pr"] for i in ids}) >= MIN_PRS


def run(repo, verify_evidence=True, workers=None):
    workers = workers or default_workers()
    comments = load(repo, "comments.json")
    cand = load(repo, "candidates.json")
    by_id = {c["id"]: c for c in comments if c["split"] == "train"}

    kept, rejected = citation_check(cand["candidates"], set(by_id))
    progress(repo, "merge", f"citation check: {len(rejected)} of {len(cand['candidates'])} candidate rules "
             "cited comments that do not exist and were rejected")
    merged = reduce(sorted(kept, key=lambda r: r["rule"].lower()), repo)

    pool_rules = [r for r in merged if supported(r["comment_ids"], by_id)]
    dropped_citations = 0
    if verify_evidence and pool_rules:
        progress(repo, "verify", f"checking evidence for {len(pool_rules)} rules", 0, len(pool_rules))
        with ThreadPoolExecutor(workers) as pool:
            for n, (r, ids) in enumerate(zip(pool_rules, pool.map(lambda r: verify(r, by_id), pool_rules)), 1):
                dropped_citations += len(r["comment_ids"]) - len(ids)
                r["comment_ids"] = ids
                progress(repo, "verify", r["rule"][:60], n, len(pool_rules))
    final = [r for r in pool_rules if supported(r["comment_ids"], by_id)]

    taken, rules = set(), []
    for r in sorted(final, key=lambda r: -len(r["comment_ids"])):
        ev = sorted((by_id[i] for i in r["comment_ids"]), key=lambda c: c["created_at"])
        rules.append({
            "id": slug(r.get("id") or r["rule"], taken),
            "rule": r["rule"],
            "why": r["why"],
            "support": len(ev),
            "prs": len({c["pr"] for c in ev}),
            "since": ev[0]["created_at"][:4],
            "evidence": [{"comment_id": c["id"], "url": c["url"], "pr": c["pr"], "author": c["author"],
                          "created_at": c["created_at"], "quote": c["body"][:280]} for c in ev],
        })

    meta = load(repo, "meta.json")
    out = {
        "repo": meta["repo"], "mined": meta["mined"], "train": meta["train"], "model": cand["model"], "provider": cand.get("provider"),
        "candidates": len(cand["candidates"]), "rejected_rules": len(rejected),
        "rejected_examples": [{"rule": r.get("rule"), "comment_ids": r.get("comment_ids")} for r in rejected[:10]],
        "unsupported_citations": dropped_citations,
        "below_threshold": len(merged) - len(final),
        "threshold": {"min_comments": MIN_COMMENTS, "min_prs": MIN_PRS},
        "rules": rules,
    }
    save(repo, "rules.json", out)
    progress(repo, "merge", f"{len(rules)} rules kept; {len(rejected)} rejected by citation check; "
             f"{dropped_citations} citations dropped by grounding check")
    return out
