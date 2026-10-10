"""Lore CLI: python -m lore <command> owner/repo"""
import argparse
import json
import os
import time
from pathlib import Path

from . import emit_skill, evaluate, extract, llm, merge, mine
from .common import load_env, parse_repo, progress


def write_index():
    """out/index.json lists every repo with finished results, for the web page."""
    root = Path(os.environ.get("LORE_OUT", "out"))
    runs = sorted(p.name for p in root.iterdir() if (p / "rules.json").exists()) if root.exists() else []
    (root / "index.json").write_text(json.dumps(runs), encoding="utf-8")


def pipeline(repo, max_comments=3000, review_prs=300, holdout_days=60, eval_n=150, verify=True, fresh=True,
             max_pages=100):
    repo = parse_repo(repo)
    t0 = time.time()
    try:
        progress(repo, "start", f"Lore on {repo} with {llm.model()} via {llm.provider()}")
        if fresh:
            mine.run(repo, max_comments=max_comments, review_prs=review_prs, holdout_days=holdout_days,
                     max_pages=max_pages)
        extract.run(repo)
        merge.run(repo, verify_evidence=verify)
        errors = emit_skill.run(repo)
        evaluate.run(repo, eval_n=eval_n)
        write_index()
        progress(repo, "done", f"finished in {time.time() - t0:.0f}s" + (" (skill INVALID)" if errors else ""))
    except (Exception, SystemExit) as e:  # SystemExit: missing key or no open model
        progress(repo, "error", f"{type(e).__name__}: {e}")
        raise


def main():
    p = argparse.ArgumentParser(prog="lore", description="Compile a repo's review history into an Agent Skill.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models", help="list the provider's models and the open-weight one Lore will use")

    def add(name, help):
        s = sub.add_parser(name, help=help)
        s.add_argument("repo", help="owner/repo or GitHub URL")
        return s

    for s in [add("run", "full pipeline"), add("mine", "F1-F3: mine and split comments")]:
        s.add_argument("--max-comments", type=int, default=3000)
        s.add_argument("--review-prs", type=int, default=300, help="PRs to fetch review bodies for (0 = skip)")
        s.add_argument("--holdout-days", type=int, default=60)
        s.add_argument("--max-pages", type=int, default=100, help="API pages of raw comments to scan (100 each)")
    run_p = sub.choices["run"]
    run_p.add_argument("--live", action="store_true", help="fast demo mode: ~300 comments, no review bodies")
    run_p.add_argument("--cached", action="store_true", help="reuse comments.json instead of re-mining")
    run_p.add_argument("--eval-n", type=int, default=150)
    run_p.add_argument("--no-verify", action="store_true", help="skip the per-rule grounding check")
    add("extract", "F4: map step")
    add("merge", "F5-F6: reduce + citation check").add_argument("--no-verify", action="store_true")
    add("emit", "F7: write and validate the skill")
    add("eval", "F8: holdout evaluation").add_argument("--eval-n", type=int, default=150)
    chk = add("check", "review a PR (number, URL or diff file) against the learned rules")
    chk.add_argument("pr", help="PR number, PR URL, or path to a .diff file")
    serve = sub.add_parser("serve", help="serve the web page with live mode")
    serve.add_argument("--port", type=int, default=8000)

    a = p.parse_args()
    load_env()
    if a.cmd == "models":
        ids = llm.list_models()
        for m in ids:
            print(("  open   " if llm.is_open(m) else "  closed ") + m)
        print(f"\nLore will use: {llm.model()} via {llm.provider()}")
    elif a.cmd == "run":
        if a.live:
            a.max_comments, a.review_prs, a.eval_n = min(a.max_comments, 300), 0, min(a.eval_n, 60)
        pipeline(a.repo, a.max_comments, a.review_prs, a.holdout_days, a.eval_n, not a.no_verify, not a.cached,
                 a.max_pages)
    elif a.cmd == "mine":
        mine.run(a.repo, max_comments=a.max_comments, review_prs=a.review_prs, holdout_days=a.holdout_days,
                 max_pages=a.max_pages)
    elif a.cmd == "extract":
        extract.run(a.repo)
    elif a.cmd == "merge":
        merge.run(a.repo, verify_evidence=not a.no_verify)
    elif a.cmd == "emit":
        raise SystemExit(1 if emit_skill.run(a.repo) else 0)
    elif a.cmd == "eval":
        evaluate.run(a.repo, eval_n=a.eval_n)
        write_index()
    elif a.cmd == "check":
        from .check import check, fetch_diff
        diff = Path(a.pr).read_text(encoding="utf-8") if Path(a.pr).is_file() else fetch_diff(parse_repo(a.repo), a.pr)
        res = check(parse_repo(a.repo), diff)
        for f in res["findings"]:
            print(f"[{f['rule_id']}] {f['file']}:{f['line']}  {f['issue']}")
            print(f"    fix: {f['fix']}\n    evidence: {f['evidence'][0]['url']}")
        print(f"{len(res['findings'])} findings; {res['rejected']} dropped for citing no real rule")
    elif a.cmd == "serve":
        from .serve import serve as run_server
        run_server(a.port)


if __name__ == "__main__":
    main()
