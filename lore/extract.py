"""F4: map step. Batches of training comments -> candidate rules {rule, why, comment_ids[]}."""
import json
from concurrent.futures import ThreadPoolExecutor

from . import llm
from .common import load, out_dir, workers as default_workers, progress, save

BATCH = 50
MAX_BODY = 700

SYSTEM = """You read pull-request review comments written by a project's maintainers and extract the \
project's house rules: conventions the maintainers enforce on contributors.

A good rule is specific to this project and actionable before opening a PR: which helper, fixture or API \
to use, where documentation or changelog entries go, how tests must be written, naming and structure \
conventions. Write each rule in your own words as an instruction; never copy a question. Skip one-off \
bug reports, questions, praise, and generic advice that applies to any codebase.

Only output a rule if at least one comment in the batch clearly expresses it. Cite every comment id \
that expresses the rule, and only those ids. Never invent ids.

Reply with JSON only:
{"rules": [{"rule": "<imperative, one sentence>", "why": "<the maintainers' reason, one sentence>", \
"comment_ids": [<int>, ...]}]}
If no comment expresses a house rule, reply {"rules": []}."""


def fmt(c):
    body = c["body"] if len(c["body"]) <= MAX_BODY else c["body"][:MAX_BODY] + " ..."
    where = f" {c['path']}" if c.get("path") else ""
    return f"[{c['id']}] PR #{c['pr']}{where}:\n{body}"


def run(repo, workers=None):
    workers = workers or default_workers()
    train = [c for c in load(repo, "comments.json") if c["split"] == "train"]
    # Group by file area so related comments land in the same batch and can co-cite one rule.
    train.sort(key=lambda c: (c.get("path") or "~", c["created_at"]))
    batches = [train[i:i + BATCH] for i in range(0, len(train), BATCH)]

    # Finished batches are cached per model, so a crashed or interrupted run resumes instead of starting over.
    cache_path = out_dir(repo) / "extract_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    def key(batch):
        return f"{llm.model()}:{batch[0]['id']}:{batch[-1]['id']}:{len(batch)}"

    def one(batch):
        if key(batch) in cache:
            return cache[key(batch)]
        out = llm.chat_json(SYSTEM, "\n\n".join(fmt(c) for c in batch))
        rules = (out or {}).get("rules") if isinstance(out, dict) else None
        return rules if isinstance(rules, list) else None

    candidates, failed = [], 0
    progress(repo, "extract", f"{len(train)} training comments in {len(batches)} batches", 0, len(batches))
    with ThreadPoolExecutor(workers) as pool:
        for n, (batch, rules) in enumerate(zip(batches, pool.map(one, batches)), 1):
            if rules is None:
                failed += 1
            else:
                cache[key(batch)] = rules
                cache_path.write_text(json.dumps(cache), encoding="utf-8")
                candidates += [r for r in rules if isinstance(r, dict) and r.get("rule")]
            progress(repo, "extract", f"{len(candidates)} candidate rules", n, len(batches))
    save(repo, "candidates.json", {"model": llm.model(), "provider": llm.provider(), "batches": len(batches),
                                   "failed_batches": failed, "candidates": candidates})
    return candidates
