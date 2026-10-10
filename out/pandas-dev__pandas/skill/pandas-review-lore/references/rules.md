# Evidence for pandas-dev/pandas review rules

Every rule below cites real maintainer review comments. 0 candidate rules were rejected because they cited comments that do not exist.

## `whatsnew-categorization-and-content`: Place whatsnew entries in the correct section, avoid internal changes, and focus on concise, user-facing impact.

This ensures the changelog remains useful and accurate for end users and avoids clutter from non-essential changes.

Support: 10 comments across 9 PRs, since 2026.

- [PR #66498, @jbrockmendel, 2026-07-28](https://github.com/pandas-dev/pandas/pull/66498#discussion_r3667965804): i dont think we want implementation details in the whatsnew
- [PR #66557, @jbrockmendel, 2026-08-02](https://github.com/pandas-dev/pandas/pull/66557#discussion_r3697309610): dont include implementation details in the whatsnew
- [PR #66658, @jbrockmendel, 2026-08-09](https://github.com/pandas-dev/pandas/pull/66658#discussion_r3745521722): dont describe implementation details here, only user-facing changes
- [PR #66708, @jbrockmendel, 2026-08-14](https://github.com/pandas-dev/pandas/pull/66708#discussion_r3787603705): avoid talking about implementation details
- [PR #66836, @rhshadrach, 2026-08-21](https://github.com/pandas-dev/pandas/pull/66836#discussion_r3829824502): I believe the only place this code is hit is I/O, can you move to the I/O section and make it something like ```rst - :func:`read_csv`, :func:`read_fwf`, and :func:`read_excel` with a numeric :class:`ArrowDtype` (e.g. ``dtype="double[pyarrow]"``) now raise ``ValueError`` for an
- [PR #66708, @jbrockmendel, 2026-08-31](https://github.com/pandas-dev/pandas/pull/66708#discussion_r3898128722): this still contains too much internal detail. we only need the user-facing bit
- [PR #68168, @rhshadrach, 2026-09-07](https://github.com/pandas-dev/pandas/pull/68168#discussion_r3952659172): This is quite verbose. Can you make this more concise, something like "Reduced duplicate warning messages in DataFrame.to_excel when contents are too long" is sufficient.
- [PR #66380, @rhshadrach, 2026-09-07](https://github.com/pandas-dev/pandas/pull/66380#discussion_r3952740561): Can you make this more concise. You can remove "instead of returning..." and the error message, they aren't necessary.
- [PR #67406, @jbrockmendel, 2026-09-08](https://github.com/pandas-dev/pandas/pull/67406#discussion_r3953398232): this can be much more concise
- [PR #66375, @jorisvandenbossche, 2026-09-09](https://github.com/pandas-dev/pandas/pull/66375#discussion_r3970140312): Please reduce the verbosity here, just mentioning this is for registering the pyarrow extension types at import is good enough

## `test-organization-and-structure`: Place test functions, files, and imports in the correct locations and organize them for clarity and reuse.

Proper organization improves discoverability, maintainability, and consistency across the test suite.

Support: 10 comments across 8 PRs, since 2026.

- [PR #65701, @jbrockmendel, 2026-06-06](https://github.com/pandas-dev/pandas/pull/65701#discussion_r3368212012): please import at the top
- [PR #66293, @jbrockmendel, 2026-07-15](https://github.com/pandas-dev/pandas/pull/66293#discussion_r3590872006): import at the top of the file
- [PR #66344, @jbrockmendel, 2026-07-17](https://github.com/pandas-dev/pandas/pull/66344#discussion_r3604354648): imports at the top of the file
- [PR #66357, @jbrockmendel, 2026-07-20](https://github.com/pandas-dev/pandas/pull/66357#discussion_r3616203079): i think this belongs in TestUltraJSONTests?
- [PR #66530, @jbrockmendel, 2026-08-01](https://github.com/pandas-dev/pandas/pull/66530#discussion_r3694248467): belongs in tests.arrays.interval.test_interval?
- [PR #66318, @jbrockmendel, 2026-08-09](https://github.com/pandas-dev/pandas/pull/66318#discussion_r3744544488): imports at the top of the file
- [PR #64535, @mroeschke, 2026-08-11](https://github.com/pandas-dev/pandas/pull/64535#discussion_r3759903875): Can you make this a `pytest.fixture`?
- [PR #66584, @rhshadrach, 2026-08-11](https://github.com/pandas-dev/pandas/pull/66584#discussion_r3761727286): Can you keep the style of these tests consistent with other writers and introduce a `tmp_excel` fixture (see test_odswriter.py or test_xlsxwriter.py for examples).
- [PR #64535, @mroeschke, 2026-08-12](https://github.com/pandas-dev/pandas/pull/64535#discussion_r3769629190): You can also make this a fixture as part of the `BasePlottingTests` I think like ```python class BasePlottingTests: @pytest.fixture def plot_data(self, data): return pd.DataFrame(...) def test_plot_on_x_axis(self, plot_data): .... ```
- [PR #64535, @jbrockmendel, 2026-08-24](https://github.com/pandas-dev/pandas/pull/64535#discussion_r3846411929): Good point. what about something like ``` @pytest.fixture def mpl(self, request): self.skip_if_no_matplotlib() return request.getfixturevalue("mpl_cleanup") @pytest.fixture(params=[True, False], ids=["skipna", "no_skipna"]) def plot_data(self, data, request, mp

## `parametrize-over-repetition`: Parametrize test cases instead of writing repetitive logic for different inputs or engines.

This reduces code duplication and improves clarity and maintainability of test suites.

Support: 8 comments across 8 PRs, since 2026.

- [PR #65332, @rhshadrach, 2026-04-25](https://github.com/pandas-dev/pandas/pull/65332#discussion_r3142012035): Instead of having two tests at once, can you parametrize. ```python @pytest.mark.parametrize("test_empty", [True, False]) ``` Then can do: ```python if test_empty: df = df.iloc[:0] ... if test_empty: expected = DataFrame(...) else: expected = DataFrame(...) ```
- [PR #65052, @rhshadrach, 2026-05-05](https://github.com/pandas-dev/pandas/pull/65052#discussion_r3191559227): Can you instead parametrize with @pytest.mark.parametrize("na_position", ["first", "last"]) Just need to set `expected` based on the `na_position` value then.
- [PR #66046, @jbrockmendel, 2026-07-05](https://github.com/pandas-dev/pandas/pull/66046#discussion_r3525475679): parametrize over ascending?
- [PR #65349, @jbrockmendel, 2026-08-09](https://github.com/pandas-dev/pandas/pull/65349#discussion_r3744711611): can you parametrize over engine like other tests
- [PR #65675, @jbrockmendel, 2026-08-18](https://github.com/pandas-dev/pandas/pull/65675#discussion_r3808072751): i think you need to parametrize over engine to get the old bug
- [PR #66909, @Alvaro-Kothe, 2026-08-24](https://github.com/pandas-dev/pandas/pull/66909#discussion_r3848421835): Can this be a parametrized test?
- [PR #66659, @Alvaro-Kothe, 2026-08-29](https://github.com/pandas-dev/pandas/pull/66659#discussion_r3887344354): This should be parametrized on `bias`
- [PR #68206, @rhshadrach, 2026-09-10](https://github.com/pandas-dev/pandas/pull/68206#discussion_r3978835865): There are a few different paths through the code here. Can you parametrize over three cases: single EA block; two EA blocks; and a NumPy block. Something like: ``` "data, dtype", [ ({"a": [1, 2, 3]}, "Int64"), ({"a": [1, 2, 3], "b": [4, 5, 6]}, "Int64"), ({"a": [1, 2

## `github-issue-linking-in-tests`: Link every new test to its corresponding GitHub issue using a comment with the issue reference format #GHXXXXX.

This ensures traceability between tests and the issues they address, improving maintainability and context for future contributors.

Support: 7 comments across 6 PRs, since 2026.

- [PR #65332, @rhshadrach, 2026-04-25](https://github.com/pandas-dev/pandas/pull/65332#discussion_r3142009247): Add a reference to the GH issue as a comment on the first line. ```suggestion def test_apply_as_index_false_empty_index_name(): # https://github.com/pandas-dev/pandas/issues/48135 df = DataFrame({"A": [4, 4, 4], "B": [9, 9, 9]}) ```
- [PR #65052, @rhshadrach, 2026-05-05](https://github.com/pandas-dev/pandas/pull/65052#discussion_r3191551426): Can you add a reference to the GitHub issue as a comment on the first line of these tests. # https://github.com/pandas-dev/pandas/issues/64977
- [PR #65052, @rhshadrach, 2026-05-16](https://github.com/pandas-dev/pandas/pull/65052#discussion_r3252783792): Your tests no longer have the reference to the issue. Can you restore these on all added tests.
- [PR #65675, @rhshadrach, 2026-05-20](https://github.com/pandas-dev/pandas/pull/65675#discussion_r3276999079): Any added tests need to contain a link to the issue (or PR if there is no issue). ```suggestion # https://github.com/pandas-dev/pandas/issues/65664 df = DataFrame({"old": [1, 2, 3]}) ```
- [PR #65806, @rhshadrach, 2026-06-05](https://github.com/pandas-dev/pandas/pull/65806#discussion_r3365581403): Start tests with a ref to the issue. ```suggestion def test_to_dict_index_into_applies_to_nested_mappings(self, df: DataFrame): # https://github.com/pandas-dev/pandas/issues/65778 ```
- [PR #66584, @rhshadrach, 2026-08-11](https://github.com/pandas-dev/pandas/pull/66584#discussion_r3761731425): Link any new tests back to corresponding issue (or PR if no issue exists). ```suggestion def test_read_covered_table_cell_value(tmp_path): # https://github.com/pandas-dev/pandas/issues/66579 ```
- [PR #66380, @rhshadrach, 2026-09-07](https://github.com/pandas-dev/pandas/pull/66380#discussion_r3952767717): ```suggestion # GH#66372 ``` I don't think we need to repeat the comment again; the GitHub reference is enough. In addition, the format I'm suggesting is more common.

## `prefer-full-object-equality-assertions`: Use `tm.assert_frame_equal`, `tm.assert_series_equal`, or similar functions to check the full state of objects, including index, columns, and dtypes.

This ensures comprehensive validation and prevents subtle regressions due to incomplete comparisons.

Support: 5 comments across 5 PRs, since 2026.

- [PR #65332, @rhshadrach, 2026-04-23](https://github.com/pandas-dev/pandas/pull/65332#discussion_r3133571410): Can you assert the full result. ```python expected = DataFrame(...) tm.assert_frame_equal(result, expected) ```
- [PR #65360, @rhshadrach, 2026-04-25](https://github.com/pandas-dev/pandas/pull/65360#discussion_r3141998870): Check the full state of the object (index, columns, dtypes). ```python expected = DataFrame(...) tm.assert_result_equal(result, expected) ```
- [PR #65711, @rhshadrach, 2026-05-28](https://github.com/pandas-dev/pandas/pull/65711#discussion_r3317024563): Always test the full state of the object, e.g. ```python expected = Series(...) tm.assert_series_equal(result, expected) ```
- [PR #65807, @rhshadrach, 2026-06-07](https://github.com/pandas-dev/pandas/pull/65807#discussion_r3369301437): Always check the full state when possible - `expected = DataFrame(...)` as above.
- [PR #66136, @rhshadrach, 2026-07-14](https://github.com/pandas-dev/pandas/pull/66136#discussion_r3575716543): Please check the full state of the result. ```python expected = MultIndex(...) tm.assert_index_equal(result, expected) ```

## `test-edge-cases-and-coverage`: Ensure test coverage includes edge cases such as large integers, small sample sizes, and non-standard dtypes.

Comprehensive coverage helps catch regressions in corner cases that are often sources of bugs.

Support: 5 comments across 5 PRs, since 2026.

- [PR #65869, @jorisvandenbossche, 2026-06-12](https://github.com/pandas-dev/pandas/pull/65869#discussion_r3406270352): Can you instead do `ser.index = ser.index.astype(object)` so we are actually testing with object dtype?
- [PR #66148, @jbrockmendel, 2026-08-09](https://github.com/pandas-dev/pandas/pull/66148#discussion_r3745486314): these are still numpy ints. dont we need to test with an int that doesnt fit in those bounds?
- [PR #66684, @jbrockmendel, 2026-08-10](https://github.com/pandas-dev/pandas/pull/66684#discussion_r3751391766): lets just test with both np.int32 and np.int64 here
- [PR #66603, @jbrockmendel, 2026-08-23](https://github.com/pandas-dev/pandas/pull/66603#discussion_r3839309707): can you add something many-digit like pi to the float parametrization
- [PR #66659, @Alvaro-Kothe, 2026-09-04](https://github.com/pandas-dev/pandas/pull/66659#discussion_r3938515635): Also, does it have test coverage small sample size, where `bias=False` returns `NAN` and `bias=True` doesn't?

## `use-descriptive-variables-and-comments`: Use clear variable names and comments that explain the purpose, not just repeat the code.

Clear naming and meaningful comments improve readability and maintainability of tests and code.

Support: 5 comments across 5 PRs, since 2026.

- [PR #65342, @rhshadrach, 2026-04-25](https://github.com/pandas-dev/pandas/pull/65342#discussion_r3142132745): Can you combine these two checks into the same line. Also the comment should explain why, e.g. # When result is a Series, there is no other axis to sort.
- [PR #65675, @rhshadrach, 2026-05-20](https://github.com/pandas-dev/pandas/pull/65675#discussion_r3276994994): Comment repeats the code; can you remove.
- [PR #65823, @jorisvandenbossche, 2026-06-08](https://github.com/pandas-dev/pandas/pull/65823#discussion_r3371752832): The logic here is clear, but I was first confused about the name `result_missing_mask`, because you are checking here for the dtypes where the result does _not_ use a mask for the missing values
- [PR #65873, @jbrockmendel, 2026-06-13](https://github.com/pandas-dev/pandas/pull/65873#discussion_r3408433104): nitpick pls avoid 1-letter variable names
- [PR #65691, @jbrockmendel, 2026-08-12](https://github.com/pandas-dev/pandas/pull/65691#discussion_r3768800149): this comment isnt adding anything

## `avoid-unnecessary-complexity-in-tests`: Use the simplest possible constructs in tests, avoiding unnecessary DataFrame constructions, deep copies, or indirections.

Simpler tests are easier to understand, debug, and maintain while still validating the intended behavior.

Support: 4 comments across 3 PRs, since 2026.

- [PR #65052, @jbrockmendel, 2026-06-01](https://github.com/pandas-dev/pandas/pull/65052#discussion_r3336580516): can we do this without constructing a DataFrame?
- [PR #63635, @jbrockmendel, 2026-06-03](https://github.com/pandas-dev/pandas/pull/63635#discussion_r3350702221): can you pass deep=False here
- [PR #66238, @WillAyd, 2026-07-16](https://github.com/pandas-dev/pandas/pull/66238#discussion_r3595478244): Let's get rid of this indirection and just refer to the argument directly
- [PR #66238, @WillAyd, 2026-07-16](https://github.com/pandas-dev/pandas/pull/66238#discussion_r3599286500): Let's remove unnecessary indirections like this

## `check-dtype-and-index-codes-correctly`: Check the dtype of MultiIndex codes and ensure expected and actual dtypes match without relying on `check_dtype=False`.

Accurate dtype checking prevents silent mismatches and ensures correct behavior across platforms.

Support: 3 comments across 3 PRs, since 2026.

- [PR #65701, @jorisvandenbossche, 2026-05-27](https://github.com/pandas-dev/pandas/pull/65701#discussion_r3312301203): Can you check the dtype of the codes of `mi2`? Because I think the MultiIndex() constructor will normalize the dtypes, even when constructed this way (that is the reason that in the issue https://github.com/pandas-dev/pandas/issues/65700 I assigned to `_codes` directly to constru
- [PR #63831, @rhshadrach, 2026-08-30](https://github.com/pandas-dev/pandas/pull/63831#discussion_r3889687415): This PR is directly impacting the dtype, can you refine this test so that you don't need to pass `check_dtype=False`.
- [PR #68090, @rhshadrach, 2026-09-05](https://github.com/pandas-dev/pandas/pull/68090#discussion_r3940814235): Can you instead compare to a hard-coded dict and drop `check_dtype=False`.
