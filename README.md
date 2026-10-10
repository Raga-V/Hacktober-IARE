# Lore

**Every maintainer has a review comment they could type in their sleep. Lore makes it the last time they type it.**

Lore reads a repository's pull-request review history with an open-weight model and compiles the rules maintainers actually enforce into an [Agent Skill](https://agentskills.io).
Every rule links to the real review comments behind it.

Built at Hacktoberfest Hack Day Hyderabad × IARE, 10 Oct 2026, for the DigitalOcean Best Open-Source AI Project track.

## The problem

An open-source project's most important rules are scattered across years of pull-request review comments, and
nobody reads those. Each new contributor learns the rules by getting rejected, and maintainers lose time repeating
them. AI coding agents make this worse: they produce more contributions, and none of those contributions follow the
project's unwritten rules.

## What Lore does

1. **Mine** maintainer review comments (inline comments and review bodies) through the GitHub API. Lore keeps only
   comments by `OWNER`, `MEMBER` or `COLLABORATOR` accounts, drops bots, comments under 20 characters, and
   maintainers replying on their own PRs.
2. **Split by date.** The last 60 days are held out, and the extractor never sees them. If that window is too
   quiet (under 20 comments) or too busy (over 30% of the comments), Lore holds out the newest 20% instead.
3. **Map.** Batches of 50 comments go to the model, which returns candidate rules `{rule, why, comment_ids[]}`.
4. **Citation check.** Any rule that cites a comment ID not in the mined training set is rejected, and the
   rejections are counted.
5. **Reduce.** Duplicate rules are merged, and each rule is grounded: the model rechecks every cited comment and
   drops citations that don't state the rule. A rule is kept only with **3+ comments across 2+ PRs**.
6. **Emit** `<repo>-review-lore/SKILL.md` plus `references/rules.md` with evidence links, then validate it with
   `skills-ref`.
7. **Evaluate.** For each held-out comment, the same model and prompt decide whether any rule anticipates it,
   once for Lore's rules and once for a generic 20-rule code-review skill.
8. **Unwritten or documented?** Lore reads the repo's CONTRIBUTING.md, AGENTS.md, CLAUDE.md and Copilot
   instructions and marks which learned rules are not written down anywhere. On pandas, 9 of 9 rules are missing
   from its AGENTS.md; on home-assistant, 25 of 30 are missing from all three of its docs (and the 5 that are
   documented were rediscovered from review comments alone).
9. **Check a PR.** `python -m lore check owner/repo <PR number | URL | file.diff>` reviews a diff against the
   learned rules. Every finding is ranked must-fix or suggestion and names a rule id, a concrete fix and the
   precedent comment; findings citing a rule
   that doesn't exist are dropped, the same discipline as the citation check. The generated `SKILL.md` carries the
   same review instructions, so any agent can run it.

It's a harness, not a prompt. Two model steps (extract, judge) are wrapped in deterministic code that checks the
model's output: the citation verifier, the support threshold, the holdout split and the baseline comparison.

## Results

Model: `qwen/qwen3-235b-a22b-instruct-2507-maas` (open-weight, Apache-2.0) on Google Cloud Vertex AI.
Holdout: 150 maintainer comments per repo that the extractor never saw.

| Repo | Comments mined | Candidate rules | Rejected by citation check | Citations dropped by grounding | Rules kept | Generic skill | Lore alone | Generic + Lore |
|---|---|---|---|---|---|---|---|---|
| [pandas-dev/pandas](out/pandas-dev__pandas/skill/) | 2,203 | 106 | 0 | 51 | 9 | 57.3% | 37.3% | **64.7%** (+7.4) |
| [home-assistant/core](out/home-assistant__core/skill/) | 2,237 | 303 | 0 | 56 | 30 | 48.7% | 21.3% | **55.3%** (+6.6) |

**What the numbers say.** A generic 20-rule review skill already anticipates about half of what maintainers say,
because much review feedback is generic ("add a test", "handle this edge case"). Lore's handful of rules alone covers
less. Added to the generic skill, though, Lore raises coverage by about 7 points on both repos: these are the comments
only project knowledge can anticipate, like pandas' whatsnew-entry and `tm.assert_frame_equal` conventions. That
matches how review skills are built: Warp's `review-pr` expects a companion "with the repository's own conventions",
and Matt Pocock's `code-review` looks for the repo's standards documents. Lore generates that companion from evidence.

How the numbers are measured: the extractor never sees the held-out comments. Lore and the generic skill are
judged by the same open-weight model with the same prompt. A comment counts as covered only when the judge maps
it to a specific rule. "Generic + Lore" counts a comment as covered if either skill covers it. See `eval.json`.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # add one model key (see "Model providers"); GitHub falls back to `gh auth token`

python -m lore models                      # list the provider's models; shows the open-weight one Lore will use
python -m lore run home-assistant/core     # full pipeline -> out/home-assistant__core/
python -m lore run owner/repo --live       # quick run on ~300 recent comments
python -m lore check pandas-dev/pandas 70945   # review a PR against the learned rules
python -m lore serve                       # page at http://127.0.0.1:8000/web/ with live mode and PR check
```

Stages can also run one at a time: `mine`, `extract`, `merge`, `emit`, `eval`.

Output in `out/<owner>__<repo>/`:

| File | Contents |
|---|---|
| `comments.json` | maintainer comments with `split: train/holdout` |
| `meta.json` | counts, date range and split method |
| `candidates.json` | raw map-step output |
| `rules.json` | final rules with evidence, rejected count, grounding drops |
| `eval.json` | holdout coverage for Lore and for the generic skill |
| `skill/<name>/` | the generated Agent Skill, plus `<name>.zip` |

## Model providers

Lore talks to any OpenAI-compatible endpoint and only ever uses **open-weight models**. It picks the best one
listed by `GET /v1/models` (GLM first, then Qwen, DeepSeek, gpt-oss and Llama), or the one you pin with
`LORE_MODEL`, preferring the largest size in a family. It refuses closed models (GPT, o-series, Claude,
Gemini, Grok).

| Provider | Key | Endpoint |
|---|---|---|
| DigitalOcean Serverless Inference (default) | `DO_MODEL_KEY` | `https://inference.do-ai.run/v1/` |
| Groq | `GROQ_API_KEY` | `https://api.groq.com/openai/v1` |
| Cerebras | `CEREBRAS_API_KEY` | `https://api.cerebras.ai/v1` |
| OpenRouter (`:free` models only) | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` |
| Google AI Studio (open-weight Gemma only) | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| Google Cloud Vertex AI (Model Garden) | `VERTEX_PROJECT` + gcloud login | `https://aiplatform.googleapis.com/v1/projects/…/endpoints/openapi` |
| Ollama (local) | `LORE_PROVIDER=ollama` | `http://localhost:11434/v1` |

The first key found wins, in table order; `LORE_PROVIDER` forces one. The provider and model that produced each
result are recorded in `rules.json` and `eval.json` and shown on the page.
Results above: Google Cloud Vertex AI (`VERTEX_PROJECT`, authenticated with `gcloud auth login`), Qwen3 235B.

- JSON mode, `temperature=0`, one retry on invalid JSON, then the batch is skipped. The system prompt is
  byte-identical across batches so prompt caching can reuse it.
- Free tiers rate-limit parallel calls: the client retries 429s with backoff, and `LORE_WORKERS=2` slows Lore down.
- **Hosting**: the page is a static site (`web/` + `out/`). Deploy the repo as a static site (for example
  DigitalOcean App Platform) and open `/web/`.

## Lore as a skill

`skills/lore/` packages Lore itself as an Agent Skill (`SKILL.md` + `scripts/run_lore.py`) so any compatible
agent can generate review-lore skills. Both it and every generated skill pass `agentskills validate`.

## Privacy

Lore reads only public review comments. Nothing is stored beyond the local JSON cache in `out/`.

## License

[Apache-2.0](LICENSE)
