---
name: lore
description: Compile the rules a project's maintainers actually enforce in pull-request review into an Agent Skill, with every rule linked to the review comments behind it. Use when asked to learn, document or extract a GitHub repository's unwritten contribution rules, house style or review conventions, or to generate a review-lore skill for a repository.
license: Apache-2.0
compatibility: Requires Python 3.10+, network access to api.github.com and an OpenAI-compatible inference endpoint serving open-weight models (DigitalOcean Serverless Inference, Groq, Cerebras, OpenRouter or local Ollama), and a GitHub token (GITHUB_TOKEN or a logged-in gh CLI).
metadata:
  author: Raga-V
  version: "0.1.0"
---

# Lore

Lore reads a GitHub repository's pull-request review history with an open-weight model and writes a skill named `<repo>-review-lore` that lists the rules maintainers
repeatedly enforce. Every rule cites at least 3 real maintainer comments from at least 2 pull requests.

## Steps

1. Check that one model key is set: `DO_MODEL_KEY` (DigitalOcean Serverless Inference), `GROQ_API_KEY`,
   `CEREBRAS_API_KEY` or `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `VERTEX_PROJECT` (Google Cloud Vertex AI with a gcloud login),
   or `LORE_PROVIDER=ollama` for a local model. If none is set,
   ask the user for one.
2. Install dependencies once: `pip install -r scripts/requirements.txt`.
3. Run the full pipeline:

   ```
   python scripts/run_lore.py run owner/repo
   ```

   For a quick run (about 300 comments, no review bodies), add `--live`.
   To re-run without re-mining GitHub, add `--cached`.
4. Read the results in `out/<owner>__<repo>/`:
   - `skill/<repo>-review-lore/` is the generated skill. It has already been checked with `skills-ref validate`.
   - `rules.json` has every rule with its evidence and the count of rules rejected by the citation check.
   - `eval.json` has holdout coverage for the generated skill versus a generic code-review skill.
5. Report to the user: the number of rules, the rejected count, and the coverage numbers from `eval.json`
   (`lore_pct` vs `generic_pct`). Do not round the numbers in a way that changes the comparison.
6. If the user wants to contribute the skill to the repository, copy the generated skill folder to
   `.agents/skills/` in their checkout of that repository.
7. To review a pull request against the learned rules, run
   `python scripts/run_lore.py check owner/repo <PR number, PR URL or .diff file>`. Report each finding with its
   rule id, fix and precedent link.

## Pipeline stages

Each stage can be run on its own with `python scripts/run_lore.py <stage> owner/repo`:
`mine`, `extract`, `merge`, `emit`, `eval`. Run `python scripts/run_lore.py models` to see which
open-weight model will be used. Set `LORE_MODEL` to pin one; closed models are refused.

## Gotchas

- Mining uses the GitHub REST API. Without a token the rate limit is 60 requests per hour, which is not enough.
- Repositories with few maintainer review comments may produce zero rules. That is a correct result, not an error.
- The holdout set is the last 60 days of comments, or the newest 20% when that window is too busy or too quiet.
