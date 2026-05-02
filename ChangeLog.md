# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## v2.5.2 - 2026-05-02
- Add C extension module `_speedup` for performance optimization in `future.py`
- Optimize exception type checking (`issubclass`) and list append operations with C implementation
- Automatic fallback to pure Python when C extension is unavailable

## v2.5.1 - 2026-05-01
- Improve compatibility across Python 3.8 to 3.15.

## v2.5.0 - 2026-05-01
- Release 2.5.0

## v2.4.4 - 2026-04-30
- Add Python 3.15 compatibility for `disjoint_base` imports by using `typing` on 3.15+ and `typing_extensions` on earlier versions.
- Update packaging metadata for v2.4.4, including Python 3.15 classifier support and conditional dependency handling in `setup.py`.

## v2.4.3 - 2026-04-25
- Show log level icons in default logging output.
- Fix logging file tests on Windows by reading UTF-8 log files explicitly.

## v2.4.2 - 2026-04-25
- Add logging submodule im errortools module.
- Add future submodule im errortools module.
- Add partial submodule im errortools module.
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
- Refactor and optimize _errortools/errno.py.
- Change tests/test_errno.py to refactor version.

## v2.3.2 - 2026-04-19
- Use `typing.Final` in _errortools/logging/level.py.

## v2.3.1 - 2026-04-19
- Use `typing.Final` in _errortools/const.py.

## Release v2.3.0 - 2026-04-19
- Release 2.3.0

## Previous releases
Prior to release 2.3.0 we did not provide a changelog. Please check the Git history for details.
