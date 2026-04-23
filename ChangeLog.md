# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
