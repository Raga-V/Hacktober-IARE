---
name: pandas-review-lore
description: "House rules the maintainers of pandas-dev/pandas enforce in pull-request review, compiled by Lore from 2203 maintainer review comments. Use when writing code for, reviewing code in, or opening a pull request against pandas-dev/pandas."
metadata:
  source-repo: "pandas-dev/pandas"
  generated-by: lore
  mined-comments: "2203"
  model: "qwen/qwen3-235b-a22b-instruct-2507-maas"
---

# pandas-dev/pandas review lore

These are the rules pandas-dev/pandas maintainers repeatedly enforce in code review. Each one was stated by maintainers in at least 3 review comments across at least 2 pull requests between 2026-01-24 and 2026-10-09. The comments behind every rule are linked in [references/rules.md](references/rules.md).

## Rules

1. **Place whatsnew entries in the correct section, avoid internal changes, and focus on concise, user-facing impact.** This ensures the changelog remains useful and accurate for end users and avoids clutter from non-essential changes. _(10 comments, 9 PRs, since 2026; see `whatsnew-categorization-and-content`)_
2. **Place test functions, files, and imports in the correct locations and organize them for clarity and reuse.** Proper organization improves discoverability, maintainability, and consistency across the test suite. _(10 comments, 8 PRs, since 2026; see `test-organization-and-structure`)_
3. **Parametrize test cases instead of writing repetitive logic for different inputs or engines.** This reduces code duplication and improves clarity and maintainability of test suites. _(8 comments, 8 PRs, since 2026; see `parametrize-over-repetition`)_
4. **Link every new test to its corresponding GitHub issue using a comment with the issue reference format #GHXXXXX.** This ensures traceability between tests and the issues they address, improving maintainability and context for future contributors. _(7 comments, 6 PRs, since 2026; see `github-issue-linking-in-tests`)_
5. **Use `tm.assert_frame_equal`, `tm.assert_series_equal`, or similar functions to check the full state of objects, including index, columns, and dtypes.** This ensures comprehensive validation and prevents subtle regressions due to incomplete comparisons. _(5 comments, 5 PRs, since 2026; see `prefer-full-object-equality-assertions`)_
6. **Ensure test coverage includes edge cases such as large integers, small sample sizes, and non-standard dtypes.** Comprehensive coverage helps catch regressions in corner cases that are often sources of bugs. _(5 comments, 5 PRs, since 2026; see `test-edge-cases-and-coverage`)_
7. **Use clear variable names and comments that explain the purpose, not just repeat the code.** Clear naming and meaningful comments improve readability and maintainability of tests and code. _(5 comments, 5 PRs, since 2026; see `use-descriptive-variables-and-comments`)_
8. **Use the simplest possible constructs in tests, avoiding unnecessary DataFrame constructions, deep copies, or indirections.** Simpler tests are easier to understand, debug, and maintain while still validating the intended behavior. _(4 comments, 3 PRs, since 2026; see `avoid-unnecessary-complexity-in-tests`)_
9. **Check the dtype of MultiIndex codes and ensure expected and actual dtypes match without relying on `check_dtype=False`.** Accurate dtype checking prevents silent mismatches and ensures correct behavior across platforms. _(3 comments, 3 PRs, since 2026; see `check-dtype-and-index-codes-correctly`)_

## How to use these rules

- Before writing code for pandas-dev/pandas, read the rules above and apply the ones that touch the files you are changing.
- Before opening a pull request, check your diff against each rule and fix any violation.
- When a rule is unclear, open its entry in [references/rules.md](references/rules.md) and read the linked review comments.
- If a rule conflicts with the repository's own CONTRIBUTING guide or with explicit instructions, those take precedence.

## Reviewing a pull request with these rules

Use this skill alongside a general code-review skill: that skill covers correctness, security and design; this one
covers what pandas-dev/pandas maintainers specifically ask for. For each rule above, check the lines the diff adds or changes.

- Report only clear violations of a listed rule. Do not report style or taste issues no rule covers.
- Start each finding with the rule id in brackets, then `file:line`, the problem in one sentence, and a concrete fix
  (a suggestion block when the fix is a small edit).
- Link one evidence comment from [references/rules.md](references/rules.md) so the author can see the precedent.
- If no rule is broken, say so in one line. Do not pad the review.

Example: `[whatsnew-categorization-and-content] path/to/file.py:42 - <problem>. Fix: <change>. Precedent: <comment link>`
