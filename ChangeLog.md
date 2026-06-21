# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]


## v3.5.3 - 2026-06-21
- Add `# type: ignore[no-any-return]` in `_errortools/version.py` line 92 (in `VersionInfo.__ne__`, commit 7e0a72)

## v3.5.2 - 2026-06-21
- Fix `VersionInfo.__ne__` return type error by mypy (In github workflows)

## v3.5.1 - 2026-06-21
- Rename `_get_version_tuple` function in `_errortools/version.py` to `get_version_tuple` and add it to the public API.
- Add new class `VersionInfo` in `_errortools/version.py`.
- Add comprehensive tests for `VersionInfo` and `get_version_tuple` in `testing/meta/test_version.py` (43 new tests covering construction, `from_str`, `to_tuple`, dunder methods, equality, ordering, sorting, and public-API exposure).
- Add a dedicated doctest module `testing/doctest/test_version.py` with 55 doctests that double as runnable documentation for `VersionInfo` and `get_version_tuple`.
- Use `typing.Final` in `_errortools/version.py`.

## Release v3.5.0 - 2026-06-20
- Release 3.5.0

## v3.4.11 - 2026-06-19
- Refactor type hints of `fast_append_exception` and `fast_suppress_exit` in `_errortools/future.py`.

## v3.4.10 - 2026-06-19
- Refactor and improve compatibility in `_errortools/_speedup.c`.

## v3.4.9 - 2026-06-14
- Refactor `_errortools/cli.py` to improve robustness, structure and consistency.
- Replace fragile `"logger" in sys.argv[0]` substring test with a basename-based `_detect_mode()` helper (handles `.exe`, `.py`, `.pyw`, `.pyz`, `.sh` suffixes) so paths like `my_logger_tool` or `/usr/bin/logger` no longer mis-detect the CLI family.
- Cache the detected mode at import time as `_CLI_MODE: Final[str]` instead of recomputing on every call.
- Split `parse_args()` into `_build_errortools_parser()` and `_build_logger_parser()` so each CLI family owns its own argument schema.
- Extract `_make_parser(prog, description)` helper to deduplicate the Python 3.14+ `color=True` branch.
- Replace `args.message == "shell"` dispatch anti-pattern with `args.subcmd` checks plus a defensive fallback branch.
- Split each `--*` flag action into its own named function (`_show_version`, `_show_author`, …) and mark `_FLAG_ACTIONS` as `Final`.
- Unify `--version` output (`errortools 3.4.9`) with the format already used by `--info`.
- Add a friendly `ImportError` handler for `--run-tests` so missing test extras produce an actionable message and exit code 2 instead of a traceback.
- Switch `parse_args`/`main` signatures to `Sequence[str] | None` for broader caller compatibility and enable `from __future__ import annotations` for PEP 604 syntax on Python 3.8+.
- Add module-level docstring documenting both CLI families.

## v3.4.8 - 2026-06-13
- Add example cli in `_errortools/version.py`, `_errortools/metadata.py` and `_errortools/plugins.py`.

## v3.4.7 - 2026-06-13
- Change format of `_errortools/classes/protocol.py` back to black's format.

## v3.4.6 - 2026-06-12
- Add more comments in `_errortools/ignore.py`.

## v3.4.5 - 2026-06-12
- Improve compatibility in `errortools/__init__.py` to Python 3.10 (for `NameErrorLike` and `AttributeErrorLike` compatibility).

## v3.4.4 - 2026-06-12
- Fix flake8 error W504 and E704 in `_errortools/classes/protocol.py`.
- Fix flake8 error B042 in `_errortools/classes/group.py`.
- Fix flake8 error B027 in `_errortools/logging/sink.py`.

## v3.4.3 - 2026-06-12
- Fix flake8 W504 error in `_errortools/classes/protocol.py`.

## v3.4.2 - 2026-06-12
- Add interactive `logger shell` REPL with pre-imported logging shortcuts and std-lib logging base classes.

## v3.4.1 - 2026-06-11
- Add remove time in deprecated 4 type alias in `_errortools/typing.py`.

## Release v3.4.0 - 2026-06-09
- Release 3.4.0

## v3.3.6 - 2026-06-08
- Optimize `_errortools/classes/protocol.py`: fix `__all__` on Python < 3.11, remove dead code, and expand docstrings.

## v3.3.5 - 2026-06-07
- Fix `get()` sentinel bug so `default=None` is correctly honored.
- Add `has()`, `clear()`, and `Registry.remove()` to plugin system.
- Improve test coverage for `_errortools/plugins.py`.

## v3.3.4 - 2026-06-06
- Set `logger`'s floor level to `Level.TRACE` (the lowest level).

## v3.3.3 - 2026-06-06
- Fix #53 to import `_check_methods` from `_collections_abc` module in `_errortools/classes/abc.py`.

## v3.3.2 - 2026-06-05
- Fixed flake8 F401 error in `errortools/__init__.py`.

## v3.3.1 - 2026-06-05
- Improve compatibility in `errortools/__init__.py` to Python 3.11 (for `ExceptionGroup` compatibility).

## Release v3.3.0 - 2026-06-02
- Release 3.3.0

## v3.2.6 - 2026-06-01
- Deleted the 4 constants in `_errortools/const.py`.
- Deleted tests for `_errortools/const.py`.

## v3.2.5 - 2026-05-31
- Add `.. versionadded:: 3.2` in `_errortools/plugin.py`.

## v3.2.4 - 2026-05-31
- Add ultra-lightweight plugin system in `_errortools/plugins.py`.
- Expose plugin APIs to top-level errortools module.
- Add complete test suite for plugin system in `tests/test_plugins.py`.

## v3.2.3 - 2026-05-30
- Fix max complexity error in `classes/protocol.py`.

## v3.2.2 - 2026-05-30
- Add `ErrortoolsDeprecationWarning` warning class.
- Now the deprecated features will warn `ErrortoolsDeprecationWarning`.

## v3.2.1 - 2026-05-30
- Add 14 protocol classes about exceptions (like `ExceptionLike`, `ImportErrorLike`, `ExceptionGroupLike`).
- Add tests for protocol classes (`test_protocols.py`).

## Release v3.2.0 - 2026-05-29
- Release 3.2.0

## v3.1.12 - 2026-05-28
- Add `__getattr__` to `errortools/__init__.py` for lazy-loading submodules (`future`, `logging`, `partial`).
- Deprecated aliases (`fast_ignore`, `InputError`, `AccessError`, `LookupError_`, `RuntimeError_`) now emit `DeprecationWarning` on access.
- Add `__dir__` to `errortools/__init__.py` so `dir(errortools)` includes all public names.

## v3.1.11 - 2026-05-28
- Use autoflake to fix errors in `_errortools/classes/abc.py`.

## v3.1.10 - 2026-05-28
- Useing `flake8-comprehensions` and `flake8-bugbear` plugins in flake8.

## v3.1.9 - 2026-05-28
- Add function `_get_version_tuple` to get the `__version_tuple__` var in `_errortools/version.py`.

## v3.1.8 - 2026-05-24
- Split CLI: `python -m errortools` (public) and `python -m _errortools` (debug).
- Add `--debug`, `--reset`, `--check`, `--list-features` to private debug CLI.

## v3.1.7 - 2026-05-24
- Move `timeout` decorator to `_errortools/decorator/timeout.py`.
- Move `retry` decorator to `_errortools/decorator/retry.py`.
- `_errortools/ignore.py` now re-exports from new locations for backwards compatibility.

## v3.1.6 - 2026-05-24
- Add `suppress` and `convert` decorators in `_errortools/decorator/handlers.py`.
- Add tests for `suppress` and `convert` in `testing/test_decorator.py`.

## v3.1.5 - 2026-05-24
- Add `fast_suppress_exit` C function in `_errortools/_speedup.c` for optimized `__exit__` calls.
- Optimize `super_fast_ignore` to use `fast_suppress_exit`, removing `cast` overhead.
- Optimize `super_fast_catch.__exit__` with inline short-circuit check.
- Remove `cast` call in `ExceptionCollector.raise_all`.
- Add performance tests in `testing/benchmark/test_future_perf.py`.

## v3.1.4 - 2026-05-24
- Add `BaseDescriptor` base class in `_errortools/descriptor/base.py` for shared descriptor logic.
- Refactor `ErrorMsg` and `NonBlankErrorMsg` to inherit from `BaseDescriptor`.
- Add tests for `BaseDescriptor` in `testing/test_descriptor.py`.

## v3.1.3 - 2026-05-23
- Reduce cyclomatic complexity of `main()` in `_errortools/cli.py` (C901).
- Reduce cyclomatic complexity of `retry.__call__` in `_errortools/ignore.py` (C901).

## v3.1.2 - 2026-05-23
- Changed `except ValueError, OSError:` to `except (ValueError, OSError):` at `_errortools/errno.py` line 85.

## v3.1.1 - 2026-05-23
-  Changed `except AttributeError, TypeError:` to `except (AttributeError, TypeError):` at `_errortools/errno.py` line 52.

## Release v3.1.0 - 2026-05-22
- Release 3.1.0

## v3.0.4 - 2026-05-05
- Deprecated `fast_ignore` in `_errortools/ignore.py`.

## v3.0.3 - 2026-05-05
- Deprecated 4 type alias in `_errortools/typing.py`.

## v3.0.2 - 2026-05-04
- ~~Let mypyc OK.~~ Now use mypyc now.

## v3.0.1 - 2026-05-04
- Optimize exception handling functions in _speedup.c

## Release v3.0.0 - 2026-05-03
- Fix flake8 error F811 in `_errortools/wrappers/cache.py`.
- Fix flake8 error W293 in `_errortools/wrappers/ignore.py`.

## v2.5.5 - 2026-05-03
- Improve compatibility for `TypeAlias` across Python 3.8 to 3.15 in some files.

## v2.5.4 - 2026-05-02
- Delete 4 classes in `/methods`.
- Delete 1 class in `classes/abc.py`.
- Delete tests for 5 delete classes.

## v2.5.3 - 2026-05-02
- Fix type error by mypy in `future.py`.

## v2.5.2 - 2026-05-02
- Add C extension module `_speedup` for performance optimization in `future.py`.
- Optimize exception type checking (`issubclass`) and list append operations with C implementation
- Automatic fallback to pure Python when C extension is unavailable.

## v2.5.1 - 2026-05-01
- Improve compatibility across Python 3.8 to 3.15.

## Release v2.5.0 - 2026-05-01
- Release 2.5.0

## v2.4.4 - 2026-04-30
- Add Python 3.15 compatibility for `disjoint_base` imports by using `typing` on 3.15+ and `typing_extensions` on earlier versions.
- Update packaging metadata for v2.4.4, including Python 3.15 classifier support and conditional dependency handling in ~~`setup.py`~~`pyproject.toml`.

## v2.4.3 - 2026-04-25
- Show log level icons in default logging output.
- Fix logging file tests on Windows by reading UTF-8 log files explicitly.

## v2.4.2 - 2026-04-25
- Add logging submodule in errortools module.
- Add future submodule in errortools module.
- Add partial submodule in errortools module.
- Add type hints in `_errortools/partial.py`.

## v2.4.1 - 2026-04-25
- `experimental` decorator now warns `FutureWarning`.

## Release v2.4.0 - 2026-04-23
- Release 2.4.0

## v2.3.5 - 2026-04-23
- Add docstring in `_errortools/errno.py`.

## v2.3.4 - 2026-04-22
- Add lightweight exception handling utilities to `_errortools/future.py`:
  - `super_fast_ignore`: Ultra-lightweight context manager to suppress exceptions
  - `super_fast_catch`: Ultra-lightweight context manager to catch and store exceptions
  - `super_fast_reraise`: Ultra-lightweight context manager to convert exception types
  - `ExceptionCollector`: Batch exception collection for bulk operations with support for error grouping
- Add comprehensive test suite for future utilities (36 tests)

## v2.3.3 - 2026-04-19
- Refactor and optimize `_errortools/errno.py`.
- Change `tests/test_errno.py` to refactor version.

## v2.3.2 - 2026-04-19
- Use `typing.Final` in `_errortools/logging/level.py`.

## v2.3.1 - 2026-04-19
- Use `typing.Final` in `_errortools/const.py`.

## Release v2.3.0 - 2026-04-19
- Release 2.3.0

## Previous releases
Prior to release 2.3.0 we did not provide a changelog. Please check the Git history for details.
