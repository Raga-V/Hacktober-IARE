"""F8: holdout evaluation. Which share of unseen maintainer comments does each skill's rules anticipate?"""
from concurrent.futures import ThreadPoolExecutor

from . import llm
from .common import load, workers as default_workers, progress, save

BATCH = 20
MAX_BODY = 600

# Baseline: a well-written, project-agnostic code-review skill of the kind people drop into agents today.
GENERIC_RULES = [
    "Add or update tests that cover every behaviour change.",
    "Update documentation and docstrings when behaviour or public APIs change.",
    "Add a changelog or release-notes entry for user-facing changes.",
    "Follow the existing code style and formatting; run the project's linter and formatter.",
    "Use clear, descriptive names for variables, functions and classes.",
    "Keep functions small and focused; split large functions.",
    "Do not duplicate code; reuse existing helpers and utilities.",
    "Handle errors explicitly; do not swallow exceptions silently.",
    "Remove debug prints, commented-out code and unused imports or variables.",
    "Add type annotations to new and changed code.",
    "Replace magic numbers and strings with named constants.",
    "Do not break public APIs without a deprecation path.",
    "Keep pull requests small and focused on a single change.",
    "Write clear commit messages and PR descriptions explaining why.",
    "Consider edge cases such as empty input, None and boundary values.",
    "Avoid unnecessary performance costs such as repeated work inside loops.",
    "Never commit secrets, credentials or hard-coded environment-specific paths.",
    "Justify any new dependency and prefer the standard library.",
    "Use the project's logging facility instead of print statements, at appropriate levels.",
    "Add comments explaining non-obvious logic, and keep existing comments accurate.",
]

SYSTEM = """You judge whether a set of house rules anticipates the feedback in code-review comments.

For each comment, return the label of the rule that, had the contributor followed it, would have made \
the comment unnecessary. A rule covers a comment only if the comment raises the specific point the rule \
states. A broad rule that merely touches the same topic does not count. Comments that raise no \
rule-like point (questions, approvals, one-off bugs) are covered by no rule.

Reply with JSON only: {"results": [{"id": <comment id>, "rule": "<rule label>" or null}]}"""


def sample(holdout, n):
    """Deterministic, evenly spaced sample across the holdout window."""
    if len(holdout) <= n:
        return holdout
    step = len(holdout) / n
    return [holdout[int(k * step)] for k in range(n)]


def judge(rules, comments, workers):
    """Returns {comment_id: rule index or None}."""
    labels = {f"R{i + 1}": i for i in range(len(rules))}
    listing = "\n".join(f"R{i + 1}: {r}" for i, r in enumerate(rules))
    batches = [comments[i:i + BATCH] for i in range(0, len(comments), BATCH)]

    def one(batch):
        body = "\n\n".join(f"[{c['id']}] {c['body'][:MAX_BODY]}" for c in batch)
        out = llm.chat_json(SYSTEM, f"Rules:\n{listing}\n\nComments:\n{body}")
        res = (out or {}).get("results") if isinstance(out, dict) else None
        got = {}
        for r in res if isinstance(res, list) else []:
            if isinstance(r, dict) and str(r.get("id")).isdigit():
                got[int(r["id"])] = labels.get(str(r.get("rule") or "").strip())
        return {c["id"]: got.get(c["id"]) for c in batch}

    verdict = {}
    with ThreadPoolExecutor(workers) as pool:
        for part in pool.map(one, batches):
            verdict.update(part)
    return verdict


def run(repo, eval_n=150, workers=None):
    workers = workers or default_workers()
    comments = load(repo, "comments.json")
    meta = load(repo, "meta.json")
    data = load(repo, "rules.json")
    holdout = sample([c for c in comments if c["split"] == "holdout"], eval_n)
    lore_rules = [f"{r['rule']} ({r['why']})" if r["why"] else r["rule"] for r in data["rules"]]

    progress(repo, "eval", f"judging {len(holdout)} holdout comments against {len(lore_rules)} Lore rules")
    lore = judge(lore_rules, holdout, workers) if lore_rules else {c["id"]: None for c in holdout}
    progress(repo, "eval", f"judging {len(holdout)} holdout comments against {len(GENERIC_RULES)} generic rules")
    generic = judge(GENERIC_RULES, holdout, workers)

    n = len(holdout) or 1
    lore_hit = [c for c in holdout if lore[c["id"]] is not None]
    gen_hit = [c for c in holdout if generic[c["id"]] is not None]
    per_rule = {r["id"]: 0 for r in data["rules"]}
    for c in lore_hit:
        per_rule[data["rules"][lore[c["id"]]]["id"]] += 1
    only_lore = [c for c in lore_hit if generic[c["id"]] is None]

    out = {
        "holdout_comments": len(holdout),
        "holdout_total": sum(c["split"] == "holdout" for c in comments),
        "holdout_since": meta["holdout_since"],
        "split_method": meta["split_method"],
        "lore_rules": len(lore_rules),
        "generic_rules": len(GENERIC_RULES),
        "lore_covered": len(lore_hit),
        "generic_covered": len(gen_hit),
        "both_covered": sum(generic[c["id"]] is not None for c in lore_hit),
        "lore_pct": round(100 * len(lore_hit) / n, 1),
        "generic_pct": round(100 * len(gen_hit) / n, 1),
        # Lore is meant to sit beside a general review skill, so the headline is what it adds on top.
        "lore_only": len(only_lore),
        "combined_pct": round(100 * (len(gen_hit) + len(only_lore)) / n, 1),
        "per_rule": per_rule,
        "examples": [{"comment_id": c["id"], "url": c["url"], "quote": c["body"][:280],
                      "rule": data["rules"][lore[c["id"]]]["id"]} for c in only_lore[:8]],
        "model": llm.model(),
        "provider": llm.provider(),
        "method": "Same open-weight model and judging prompt for both skills; each holdout comment "
                  "(never seen by the extractor) counts as covered if the judge maps it to a specific rule.",
    }
    save(repo, "eval.json", out)
    progress(repo, "eval", f"Lore {out['lore_pct']}% vs generic {out['generic_pct']}% "
             f"of {len(holdout)} unseen maintainer comments")
    return out
