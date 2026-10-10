---
name: home-assistant-core-review-lore
description: "House rules the maintainers of home-assistant/core enforce in pull-request review, compiled by Lore from 2237 maintainer review comments. Use when writing code for, reviewing code in, or opening a pull request against home-assistant/core."
metadata:
  source-repo: "home-assistant/core"
  generated-by: lore
  mined-comments: "2237"
  model: "qwen/qwen3-235b-a22b-instruct-2507-maas"
---

# home-assistant/core review lore

These are the rules home-assistant/core maintainers repeatedly enforce in code review. Each one was stated by maintainers in at least 3 review comments across at least 2 pull requests between 2026-03-19 and 2026-10-10. The comments behind every rule are linked in [references/rules.md](references/rules.md).

## Rules

1. **Do not create or interact with coordinators directly in tests; instead test integration behavior through entities.** This ensures tests reflect real-world usage and avoids bypassing integration setup. _(12 comments, 9 PRs, since 2026; see `avoid-creating-coordinators-in-tests`)_
2. **Ensure config flow tests end with CREATE_ENTRY or ABORT to verify flow completion and recovery from errors.** This ensures the config flow behaves correctly under all conditions and completes as expected. _(12 comments, 12 PRs, since 2026; see `config-flow-test-expectations`)_
3. **Split complex fixtures into smaller, composable ones and use shared fixtures like mock_config_entry instead of duplicating setup.** Reusable fixtures reduce duplication and improve test maintainability. _(12 comments, 9 PRs, since 2026; see `fixture-management`)_
4. **Split unrelated changes, major features, or flows like reauth into separate pull requests.** Focused PRs are easier to review, test, and merge. _(12 comments, 7 PRs, since 2026; see `pr-scope`)_
5. **Do not include reauthentication or reconfiguration functionality in the initial PR for a new integration.** This allows incremental development and review of complex flows. _(9 comments, 8 PRs, since 2026; see `avoid-reauth-reconfig-initial-pr`)_
6. **Do not interact with the coordinator directly in tests; use time freezing or let the coordinator tick naturally.** This ensures proper simulation of real-world behavior and avoids bypassing integration logic. _(7 comments, 7 PRs, since 2026; see `avoid-direct-coordinator-interaction-in`)_
7. **Use snapshot testing with snapshot_platform for complex data structures instead of writing explicit assertions.** Reduces test maintenance overhead and ensures comprehensive structure validation. _(6 comments, 6 PRs, since 2026; see `snapshot-testing-complex-data`)_
8. **Avoid inline patching; use common patching patterns or fixtures instead.** This improves test readability and reusability of test setup logic. _(5 comments, 5 PRs, since 2026; see `avoid-inline-patching`)_
9. **Avoid using if statements or conditions in tests to maintain clarity and prevent conditional logic from obscuring test intent.** This ensures tests are deterministic and easy to understand. _(5 comments, 5 PRs, since 2026; see `avoid-using-if-statements-in-tests`)_
10. **Bump dependencies in a separate PR from functional changes.** This isolates changes and makes reviews more focused. _(5 comments, 5 PRs, since 2026; see `avoid-bumping-dependencies-with-function`)_
11. **Implement consistent patterns by inlining simple functions as lambdas in entity descriptions.** It reduces unnecessary function definitions and maintains consistency across sensors with minimal business logic. _(5 comments, 2 PRs, since 2026; see `implement-consistent-patterns-by-inlinin`)_
12. **Mark binary sensors and sensors that expose diagnostic information with entity category diagnostic.** This ensures diagnostic entities are properly grouped and hidden by default in the UI. _(5 comments, 2 PRs, since 2026; see `use-entity-category-diagnostic`)_
13. **Use common translation keys from homeassistant/strings.json for standard statuses like paused or charging.** This ensures consistency in user-facing status messages across integrations. _(5 comments, 3 PRs, since 2026; see `use-common-translation-keys`)_
14. **Avoid patching integration internals; instead, patch the underlying library or client.** This ensures tests validate integration behavior without relying on internal implementation details. _(4 comments, 4 PRs, since 2026; see `avoid-patching-integration-internals`)_
15. **Do not access or modify runtime_data in tests.** This ensures tests reflect real integration behavior through proper setup and state checks. _(4 comments, 3 PRs, since 2026; see `avoid-accessing-runtime-data-in-tests`)_
16. **Do not calculate entity states in the integration; this logic should reside in the library.** This separates concerns and improves testability and reuse. _(4 comments, 2 PRs, since 2026; see `avoid-calculating-entity-states-in-integ`)_
17. **Only include code in try blocks that can potentially raise exceptions.** This prevents catching exceptions from code that cannot fail, improving clarity. _(4 comments, 4 PRs, since 2026; see `avoid-putting-logic-in-try-blocks`)_
18. **Parametrize tests instead of writing separate test functions for similar cases.** It reduces code duplication and makes test coverage clearer. _(4 comments, 4 PRs, since 2026; see `parametrize-tests-instead-of-writing-sep`)_
19. **Assert the unique_id in config flow tests when applicable.** This verifies that entities are correctly identified and avoids duplication issues. _(3 comments, 3 PRs, since 2026; see `assert-unique-id-in-config-flow`)_
20. **Avoid using parametrize when only a single test case is used.** This avoids unnecessary complexity in test definitions. _(3 comments, 2 PRs, since 2026; see `avoid-using-parametrize-single-case`)_
21. **Freeze and advance time to trigger coordinator refreshes instead of relying on integration-specific runtime data like the coordinator directly.** This simulates real-world timing and avoids bypassing normal update mechanisms. _(3 comments, 3 PRs, since 2026; see `avoid-manual-coordinator-refresh`)_
22. **Merge related test cases into a single test when they share setup and logic.** Combining similar tests reduces duplication and improves maintainability. _(3 comments, 3 PRs, since 2026; see `merge-related-test-cases-into-a-single-t`)_
23. **Move data parsing logic from models or entities into the underlying library when possible.** This promotes code reuse and separates concerns. _(3 comments, 2 PRs, since 2026; see `avoid-unnecessary-data-parsing-in-models`)_
24. **Set _attr_name = None when the entity is the primary feature of the device to avoid redundant naming.** This prevents duplicate or confusing entity names in the UI. _(3 comments, 2 PRs, since 2026; see `entity-name-handling`)_
25. **Store JSON-based test data in fixture files within the fixtures folder using get_fixture_path or load_json_fixture.** Centralized test data improves readability and reuse. _(3 comments, 3 PRs, since 2026; see `test-data-storage`)_
26. **Use consistent and meaningful naming for functions, variables, and parameters, such as avoiding 'async_' prefix for non-async functions and using 'info' instead of 'data'.** This improves code readability and maintainability. _(3 comments, 3 PRs, since 2026; see `use-consistent-naming`)_
27. **Use extended config entry types and type hints in coordinators for better type safety.** This improves code clarity and enables better IDE support and error detection. _(3 comments, 3 PRs, since 2026; see `use-extended-config-entry-types`)_
28. **Use freezer.tick(x) or the freezer to advance and control time in tests instead of arbitrary delays.** This provides precise and reliable time manipulation in asynchronous tests. _(3 comments, 3 PRs, since 2026; see `use-freezer-to-advance-time-in-tests`)_
29. **Use TYPE_CHECKING from typing to avoid runtime import overhead.** Improves performance by preventing unnecessary imports during execution. _(3 comments, 2 PRs, since 2026; see `typing-type-checking`)_
30. **Wait for background tasks when testing coordinator refreshes using hass.async_block_till_done with wait_background_tasks=True.** Ensures test reliability by confirming all asynchronous operations are complete. _(3 comments, 3 PRs, since 2026; see `wait-background-tasks-testing`)_

## How to use these rules

- Before writing code for home-assistant/core, read the rules above and apply the ones that touch the files you are changing.
- Before opening a pull request, check your diff against each rule and fix any violation.
- When a rule is unclear, open its entry in [references/rules.md](references/rules.md) and read the linked review comments.
- If a rule conflicts with the repository's own CONTRIBUTING guide or with explicit instructions, those take precedence.

## Reviewing a pull request with these rules

Use this skill alongside a general code-review skill: that skill covers correctness, security and design; this one
covers what home-assistant/core maintainers specifically ask for. For each rule above, check the lines the diff adds or changes.

- Report only clear violations of a listed rule. Do not report style or taste issues no rule covers.
- Start each finding with the rule id in brackets, then `file:line`, the problem in one sentence, and a concrete fix
  (a suggestion block when the fix is a small edit).
- Link one evidence comment from [references/rules.md](references/rules.md) so the author can see the precedent.
- If no rule is broken, say so in one line. Do not pad the review.

Example: `[avoid-creating-coordinators-in-tests] path/to/file.py:42 - <problem>. Fix: <change>. Precedent: <comment link>`
