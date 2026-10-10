# Evidence for home-assistant/core review rules

Every rule below cites real maintainer review comments. 0 candidate rules were rejected because they cited comments that do not exist.

## `avoid-creating-coordinators-in-tests`: Do not create or interact with coordinators directly in tests; instead test integration behavior through entities.

This ensures tests reflect real-world usage and avoids bypassing integration setup.

Support: 12 comments across 9 PRs, since 2026.

- [PR #171587, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/171587#discussion_r3847677880): we shouldn't directly create a camera entity, instead do this via the state machine
- [PR #178684, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/178684#discussion_r3862220528): we shouldn't touch the coordinator data, instead repatch the library to what you expect it returns and trigger a refresh by freezing and skipping time
- [PR #180238, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/180238#discussion_r3864471014): we shouldn't touch runtime_data/the coordinator directly, instead skip time using the freezer to trigger a refresh
- [PR #180581, @joostlek, 2026-08-30](https://github.com/home-assistant/core/pull/180581#discussion_r3889512871): Can we avoid touching the coordinator here?
- [PR #177918, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/177918#discussion_r3961277107): We should not create a coordinator ourselves. Instead test the behavior of the integration via the entities, so via `test_sensor.py`
- [PR #177918, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/177918#discussion_r3961281644): In the end I think we should try to not have a `test_coordinator.py`
- [PR #177918, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/177918#discussion_r3961283529): don't touch the coordinator in the tests
- [PR #181566, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/181566#discussion_r4005331920): We shouldn't create entities directly. Looking at the relevant tests, those wouldn't work because that's already guarded by HA, so we don't need to test those
- [PR #177108, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/177108#discussion_r4047752309): The tests should not create a Coordinator object directly. Instead we should have Home Assistant set up the integration and then see the behavior of the integration and the attached entities. In the end we should not have a test_coordinator.py anymore
- [PR #177108, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/177108#discussion_r4047774005): we should not create entities directly, instead have HA set up the integration and then assert that the created entities are what we expect with the right state and such
- [PR #182648, @erwindouna, 2026-09-19](https://github.com/home-assistant/core/pull/182648#discussion_r4052370961): We shouldn't trigger the coordinator directly, but let the time pass by the freezer factory. :)
- [PR #182956, @joostlek, 2026-09-24](https://github.com/home-assistant/core/pull/182956#discussion_r4094627461): we shouldn't create an entity directly but instead use the one created by the integration

## `config-flow-test-expectations`: Ensure config flow tests end with CREATE_ENTRY or ABORT to verify flow completion and recovery from errors.

This ensures the config flow behaves correctly under all conditions and completes as expected.

Support: 12 comments across 12 PRs, since 2026.

- [PR #168444, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/168444#discussion_r3844379311): all flows should end in CREATE_ENTRY or ABORT to test that they are able to recover
- [PR #179543, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/179543#discussion_r3847851857): all flows should end in CREATE_ENTRY or ABORT
- [PR #176785, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/176785#discussion_r3863961976): Let's make sure the test ends in CREATE_ENTRY or ABORT to test that the flow is able to recover
- [PR #167872, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/167872#discussion_r3864103137): make sure it ends in CREATE_ENTRY
- [PR #180394, @MartinHjelmare, 2026-08-28](https://github.com/home-assistant/core/pull/180394#discussion_r3879363754): Please continue the flow to a create entry or abort result.
- [PR #180856, @joostlek, 2026-08-30](https://github.com/home-assistant/core/pull/180856#discussion_r3890289273): All flows need to finish to test that it can recover
- [PR #180878, @joostlek, 2026-08-31](https://github.com/home-assistant/core/pull/180878#discussion_r3895273632): All flows should finish to show that they are able to succeed
- [PR #180531, @joostlek, 2026-09-02](https://github.com/home-assistant/core/pull/180531#discussion_r3915630219): All flows should end in CREATE_ENTRY or ABORT to test that the flow is able to finish
- [PR #181516, @joostlek, 2026-09-10](https://github.com/home-assistant/core/pull/181516#discussion_r3979002217): All flows should end in CREATE_ENTRY or ABORT to test that they're able to recover. Also, don't patch internals (`_async_probe`)
- [PR #181541, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/181541#discussion_r4008426442): All flows should end in CREATE_ENTRY to test that they are able to recover
- [PR #180437, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/180437#discussion_r4008948264): All flows should end in CREATE_ENTRY to test that they're able to recover
- [PR #182877, @joostlek, 2026-09-25](https://github.com/home-assistant/core/pull/182877#discussion_r4108213715): Let's make sure it finishes with a happy flow so we also test that it can recover

## `fixture-management`: Split complex fixtures into smaller, composable ones and use shared fixtures like mock_config_entry instead of duplicating setup.

Reusable fixtures reduce duplication and improve test maintainability.

Support: 12 comments across 9 PRs, since 2026.

- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863470071): Why don't you use `mock_config_entry`
- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863486278): use mock config entry fixture
- [PR #180878, @joostlek, 2026-08-31](https://github.com/home-assistant/core/pull/180878#discussion_r3895265922): why can't we use the `mock_config_entry` fixture here?
- [PR #180722, @joostlek, 2026-08-31](https://github.com/home-assistant/core/pull/180722#discussion_r3896233585): use the mock_config_entry fixture
- [PR #180531, @joostlek, 2026-09-02](https://github.com/home-assistant/core/pull/180531#discussion_r3915689779): you can use the mock_config_entry fixture here
- [PR #180531, @joostlek, 2026-09-02](https://github.com/home-assistant/core/pull/180531#discussion_r3915733273): Also use the mock config entry
- [PR #180531, @joostlek, 2026-09-02](https://github.com/home-assistant/core/pull/180531#discussion_r3915741819): use the mock config entry fixture
- [PR #181262, @erwindouna, 2026-09-04](https://github.com/home-assistant/core/pull/181262#discussion_r3931259649): Can't we re-use the mock in `conftest`? This is setting up a raw new one. :)
- [PR #181686, @zweckj, 2026-09-09](https://github.com/home-assistant/core/pull/181686#discussion_r3965563770): elsewhere you have the `mock_device` fixture - any reason you are not using that here?
- [PR #168419, @joostlek, 2026-09-16](https://github.com/home-assistant/core/pull/168419#discussion_r4025755575): Use the mock_config_entry fixture here
- [PR #174407, @joostlek, 2026-09-17](https://github.com/home-assistant/core/pull/174407#discussion_r4036397810): I'd split this up in 3 fixtures, as that makes it easier to maintain and overwrite. The fixtures can depend on each other so you only need 1 to activate everything
- [PR #177108, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/177108#discussion_r4047739770): Instead make the mock config entry a common fixture

## `pr-scope`: Split unrelated changes, major features, or flows like reauth into separate pull requests.

Focused PRs are easier to review, test, and merge.

Support: 12 comments across 7 PRs, since 2026.

- [PR #178361, @Markus98, 2026-08-25](https://github.com/home-assistant/core/pull/178361#discussion_r3851116514): Could you split out this change like joostlek asked and mark `entity-unique-id` as `todo` for this PR? This would mean also removing `"quality_scale": "bronze",` from `manifest.json` for this PR. After that this would be an easy merge, and the `entity-unique-id` + bronze quality
- [PR #180349, @joostlek, 2026-08-29](https://github.com/home-assistant/core/pull/180349#discussion_r3886694339): Can we split this off to a separate PR?
- [PR #180349, @joostlek, 2026-08-29](https://github.com/home-assistant/core/pull/180349#discussion_r3886694856): Let's keep reauth and reconfigure for a later PR
- [PR #180531, @joostlek, 2026-08-31](https://github.com/home-assistant/core/pull/180531#discussion_r3896874014): let's omit reauth as well
- [PR #180975, @erwindouna, 2026-09-01](https://github.com/home-assistant/core/pull/180975#discussion_r3901345015): I think these should be in a separate PR, since your PR descrption mentions to adding the reauth flow. Please split if off. :)
- [PR #180975, @erwindouna, 2026-09-01](https://github.com/home-assistant/core/pull/180975#discussion_r3901572400): This is a _new_ addition to the coordinator. Please split if off, to have the scope on the reauth flow. :)
- [PR #178466, @gjohansson-ST, 2026-09-19](https://github.com/home-assistant/core/pull/178466#discussion_r4053056318): I haven't looked at copilots comments, I'll take a look. But adding the reconfigure flow should be done in a follow-up actually rather than this PR.
- [PR #181140, @erwindouna, 2026-09-25](https://github.com/home-assistant/core/pull/181140#discussion_r4107046490): I like this, but it changes the scope and makes the PR a bit too big. Can you please split it off in a separate PR? :)
- [PR #178466, @joostlek, 2026-09-25](https://github.com/home-assistant/core/pull/178466#discussion_r4108092107): Please keep reconfigure for a later PR
- [PR #178466, @joostlek, 2026-09-25](https://github.com/home-assistant/core/pull/178466#discussion_r4108101324): Not sure why we'd need this, as in, other transport integrations also don't have this, so mind splitting this out from this PR?
- [PR #178466, @joostlek, 2026-09-25](https://github.com/home-assistant/core/pull/178466#discussion_r4108102546): Please keep reconfigure for a later PR
- [PR #183419, @erwindouna, 2026-09-28](https://github.com/home-assistant/core/pull/183419#discussion_r4121693638): The coordinator is a total new feature here. Please add this in a separate PR.

## `avoid-reauth-reconfig-initial-pr`: Do not include reauthentication or reconfiguration functionality in the initial PR for a new integration.

This allows incremental development and review of complex flows.

Support: 9 comments across 8 PRs, since 2026.

- [PR #179695, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/179695#discussion_r3845216732): Can we keep reauth for a later PR?
- [PR #168143, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/168143#discussion_r3847515803): Keep out reauth from the initial PR
- [PR #180440, @joostlek, 2026-08-29](https://github.com/home-assistant/core/pull/180440#discussion_r3886637206): can we omit reauth and reconfigure for the initial PR?
- [PR #181083, @joostlek, 2026-09-03](https://github.com/home-assistant/core/pull/181083#discussion_r3923916319): Can we keep reconfigure out of this PR
- [PR #181960, @joostlek, 2026-09-12](https://github.com/home-assistant/core/pull/181960#discussion_r3997649552): Keep reauth from the initial PR
- [PR #180515, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/180515#discussion_r4008854847): Please keep reconfigure out for the initial PR
- [PR #181591, @joostlek, 2026-09-15](https://github.com/home-assistant/core/pull/181591#discussion_r4016037527): Keep reauth out of this PR
- [PR #165993, @joostlek, 2026-09-16](https://github.com/home-assistant/core/pull/165993#discussion_r4025797367): New integrations shouldn't have reauth in it to keep the amount of stuff to review lower
- [PR #181591, @joostlek, 2026-09-28](https://github.com/home-assistant/core/pull/181591#discussion_r4122355720): No we want to keep reauth out of the initial PR. You can add it in a later PT

## `avoid-direct-coordinator-interaction-in`: Do not interact with the coordinator directly in tests; use time freezing or let the coordinator tick naturally.

This ensures proper simulation of real-world behavior and avoids bypassing integration logic.

Support: 7 comments across 7 PRs, since 2026.

- [PR #178684, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/178684#discussion_r3862220528): we shouldn't touch the coordinator data, instead repatch the library to what you expect it returns and trigger a refresh by freezing and skipping time
- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863493965): We should not touch the coordinator directly. Instead we should patch the library, have it set up the integration, and then assert the state machine to see everything is behaving like it should
- [PR #181634, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/181634#discussion_r3960236293): we shouldn't touch the coordinator directly
- [PR #181659, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/181659#discussion_r3960421915): Don't touch the coordinator
- [PR #182309, @joostlek, 2026-09-15](https://github.com/home-assistant/core/pull/182309#discussion_r4015990504): We shouldn't touch the coordinator directly, instead test this via the sensor platform and use the freezer to skip time and implicitly refresh the coordinator
- [PR #181865, @joostlek, 2026-09-22](https://github.com/home-assistant/core/pull/181865#discussion_r4071361857): Don't touch the coordinator
- [PR #183033, @zweckj, 2026-09-24](https://github.com/home-assistant/core/pull/183033#discussion_r4091306796): Do not get and trigger the coordinator directly. Use a freezer to let it tick instead.

## `snapshot-testing-complex-data`: Use snapshot testing with snapshot_platform for complex data structures instead of writing explicit assertions.

Reduces test maintenance overhead and ensures comprehensive structure validation.

Support: 6 comments across 6 PRs, since 2026.

- [PR #178132, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/178132#discussion_r3843474663): Instead use `snapshot_platform` to fixate all entities
- [PR #180689, @frenck, 2026-08-29](https://github.com/home-assistant/core/pull/180689#discussion_r3887627244): Let's use snapshot testing instead.
- [PR #180531, @joostlek, 2026-09-02](https://github.com/home-assistant/core/pull/180531#discussion_r3915739665): I'd recommend looking into `snapshot_platform` helper, as that will fixate all of this
- [PR #169872, @joostlek, 2026-09-03](https://github.com/home-assistant/core/pull/169872#discussion_r3923755167): instead use `snapshot_platform`
- [PR #181386, @erwindouna, 2026-09-05](https://github.com/home-assistant/core/pull/181386#discussion_r3941829804): Instead of manually asserts, please introduce the snapshot platform here. It's very thorough and records all changes ever done. :)
- [PR #176149, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/176149#discussion_r3960847763): instead use `snapshot_platform`

## `avoid-inline-patching`: Avoid inline patching; use common patching patterns or fixtures instead.

This improves test readability and reusability of test setup logic.

Support: 5 comments across 5 PRs, since 2026.

- [PR #179543, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/179543#discussion_r3847853897): why do we patch inline instead of using the common patch?
- [PR #176640, @Markus98, 2026-09-09](https://github.com/home-assistant/core/pull/176640#discussion_r3965315133): Let's make this into a fixture in `conftest.py`. Also we should fully type all the functions.
- [PR #178024, @Markus98, 2026-09-10](https://github.com/home-assistant/core/pull/178024#discussion_r3979957416): We should probably move this fixture to `conftest.py`. That is the convention. Also, this fixture doesn't return `entity_id`s so we should not have `entity_ids` in the fixture name.
- [PR #180437, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/180437#discussion_r4008980467): Can we have this as a fixture in conftest.py?
- [PR #177108, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/177108#discussion_r4047760868): This is stuff I would recommend to move to conftest.py

## `avoid-using-if-statements-in-tests`: Avoid using if statements or conditions in tests to maintain clarity and prevent conditional logic from obscuring test intent.

This ensures tests are deterministic and easy to understand.

Support: 5 comments across 5 PRs, since 2026.

- [PR #179349, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/179349#discussion_r3847769497): we should not have if statements in the tests
- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863466843): we shouldn't have if statements in the tests, let's alwayus make sure they recover
- [PR #167872, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/167872#discussion_r3864101839): Please don't use if statements in the tests though. I am also not seeing the difference between these 2. If they are different, then they're okay to be split
- [PR #182075, @MartinHjelmare, 2026-09-13](https://github.com/home-assistant/core/pull/182075#discussion_r3999102711): We don't want conditions in tests.
- [PR #177108, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/177108#discussion_r4047721802): as this is a direct test helper, let's not add if statements

## `avoid-bumping-dependencies-with-function`: Bump dependencies in a separate PR from functional changes.

This isolates changes and makes reviews more focused.

Support: 5 comments across 5 PRs, since 2026.

- [PR #173262, @joostlek, 2026-08-29](https://github.com/home-assistant/core/pull/173262#discussion_r3886756499): Please bump in a separate PR
- [PR #176386, @joostlek, 2026-08-29](https://github.com/home-assistant/core/pull/176386#discussion_r3886758494): Please bump in a separate PR
- [PR #182318, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/182318#discussion_r4047543616): Can we bump this in a separate PR?
- [PR #183424, @erwindouna, 2026-09-28](https://github.com/home-assistant/core/pull/183424#discussion_r4120628209): This has to be in it's own dedicated PR. Please split if off. :)
- [PR #183419, @erwindouna, 2026-09-28](https://github.com/home-assistant/core/pull/183419#discussion_r4121695949): Dependency bumps need to be in their own dedicated PR.

## `implement-consistent-patterns-by-inlinin`: Implement consistent patterns by inlining simple functions as lambdas in entity descriptions.

It reduces unnecessary function definitions and maintains consistency across sensors with minimal business logic.

Support: 5 comments across 2 PRs, since 2026.

- [PR #181265, @erwindouna, 2026-09-04](https://github.com/home-assistant/core/pull/181265#discussion_r3931671758): This function has little to no business logic. I think this can be done inline to check if it's not None, with a lambda. This is a pattern you're also doing across the other sensors, so it's good to be consistent. :)
- [PR #181278, @erwindouna, 2026-09-04](https://github.com/home-assistant/core/pull/181278#discussion_r3932238212): You can optimize this method and add the inline check. It makes it a bit more explicit and reduce a function which contains little to no business logic. :)
- [PR #181278, @erwindouna, 2026-09-04](https://github.com/home-assistant/core/pull/181278#discussion_r3932606335): I think can you inline this, with a lambda and follow the rest of the patterns. Try to make the code follow the same consistent patterns. :)
- [PR #181278, @erwindouna, 2026-09-04](https://github.com/home-assistant/core/pull/181278#discussion_r3932610800): You can inline this with a lambda too. It's only used once and is perfectly suitable for lambda.
- [PR #181278, @erwindouna, 2026-09-04](https://github.com/home-assistant/core/pull/181278#discussion_r3932788167): I see, thanks for explaining. That make sense. This function is also a perfect candidate to be a lambda, so that would be good to follow-up. :)

## `use-entity-category-diagnostic`: Mark binary sensors and sensors that expose diagnostic information with entity category diagnostic.

This ensures diagnostic entities are properly grouped and hidden by default in the UI.

Support: 5 comments across 2 PRs, since 2026.

- [PR #180825, @balloob, 2026-08-30](https://github.com/home-assistant/core/pull/180825#discussion_r3890520470): Should this be diagnostic entity category?
- [PR #180825, @balloob, 2026-08-30](https://github.com/home-assistant/core/pull/180825#discussion_r3890520598): Should this be diagnostic entity category?
- [PR #180825, @balloob, 2026-08-30](https://github.com/home-assistant/core/pull/180825#discussion_r3890524959): Diagnostic entity category
- [PR #180825, @balloob, 2026-08-30](https://github.com/home-assistant/core/pull/180825#discussion_r3890526480): Diagnostic entity category
- [PR #180952, @balloob, 2026-09-01](https://github.com/home-assistant/core/pull/180952#discussion_r3901909228): This one also needs entity category diagnostic.

## `use-common-translation-keys`: Use common translation keys from homeassistant/strings.json for standard statuses like paused or charging.

This ensures consistency in user-facing status messages across integrations.

Support: 5 comments across 3 PRs, since 2026.

- [PR #180437, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/180437#discussion_r3961536773): use common key references
- [PR #177108, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/177108#discussion_r4047698719): Some of the statuses here like paused, standby and charging are ones that you can use common key references to `homeassistant/strings.json`
- [PR #181591, @joostlek, 2026-09-28](https://github.com/home-assistant/core/pull/181591#discussion_r4122409325): We have common translation strings for this
- [PR #181591, @joostlek, 2026-09-28](https://github.com/home-assistant/core/pull/181591#discussion_r4122412344): For this one as well
- [PR #181591, @joostlek, 2026-09-28](https://github.com/home-assistant/core/pull/181591#discussion_r4122417717): These 2 as well (off I'm sure, the other one I'm not)

## `avoid-patching-integration-internals`: Avoid patching integration internals; instead, patch the underlying library or client.

This ensures tests validate integration behavior without relying on internal implementation details.

Support: 4 comments across 4 PRs, since 2026.

- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863459675): can we instead patch the library? We ideally don't patch internals
- [PR #181516, @joostlek, 2026-09-10](https://github.com/home-assistant/core/pull/181516#discussion_r3979002217): All flows should end in CREATE_ENTRY or ABORT to test that they're able to recover. Also, don't patch internals (`_async_probe`)
- [PR #182152, @MartinHjelmare, 2026-09-16](https://github.com/home-assistant/core/pull/182152#discussion_r4024795535): Please try to patch and use the library client instead to test this behavior. We want to avoid interacting with integration details in the tests. https://developers.home-assistant.io/docs/development_testing#writing-tests-for-integrations
- [PR #182389, @joostlek, 2026-09-18](https://github.com/home-assistant/core/pull/182389#discussion_r4047936555): can we avoid patching internals?

## `avoid-accessing-runtime-data-in-tests`: Do not access or modify runtime_data in tests.

This ensures tests reflect real integration behavior through proper setup and state checks.

Support: 4 comments across 3 PRs, since 2026.

- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863496335): Also don't touch runtime_data
- [PR #165457, @joostlek, 2026-08-30](https://github.com/home-assistant/core/pull/165457#discussion_r3889789031): let's avoid touching runtime_data
- [PR #181988, @MartinHjelmare, 2026-09-12](https://github.com/home-assistant/core/pull/181988#discussion_r3996105455): We shouldn't access integration details in runtime_data.
- [PR #176238, @joostlek, 2026-09-16](https://github.com/home-assistant/core/pull/176238#discussion_r4026209256): we shouldn't touch the runtime_data

## `avoid-calculating-entity-states-in-integ`: Do not calculate entity states in the integration; this logic should reside in the library.

This separates concerns and improves testability and reuse.

Support: 4 comments across 2 PRs, since 2026.

- [PR #180393, @MartinHjelmare, 2026-08-28](https://github.com/home-assistant/core/pull/180393#discussion_r3880296091): This is a calculated value. We don't allow calculating states in integrations that integrate with devices or services. The integration should represent the API as is, while following our entity design.
- [PR #180393, @MartinHjelmare, 2026-08-28](https://github.com/home-assistant/core/pull/180393#discussion_r3880439966): This is calculating the sensor state. This belongs in the library if it's needed.
- [PR #180722, @frenck, 2026-08-30](https://github.com/home-assistant/core/pull/180722#discussion_r3890317721): Honestly, this should be in the library :) If you make this properties available in the objects, you'd save yourself tons lines of code below as well.
- [PR #180393, @MartinHjelmare, 2026-08-31](https://github.com/home-assistant/core/pull/180393#discussion_r3895479209): This is still a calculated value that is used for a entity state. That's not allowed. I suggest removing that entity for now, and we can discuss separately how to best expose the corresponding data point.

## `avoid-putting-logic-in-try-blocks`: Only include code in try blocks that can potentially raise exceptions.

This prevents catching exceptions from code that cannot fail, improving clarity.

Support: 4 comments across 4 PRs, since 2026.

- [PR #179695, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/179695#discussion_r3845195346): Only keep things in the try block that can raise
- [PR #168143, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/168143#discussion_r3847537533): only keep things in the try block that can raise
- [PR #180440, @joostlek, 2026-08-29](https://github.com/home-assistant/core/pull/180440#discussion_r3886617410): Only keep things in the try block that are able to raise
- [PR #152802, @joostlek, 2026-09-11](https://github.com/home-assistant/core/pull/152802#discussion_r3988517289): only keep things in the try block that can raise

## `parametrize-tests-instead-of-writing-sep`: Parametrize tests instead of writing separate test functions for similar cases.

It reduces code duplication and makes test coverage clearer.

Support: 4 comments across 4 PRs, since 2026.

- [PR #179970, @justanotherariel, 2026-08-24](https://github.com/home-assistant/core/pull/179970#discussion_r3843136243): Can we paramaterize `test_remove_child_device_and_restore` to include this test?
- [PR #177366, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/177366#discussion_r3847908549): These 2 can be parametrized
- [PR #178407, @Markus98, 2026-09-09](https://github.com/home-assistant/core/pull/178407#discussion_r3968461307): I would like this to be included in the test above (`test_get_triggers`) instead with `@pytest.mark.parametrize()`
- [PR #182054, @Markus98, 2026-09-15](https://github.com/home-assistant/core/pull/182054#discussion_r4012978315): This test and `test_entry_reload_from_migration_error_fails` below both cover the same `OperationNotAllowed` branch, just from different states. Since the method raises before touching the integration, the `mock_integration`/`mock_platform` setup and the `async_*` mocks are not n

## `assert-unique-id-in-config-flow`: Assert the unique_id in config flow tests when applicable.

This verifies that entities are correctly identified and avoids duplication issues.

Support: 3 comments across 3 PRs, since 2026.

- [PR #180057, @erwindouna, 2026-08-25](https://github.com/home-assistant/core/pull/180057#discussion_r3854058810): Shouldn't we also assert the unique_id? :)
- [PR #165457, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/165457#discussion_r3863461001): Also assert the unique id
- [PR #180437, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/180437#discussion_r4008943554): also assert the unique id

## `avoid-using-parametrize-single-case`: Avoid using parametrize when only a single test case is used.

This avoids unnecessary complexity in test definitions.

Support: 3 comments across 2 PRs, since 2026.

- [PR #180197, @arturpragacz, 2026-08-26](https://github.com/home-assistant/core/pull/180197#discussion_r3862730617): Pointless `parametrize`, only a single case.
- [PR #180438, @bieniu, 2026-08-29](https://github.com/home-assistant/core/pull/180438#discussion_r3886069984): `parametrize` is not needed with only one test case.
- [PR #180438, @bieniu, 2026-08-29](https://github.com/home-assistant/core/pull/180438#discussion_r3886079388): `parametrize` is not needed with only one test case.

## `avoid-manual-coordinator-refresh`: Freeze and advance time to trigger coordinator refreshes instead of relying on integration-specific runtime data like the coordinator directly.

This simulates real-world timing and avoids bypassing normal update mechanisms.

Support: 3 comments across 3 PRs, since 2026.

- [PR #179057, @MartinHjelmare, 2026-08-26](https://github.com/home-assistant/core/pull/179057#discussion_r3860055001): Please move time forward instead, to trigger a coordinator refresh. To make the tests robust, we don't want to interact with integration details in runtime data like the coordinator.
- [PR #181602, @MartinHjelmare, 2026-09-08](https://github.com/home-assistant/core/pull/181602#discussion_r3956999049): Please don't use integration details in runtime data, like the coordinator, in the tests. Freeze time and move time forward to trigger a coordinator refresh instead. https://developers.home-assistant.io/docs/development_testing#writing-tests-for-integrations
- [PR #181865, @joostlek, 2026-09-22](https://github.com/home-assistant/core/pull/181865#discussion_r4071364148): Freeze and skip time instead

## `merge-related-test-cases-into-a-single-t`: Merge related test cases into a single test when they share setup and logic.

Combining similar tests reduces duplication and improves maintainability.

Support: 3 comments across 3 PRs, since 2026.

- [PR #180531, @joostlek, 2026-09-02](https://github.com/home-assistant/core/pull/180531#discussion_r3915735717): These 2 can be combined
- [PR #181516, @joostlek, 2026-09-10](https://github.com/home-assistant/core/pull/181516#discussion_r3978997363): merge this one with the next test
- [PR #182949, @bieniu, 2026-09-26](https://github.com/home-assistant/core/pull/182949#discussion_r4111644728): I think `test_existing_unique_id_is_kept` and `test_migrate_empty_unique_id` could be merged into one test.

## `avoid-unnecessary-data-parsing-in-models`: Move data parsing logic from models or entities into the underlying library when possible.

This promotes code reuse and separates concerns.

Support: 3 comments across 2 PRs, since 2026.

- [PR #180440, @balloob, 2026-08-28](https://github.com/home-assistant/core/pull/180440#discussion_r3878403831): This kind of code should be in the library. Being able to raise when an error happens. In here we just catch the specific errors.
- [PR #180440, @balloob, 2026-08-28](https://github.com/home-assistant/core/pull/180440#discussion_r3878405065): Shouldn't these be things in the library?
- [PR #179635, @joostlek, 2026-08-30](https://github.com/home-assistant/core/pull/179635#discussion_r3889906883): I think the parsing part is something for the library to do, and then I think this can just be read in the entity.py

## `entity-name-handling`: Set _attr_name = None when the entity is the primary feature of the device to avoid redundant naming.

This prevents duplicate or confusing entity names in the UI.

Support: 3 comments across 2 PRs, since 2026.

- [PR #179700, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/179700#discussion_r3847594228): shouldn't we set `_attr_name = None` instead? I would assume that for a device where we create a dehumidifier the dehumidifier is the main feature of the device
- [PR #179123, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/179123#discussion_r3863927502): you can omit the translation key and use `_attr_name = None` to make the camera entity the main feature on the device
- [PR #179700, @joostlek, 2026-08-26](https://github.com/home-assistant/core/pull/179700#discussion_r3864751145): ```suggestion self._attr_name = None ```

## `test-data-storage`: Store JSON-based test data in fixture files within the fixtures folder using get_fixture_path or load_json_fixture.

Centralized test data improves readability and reuse.

Support: 3 comments across 3 PRs, since 2026.

- [PR #177918, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/177918#discussion_r3961263241): instead use `load_json_fixture` which is a common test helper instead
- [PR #180437, @joostlek, 2026-09-14](https://github.com/home-assistant/core/pull/180437#discussion_r4008933765): Look at storing this in a json file in fixtures folder
- [PR #182457, @arturpragacz, 2026-09-17](https://github.com/home-assistant/core/pull/182457#discussion_r4035672795): We could use `get_fixture_path`. ```suggestion from tests.common import extract_stack_to_frame, get_fixture_path INCLUDE_DIRS_FIXTURE = str(get_fixture_path("core/config/annotations/include_dirs")) ```

## `use-consistent-naming`: Use consistent and meaningful naming for functions, variables, and parameters, such as avoiding 'async_' prefix for non-async functions and using 'info' instead of 'data'.

This improves code readability and maintainability.

Support: 3 comments across 3 PRs, since 2026.

- [PR #176110, @Markus98, 2026-08-24](https://github.com/home-assistant/core/pull/176110#discussion_r3843128729): One nit I have about the naming is that right now in this file we kind of have three different terms that refer to almost the same concept: `location`, `position`, and `coordinates`. I would probably use either `coordinates` or `position` for these variable names in `nws` to make
- [PR #173469, @Markus98, 2026-09-01](https://github.com/home-assistant/core/pull/173469#discussion_r3903400626): Maybe we could just use `info` instead of `data` here to be more consistent.
- [PR #183294, @erwindouna, 2026-09-27](https://github.com/home-assistant/core/pull/183294#discussion_r4115987301): Nitpicking here, but this is no async function. Renaming would be suggested.

## `use-extended-config-entry-types`: Use extended config entry types and type hints in coordinators for better type safety.

This improves code clarity and enables better IDE support and error detection.

Support: 3 comments across 3 PRs, since 2026.

- [PR #178132, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/178132#discussion_r3843445961): please use the extended ConfigEntry here
- [PR #168143, @joostlek, 2026-08-24](https://github.com/home-assistant/core/pull/168143#discussion_r3847533921): use extended config entry
- [PR #175855, @joostlek, 2026-09-16](https://github.com/home-assistant/core/pull/175855#discussion_r4026284417): Use the extended config entry

## `use-freezer-to-advance-time-in-tests`: Use freezer.tick(x) or the freezer to advance and control time in tests instead of arbitrary delays.

This provides precise and reliable time manipulation in asynchronous tests.

Support: 3 comments across 3 PRs, since 2026.

- [PR #177918, @joostlek, 2026-09-08](https://github.com/home-assistant/core/pull/177918#discussion_r3961267840): 1. this is a method, so this should be in `__init__.py` 2. Please use the freezer to skip time 3. You don't need the extra second
- [PR #161442, @joostlek, 2026-09-11](https://github.com/home-assistant/core/pull/161442#discussion_r3988413797): use `freezer.tick(x)` instead
- [PR #176238, @joostlek, 2026-09-16](https://github.com/home-assistant/core/pull/176238#discussion_r4026216504): Please use the freezer to skip time

## `typing-type-checking`: Use TYPE_CHECKING from typing to avoid runtime import overhead.

Improves performance by preventing unnecessary imports during execution.

Support: 3 comments across 2 PRs, since 2026.

- [PR #181283, @erwindouna, 2026-09-06](https://github.com/home-assistant/core/pull/181283#discussion_r3945234078): Please use TYPE_CHECKING here.
- [PR #182250, @abmantis, 2026-09-15](https://github.com/home-assistant/core/pull/182250#discussion_r4014052202): lets wrap this on a TYPE_CHECKING condition: https://developers.home-assistant.io/docs/development_guidelines/#using-assert-to-narrow-types
- [PR #182250, @abmantis, 2026-09-15](https://github.com/home-assistant/core/pull/182250#discussion_r4014074949): lets wrap this on a TYPE_CHECKING condition: developers.home-assistant.io/docs/development_guidelines#using-assert-to-narrow-types

## `wait-background-tasks-testing`: Wait for background tasks when testing coordinator refreshes using hass.async_block_till_done with wait_background_tasks=True.

Ensures test reliability by confirming all asynchronous operations are complete.

Support: 3 comments across 3 PRs, since 2026.

- [PR #179057, @MartinHjelmare, 2026-08-26](https://github.com/home-assistant/core/pull/179057#discussion_r3861848801): The coordinator runs the refresh as a background task. We need to wait for background tasks here. Please check all places where we move time forward to trigger a coordinator refresh. ```suggestion await hass.async_block_till_done(wait_background_tasks=True) ```
- [PR #180393, @MartinHjelmare, 2026-08-28](https://github.com/home-assistant/core/pull/180393#discussion_r3880456600): If we're waiting for a coordinator refresh we need to wait for backgrounds tasks since the coordinator refresh is a background task.
- [PR #181602, @MartinHjelmare, 2026-09-08](https://github.com/home-assistant/core/pull/181602#discussion_r3961775477): The coordinator refresh runs as a background task so we need to wait for background tasks here.
