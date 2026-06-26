# AGENTS_PREVIEW.md

> **Preview document for AI coding agents (Cline / Cursor / Copilot / Claude Code / etc.)**
> A concise, machine-oriented guide for working on the `errortools` codebase.
> For human contributors, see [`CONTRIBUTING.md`](.github/CONTRIBUTING.md).

---

## 1. Project Snapshot

| Item | Value |
|------|-------|
| **Package name** | `errortools` |
| **Description** | A toolset for working with Python exceptions, warnings, and logging. |
| **Python support** | `>=3.8`; type-checked against `3.13`; `3.14` wheels shipped. |
| **License** | MIT (see `LICENSE.txt`) |
| **Code style** | Google docstring style; `black` (line-length 120); `flake8`; `mypy`. |
| **Public surface** | `errortools/` (thin re-export) → `_errortools/` (real implementation). |

---

## 2. Repository Layout

```
errortools/
├── errortools/                  # Thin public API (re-exports only)
│   ├── __init__.py              # Aggregated __all__ + deprecation shims
│   ├── future.py / logging.py / partial.py   # Lazy submodule accessors
│
├── _errortools/                 # Real implementation (private)
│   ├── __init__.py              # Empty by design
│   ├── ignore.py                # ignore(), ignore_subclass(), ignore_warns()
│   ├── raises.py                # raises(), raises_all(), reraise(), assert_raises()
│   ├── errno.py                 # POSIX errno helpers
│   ├── future.py                # super_fast_ignore / super_fast_catch / ExceptionCollector
│   ├── plugins.py               # Plugin registry (register/get/has/...)
│   ├── typing.py                # ExceptionType / WarningType / TracebackType / ...
│   ├── metadata.py              # __author__, __copyright__, ...
│   ├── version.py               # version / commit_id / VersionInfo
│   ├── _cli.py / cli.py / __main__.py        # `logger` CLI entry point
│   ├── _logger_shell/           # Logger shell internals
│   ├── classes/                 # PureBaseException, BaseErrorCodes, warnings, ABCs, protocols
│   ├── decorator/               # suppress, convert, retry, timeout, error_cache, deprecated
│   ├── descriptor/              # ErrorMsg, NonBlankErrorMsg
│   ├── logging/                 # Structured logger (logger, sinks, formatting)
│   └── wrappers/                # Misc. wrapper utilities
│
├── testing/                     # Test suite (pytest)
│   ├── test_*.py                # Unit tests (test_ignore, test_raises, ...)
│   ├── conftest.py              # Shared fixtures
│   ├── run_tests.py             # Test runner entry point
│   ├── data/                    # Data-driven fixtures
│   ├── doctest/                 # Doctest collection
│   ├── classes/ · logging/   # Sub-suite directories
│   └── benchmark/ · meta/ · submodules/                  # Misc. test categories
│
├── docs/                        # Sphinx documentation (readthedocs.io)
│   ├── conf.py · index.md
│   ├── api_reference/ · cli_tools/ · emeps/ · examples/
│   ├── extending/ · faq/ · getting_started/ · user_guide/ · whatsnew/
│
├── .github/                     # GitHub config: workflows, issue & PR templates, ...
├── .vscode/                     # Editor settings (project-local)
├── pyproject.toml               # Build / pytest / mypy / black config
├── .flake8 · .pre-commit-config.yaml · .editorconfig
├── ChangeLog.md · README.md · AUTHORS.txt · LICENSE.txt
└── _errortools/_speedup.c       # Optional C-extension source (built into .pyd/.so)
```

> **Rule of thumb**: real logic lives in `_errortools/`. Anything new exported publicly is added to `_errortools/...` and re-exported through `errortools/__init__.py`.

---

## 3. Public API Map

### 3.1 Exception suppression & catching

| Symbol | Location | Purpose |
|--------|----------|---------|
| `ignore(*excs, default=...)` | `_errortools/ignore.py` | Context manager; rich metadata via `as`-binding. |
| `ignore_subclass(*excs)` | `_errortools/ignore.py` | Match subclasses, not the exact types. |
| `ignore_warns(...)` | `_errortools/ignore.py` | Suppress `Warning`s rather than `Exception`s. |
| `super_fast_ignore` / `super_fast_catch` / `super_fast_reraise` | `_errortools/future.py` | Zero-overhead, `__slots__`-only context managers; optionally backed by C extension `_errortools._speedup`. |
| `ExceptionCollector` | `_errortools/future.py` | Collect N exceptions → raise as `ExceptionGroup`. |

### 3.2 Raising & conversion

| Symbol | Location | Purpose |
|--------|----------|---------|
| `raises(exc, /, *, condition=True)` | `_errortools/raises.py` | One-shot raise helper. |
| `raises_all(*exc)` | `_errortools/raises.py` | Raise several exceptions as a group. |
| `assert_raises(exc, /, *, condition=True)` | `_errortools/raises.py` | `assert`-style raise. |
| `reraise(*exc)` | `_errortools/raises.py` | Re-raise the current exception as the first matching type. |
| `@suppress(*exc, default=...)` | `_errortools/decorator/handlers.py` | Decorator form of suppression. |
| `@convert(*exc, ...)` | `_errortools/decorator/handlers.py` | Convert caught exception types. |

### 3.3 Decorators

| Symbol | Location | Purpose |
|--------|----------|---------|
| `@retry(times=, on=, delay=, ...)` | `_errortools/decorator/retry.py` | Retry on failure with backoff. |
| `@timeout(seconds)` | `_errortools/decorator/timeout.py` | Async/sync timeout (note: implementation lives in `_errortools/decorator/`). |
| `@error_cache(maxsize=)` | `_errortools/decorator/cache.py` | LRU cache that only memoizes *successful* calls. |
| `@deprecated(...)` · `@experimental(...)` | `_errortools/decorator/deprecated.py` | Emit warnings at call time. |

### 3.4 Custom exceptions, codes & warnings

| Symbol | Location | Purpose |
|--------|----------|---------|
| `PureBaseException` | `_errortools/classes/errorcodes.py` | Base class with `code` and `default_detail`. |
| `ContextException` | `_errortools/classes/errorcodes.py` | Carries structured context (`.with_context(**k)`). |
| `BaseErrorCodes` | `_errortools/classes/errorcodes.py` | Code registry; sub-classes like `InvalidInputError`, `NotFoundError`, `AccessDeniedError`, `ConfigurationError`, `RuntimeFailure`, `TimeoutFailure`. |
| `BaseWarning` family | `_errortools/classes/warn.py` | `DeprecatedWarning`, `PerformanceWarning`, `ResourceUsageWarning`, `RuntimeBehaviourWarning`, `ConfigurationWarning`. |
| `Error` / ABCs / protocols | `_errortools/classes/abc.py`, `classes/protocol.py` | Structural typing helpers (`ExceptionLike`, etc.). |
| `ErrorMsg`, `NonBlankErrorMsg` | `_errortools/descriptor/` | Descriptor-based non-empty message validation. |

### 3.5 Logging

| Symbol | Location | Purpose |
|--------|----------|---------|
| `errortools.logging.logger` | `_errortools/logging/` | Structured logger with sinks, rotation, retention, formatting, and `logger.catch()` context. |
| `logger` CLI | `_errortools/_cli.py` | `pip install errortools` exposes a `logger` console script. |

### 3.6 Plugins

| Symbol | Location | Purpose |
|--------|----------|---------|
| `register / get / has / list_all / run / remove / clear / Registry` | `_errortools/plugins.py` | Tiny in-process plugin registry; accessible at top level via `errortools.plugins.<name>`. |

### 3.7 Misc. / metadata

| Symbol | Location | Purpose |
|--------|----------|---------|
| `__version__`, `version_tuple`, `commit_id`, `VersionInfo` | `_errortools/version.py` | Version introspection. |
| `get_errno_message` / `get_errno_name` / `get_all_errno_codes` / `is_valid_errno` | `_errortools/errno.py` | POSIX errno helpers. |
| `AnyErrorCode`, `BaseErrorCodesType`, `PureBaseExceptionType`, `ContextExceptionType`, `ExceptionType`, `WarningType`, `TracebackType`, `FrameType` | `_errortools/typing.py` | Public type aliases. |

---

## 4. Build, Test, and Quality Commands

All commands assume the repo root and an activated virtualenv (`.venv`).

```bash
# Install (editable + dev extras)
pip install -e .[dev]

# Format
black .

# Lint
flake8

# Type check (configured for Python 3.13)
mypy

# Run the test suite with coverage (see pyproject.toml [tool.pytest.ini_options])
pytest

# Build C extension in place (optional; falls back to pure Python if absent)
python -c "from _errortools._speedup import fast_append_exception"   # smoke test
```

CI workflows (see `.github/workflows/`) re-run these on every PR:
`run-tests.yml`, `pep8-check.yml`, `type-check.yml`, `code-complexity.yml`, `cli-test.yml`, `autoflake-check.yml`, `docs.yml`.

---

## 5. Conventions for AI Agents

> These rules are derived from the codebase, `pyproject.toml`, `.flake8`, `.pre-commit-config.yaml`, `.editorconfig`, and `CONTRIBUTING.md`. Follow them unless the user explicitly says otherwise.

### 5.1 General

1. **Never modify `dist/`, `*.egg-info/`, `htmlcov/`, `.mypy_cache/`, `.pytest_cache/`, or `.venv/`.** They are generated.
2. **Prefer the public API**: changes to `_errortools/` are fine; user-facing symbols must be re-exported in `errortools/__init__.py` and listed in `__all__`.
3. **Keep backward compatibility**. Deprecated names go through `_DEPRECATED_NAMES` in `errortools/__init__.py`, **never delete exported symbols outright**.
4. **Python 3.8 compatibility is mandatory**: no `match` statements, no PEP 604 union syntax (`Union[X, Y]`), no `Self` from `typing`. Use `Optional`, `Union` from `typing`, and import modern syntax from `typing_extensions` if needed.
5. **Use `from __future__ import annotations` in new files** to keep annotations lazy.
6. **Google-style docstrings** on every public symbol. Include an `Example:` block (doctest-friendly) where reasonable.

### 5.2 Style

1. **Line length: 120** (`[tool.black] line-length = 120`).
2. **`target-version = ["py313"]`** for Black formatting decisions; ignore `_errortools/classes/protocol.py` (extend-exclude).
3. **`flake8`** is configured in `.flake8` — keep it clean.
4. **Pre-commit hooks** run Black, Flake8, autoflake, and standard hygiene checks; mirror them locally before pushing.

### 5.3 Imports & layout

1. New modules belong under `_errortools/<feature>/`.
2. Submodules accessed lazily from `errortools/__init__.py` via the existing `__getattr__` pattern:
   ```python
   if name in ("future", "logging", "partial"):
       return importlib.import_module(f"_errortools.{name}")
   ```
3. **Always sort `__all__`** (the existing lists are alphabetical). Append new exports in the right bucket (functions / classes / type hints / metadata / submodules).

### 5.4 Typing

1. `mypy` is configured with `python_version = "3.13"`, `warn_return_any`, `warn_unused_configs`, `warn_unused_ignores`. Honour these flags.
2. Reuse existing type aliases (`ExceptionType`, `WarningType`, `PureBaseExceptionType`, `BaseErrorCodesType`, `AnyErrorCode`, `TracebackType`, `FrameType`) instead of redefining them.
3. Add `# type: ignore[reason]` only with a justification comment, and prefer fixing the type.

### 5.5 Tests

1. Tests live in `testing/` and are picked up by the `test_*.py` / `Test*` / `test_*` discovery rules.
2. Add tests in the same sub-area as the code you touched (`testing/test_ignore.py` ↔ `_errortools/ignore.py`, etc.). New subareas get a new file or a new subdirectory mirroring `_errortools/`.
3. Tests should be deterministic, fast, and isolated; do **not** introduce network, sleep, or wall-clock dependencies unless wrapping them with a fake.
4. The default pytest run includes coverage on `_errortools` and emits both terminal and HTML reports. Don't disable coverage locally unless debugging.
5. `filterwarnings = ["ignore::DeprecationWarning"]` is set globally — avoid relying on it for new warnings; emit specific `DeprecationWarning` subclasses instead.

### 5.6 Performance-sensitive code

1. `super_fast_*` classes in `_errortools/future.py` and other hot paths use `__slots__`; do not add instance dicts or `__dict__`.
2. The optional `_errortools/_speedup.c` provides C-accelerated helpers (`fast_append_exception`, `fast_suppress_exit`). A pure-Python fallback exists for every C function — never break it.
3. Avoid hidden allocations in `__exit__` of `super_fast_*`; keep them trivial.

### 5.7 Documentation

1. Sphinx lives under `docs/`. New public symbols need a corresponding entry under `docs/api_reference/` (or the appropriate subfolder) and at least one example in `docs/examples/` if non-trivial.
2. User-visible changes go into `ChangeLog.md` and, when significant, `docs/whatsnew/`.
3. Docstrings render in Sphinx — keep them clean, doctest-safe where marked.

### 5.8 Git & PR hygiene

1. Branch names: `feature/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`, `perf/<name>`.
2. One logical change per commit; imperative-mood messages.
3. Never commit secrets. `pypi_token.txt` is local-only and must not be modified by agents.
4. Respect `.github/CODEOWNERS` and `.github/PULL_REQUEST_TEMPLATE.md`.

---

## 6. Common Tasks — Cheat Sheet

| Goal | Where to edit | Don't forget |
|------|---------------|--------------|
| Add a public helper | `_errortools/<file>.py` + re-export in `errortools/__init__.py` | Add to `__all__` (alphabetical). |
| Add a new exception code | Subclass `BaseErrorCodes` in `_errortools/classes/errorcodes.py` | Pick a unique numeric `code`, set `default_detail`. |
| Add a new decorator | `_errortools/decorator/<name>.py` | Preserve signature via `functools.wraps`; add `__all__`. |
| Add a new warning | `_errortools/classes/warn.py` | Inherit from `BaseWarning`. |
| Add a logging sink/feature | `_errortools/logging/` + docs in `docs/user_guide/` | Keep the public surface backwards-compatible. |
| Speed up a hot path | Use `_errortools/_speedup.c` + a pure-Python fallback | Keep the fallback behaviour identical. |
| Bump version | `pyproject.toml` (`version = "..."`) and `_errortools/version.py` | Update `ChangeLog.md`. |

---

## 7. Anti-patterns to Avoid

- ❌ Editing anything under `errortools/` **except** `__init__.py` and the three lazy submodule accessors (`future.py`, `logging.py`, `partial.py`).
<!-- - ❌ Using `Union[X, None]` in public type hints (project supports Python 3.8). -->
- ❌ Catching `BaseException` indiscriminately — narrow with explicit tuples.
- ❌ Adding mutable default arguments; use `None` + sentinel.
- ❌ Swallowing exceptions silently in new code; document any deliberate suppression.
- ❌ Re-implementing existing utilities (`ignore`, `retry`, `error_cache`, `ExceptionCollector`, …) — reuse them.
- ❌ Bypassing `_DEPRECATED_NAMES` to remove a public name.
- ❌ Generating large diffs in `_errortools/classes/protocol.py` — Black is configured to skip it; align manually.

---

## 8. Quick Verification Checklist (run before finishing)

```bash
black .
flake8
mypy
pytest
```

All four should exit `0`. If a step is intentionally skipped, state the reason in your final message.

---

## 9. Pointers

- **Public docs**: <https://errortools.readthedocs.io>
- **Repo**: <https://github.com/more-abc/errortools>
- **Issue templates**: `.github/ISSUE_TEMPLATE/` (bug, feature, docs, refactor, performance, label)
- **CI**: `.github/workflows/` (run-tests, pep8-check, type-check, code-complexity, autoflake-check, cli-test, docs)
- **Code of conduct**: `.github/CODE_OF_CONDUCT.md`
- **Security policy**: `.github/SECURITY.md`
- **Support**: `.github/SUPPORT.md`

---

*Keep this file in sync with `pyproject.toml`, `_errortools/`, `errortools/__init__.py`, and `CONTRIBUTING.md` whenever those change.*
