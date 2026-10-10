"""Which learned rules are already written down? Checks CONTRIBUTING and agent-instruction files."""
import base64

from . import llm
from .common import load, progress, save
from .mine import API, get, session

DOC_FILES = ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md", "AGENTS.md", "CLAUDE.md",
             ".github/copilot-instructions.md", ".cursorrules"]
MAX_DOC = 40_000

SYSTEM = """You compare a project's house rules, learned from maintainers' review comments, with the project's \
written contributor and agent documentation.
For each rule, decide whether the documentation already states it (explicitly or as a clear, specific instruction). \
A loosely related sentence does not count.

Reply with JSON only: {"documented": {"<rule id>": "<file name that states it>" or null}}"""


def fetch_docs(repo):
    s, docs, seen = session(), {}, set()
    for f in DOC_FILES:
        r = get(s, f"{API}/repos/{repo}/contents/{f}")
        if r.status_code != 200:
            continue
        text = base64.b64decode(r.json().get("content", "")).decode("utf-8", "replace")
        if text.strip() and text not in seen:  # CLAUDE.md is often a copy of AGENTS.md
            seen.add(text)
            docs[f] = text
    return docs


def run(repo):
    data = load(repo, "rules.json")
    docs = fetch_docs(data["repo"])
    data["docs_checked"] = list(docs)
    found = {}
    if docs and data["rules"]:
        body = "\n\n".join(f"===== {name} =====\n{text}" for name, text in docs.items())[:MAX_DOC]
        listing = "\n".join(f"- {r['id']}: {r['rule']}" for r in data["rules"])
        out = llm.chat_json(SYSTEM, f"Rules:\n{listing}\n\nDocumentation:\n{body}")
        found = (out or {}).get("documented") or {} if isinstance(out, dict) else {}
    for r in data["rules"]:
        where = found.get(r["id"]) if isinstance(found, dict) else None
        r["documented_in"] = where if where in docs else None  # only trust files we actually sent
    data["unwritten"] = sum(r["documented_in"] is None for r in data["rules"])
    save(repo, "rules.json", data)
    progress(repo, "docs", f"{data['unwritten']} of {len(data['rules'])} rules are not in "
             f"{', '.join(docs) or 'any contributor or agent doc'}")
    return data
