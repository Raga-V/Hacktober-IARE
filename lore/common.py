"""Shared paths and JSON helpers. Every stage reads and writes JSON in out/<owner>__<repo>/."""
import json
import os
import sys
from pathlib import Path


def workers():
    """Parallel model calls. Lower it (LORE_WORKERS=2) on free tiers with tight rate limits."""
    return int(os.environ.get("LORE_WORKERS", "8"))


def load_env(path=".env"):
    """Minimal .env loader so the team can share one file of keys; real env vars win."""
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and not key.strip().startswith("#") and value.strip():
                os.environ.setdefault(key.strip(), value.strip().strip('"'))


def parse_repo(repo):
    repo = repo.strip().removeprefix("https://github.com/").removesuffix(".git").strip("/")
    parts = repo.split("/")
    if len(parts) < 2:
        sys.exit(f"Expected owner/repo, got {repo!r}")
    return f"{parts[0]}/{parts[1]}"


def out_dir(repo):
    owner, name = parse_repo(repo).split("/")
    d = Path(os.environ.get("LORE_OUT", "out")) / f"{owner}__{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load(repo, name):
    return json.loads((out_dir(repo) / name).read_text(encoding="utf-8"))


def save(repo, name, data):
    path = out_dir(repo) / name
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return path


def progress(repo, stage, msg, done=None, total=None):
    """Print progress and mirror it to progress.json so the web page can show a live run."""
    line = f"[{stage}] {msg}" + (f" ({done}/{total})" if total else "")
    print(line, flush=True)
    save(repo, "progress.json", {"stage": stage, "msg": msg, "done": done, "total": total})
