"""PR check: review a diff against a repo's learned rules. Findings must cite a real rule id."""
import re

from . import llm
from .common import load
from .mine import API, get, session

MAX_DIFF = 60_000

SYSTEM = """You review a pull-request diff against a project's house rules, learned from its maintainers' \
past review comments. Flag only clear violations of these specific rules in lines the diff adds or changes. \
Do not report general style, correctness or taste issues that no rule covers. Every finding needs a concrete fix.
Severity: "must-fix" when maintainers would block the merge over it, otherwise "suggestion".

Reply with JSON only:
{"findings": [{"rule_id": "<id from the list>", "severity": "must-fix" or "suggestion", "file": "<path>", "line": <line in the new file or null>, \
"issue": "<what in the diff breaks the rule, one sentence>", "fix": "<the concrete change, one sentence>"}]}
If nothing in the diff breaks a rule, reply {"findings": []}."""


def fetch_diff(repo, ref):
    """`ref` is a PR number or a github.com PR URL; returns the unified diff."""
    m = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", ref)
    repo, number = (m.group(1), m.group(2)) if m else (repo, ref.strip().lstrip("#"))
    s = session()
    s.headers["Accept"] = "application/vnd.github.diff"
    r = get(s, f"{API}/repos/{repo}/pulls/{number}")
    r.raise_for_status()
    return r.text


def check(repo, diff):
    data = load(repo, "rules.json")
    rules = {r["id"]: r for r in data["rules"]}
    listing = "\n".join(f"- {r['id']}: {r['rule']}" for r in data["rules"])
    out = llm.chat_json(SYSTEM, f"Rules:\n{listing}\n\nDiff:\n{diff[:MAX_DIFF]}")
    raw = (out or {}).get("findings") if isinstance(out, dict) else None
    findings, rejected = [], 0
    for f in raw if isinstance(raw, list) else []:
        r = rules.get(str(f.get("rule_id"))) if isinstance(f, dict) else None
        if r is None:
            rejected += 1  # same discipline as the citation check: no rule, no finding
            continue
        sev = "must-fix" if f.get("severity") == "must-fix" else "suggestion"
        findings.append({**{k: f.get(k) for k in ("rule_id", "file", "line", "issue", "fix")}, "severity": sev,
                         "rule": r["rule"], "evidence": r["evidence"][:2]})
    findings.sort(key=lambda f: f["severity"] != "must-fix")
    return {"findings": findings, "rejected": rejected, "truncated": len(diff) > MAX_DIFF,
            "model": llm.model(), "provider": llm.provider()}
