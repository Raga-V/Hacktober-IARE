"""F7: emit <repo>-review-lore/SKILL.md + references/rules.md and validate with skills-ref."""
import json
import re
import shutil
import zipfile

from skills_ref import validate

from .common import load, out_dir, progress, save


def skill_name(repo):
    owner, name = repo.lower().split("/")
    if len(name) <= 4:  # "core", "cli", "app" say nothing on their own
        name = f"{owner}-{name}"
    base = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    return f"{base[:52].strip('-')}-review-lore"


def one_line(text):
    return re.sub(r"\s+", " ", text or "").strip()


def skill_md(name, data, meta):
    repo = data["repo"]
    desc = (f"House rules the maintainers of {repo} enforce in pull-request review, compiled by Lore from "
            f"{data['mined']} maintainer review comments. Use when writing code for, reviewing code in, or "
            f"opening a pull request against {repo}.")
    front = "\n".join([
        "---",
        f"name: {name}",
        f"description: {json.dumps(desc)}",
        "metadata:",
        f"  source-repo: {json.dumps(repo)}",
        "  generated-by: lore",
        f"  mined-comments: \"{data['mined']}\"",
        f"  model: {json.dumps(data['model'])}",
        "---",
    ])
    rules = "\n".join(
        f"{n}. **{one_line(r['rule'])}** {one_line(r['why'])} "
        f"_({r['support']} comments, {r['prs']} PRs, since {r['since']}; see `{r['id']}`)_"
        for n, r in enumerate(data["rules"], 1))
    return f"""{front}

# {repo} review lore

These are the rules {repo} maintainers repeatedly enforce in code review. Each one was stated by maintainers in at least {data['threshold']['min_comments']} review comments across at least {data['threshold']['min_prs']} pull requests between {meta['first']} and {meta['last']}. The comments behind every rule are linked in [references/rules.md](references/rules.md).

## Rules

{rules}

## How to use these rules

- Before writing code for {repo}, read the rules above and apply the ones that touch the files you are changing.
- Before opening a pull request, check your diff against each rule and fix any violation.
- When a rule is unclear, open its entry in [references/rules.md](references/rules.md) and read the linked review comments.
- If a rule conflicts with the repository's own CONTRIBUTING guide or with explicit instructions, those take precedence.

## Reviewing a pull request with these rules

Use this skill alongside a general code-review skill: that skill covers correctness, security and design; this one
covers what {repo} maintainers specifically ask for. For each rule above, check the lines the diff adds or changes.

- Report only clear violations of a listed rule. Do not report style or taste issues no rule covers.
- Start each finding with the rule id in brackets, then `file:line`, the problem in one sentence, and a concrete fix
  (a suggestion block when the fix is a small edit).
- Link one evidence comment from [references/rules.md](references/rules.md) so the author can see the precedent.
- If no rule is broken, say so in one line. Do not pad the review.

Example: `[{data['rules'][0]['id'] if data['rules'] else 'rule-id'}] path/to/file.py:42 - <problem>. Fix: <change>. Precedent: <comment link>`
"""


def rules_md(data):
    parts = [f"# Evidence for {data['repo']} review rules\n",
             f"Every rule below cites real maintainer review comments. {data['rejected_rules']} candidate rules "
             "were rejected because they cited comments that do not exist.\n"]
    for r in data["rules"]:
        parts.append(f"## `{r['id']}`: {one_line(r['rule'])}\n\n{one_line(r['why'])}\n\n"
                     f"Support: {r['support']} comments across {r['prs']} PRs, since {r['since']}.\n")
        for e in r["evidence"]:
            quote = one_line(e["quote"])
            parts.append(f"- [PR #{e['pr']}, @{e['author']}, {e['created_at']}]({e['url']}): {quote}")
        parts.append("")
    return "\n".join(parts)


def run(repo):
    data = load(repo, "rules.json")
    meta = load(repo, "meta.json")
    name = skill_name(data["repo"])
    root = out_dir(repo) / "skill"
    shutil.rmtree(root, ignore_errors=True)
    skill = root / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(skill_md(name, data, meta), encoding="utf-8")
    (skill / "references" / "rules.md").write_text(rules_md(data), encoding="utf-8")

    errors = validate(skill)
    with zipfile.ZipFile(out_dir(repo) / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in skill.rglob("*"):
            z.write(f, f.relative_to(root))
    save(repo, "skill.json", {"name": name, "path": f"skill/{name}", "zip": f"{name}.zip",
                              "valid": not errors, "errors": errors})
    progress(repo, "emit", f"{name}: " + ("passes skills-ref validate" if not errors else f"INVALID {errors}"))
    return errors
