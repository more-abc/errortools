# AGENTS_CHECK_LIST.md

> **Pre-completion verification checklist for AI coding agents working on `errortools`.**
>
> This document is the companion to [`AGENTS_PREVIEW.md`](AGENTS_PREVIEW.md).
> Use it **before** declaring a task done: tick every box that applies, explain
> any that you cannot tick, and link evidence (commands run, files touched,
> test names, etc.) in your final report.
>
> **Audience:** Cline / Cursor / Copilot / Claude Code / similar agents.
> **Maintainers:** see [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md) and
> the agent contact email in [`AGENTS_PREVIEW.md`](AGENTS_PREVIEW.md#0).
>
> > Something need change or refactor? Contact email <errortools.agent-preview@proton.me>

---

## 0. Project Snapshot (recap)

| Item | Value |
|------|-------|
| **Package name** | `errortools` |
| **Implementation package** | `_errortools/` (everything real lives here) |
| **Public re-export package** | `errortools/` — only `__init__.py` + the three lazy accessors (`future.py`, `logging.py`, `partial.py`) |
| **Python support** | `>=3.8`; type-checked against `3.13`; `3.14` wheels shipped |
| **C extension** | `_errortools/_speedup.c` → `_errortools._speedup` (optional, with pure-Python fallback) |
| **CLI entry points** | `errortools` (`_errortools/cli.py`) and `logger` (`pyproject.toml [project.scripts]`) |
| **Line length** | 120 (`pyproject.toml [tool.black]`, `.editorconfig`) |
| **Target Black version** | `py313` (`pyproject.toml [tool.black].target-version`) |
| **Style** | Google docstrings, `black` + `flake8` + `mypy` + `autoflake` + `autopep8` + `pyflakes` |
| **Test runner** | `pytest` with coverage on `_errortools/` |
| **License** | MIT |

---

## 1. Context Loading (read FIRST)

- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) end-to-end.
- [ ] Read [`README.md`](../README.md) and confirm feature surface still matches reality.
- [ ] Read [`pyproject.toml`](../pyproject.toml) (`[project]`, `[tool.black]`, `[tool.pytest.ini_options]`, `[tool.mypy]`, `[tool.setuptools.*]`).
- [ ] Read [`.flake8`](../.flake8), [`.pre-commit-config.yaml`](../.pre-commit-config.yaml), [`.editorconfig`](../.editorconfig).
- [ ] Read [`ChangeLog.md`](../ChangeLog.md) for the latest released + unreleased entries.
- [ ] Read [`errortools/__init__.py`](../errortools/__init__.py) — confirm what is publicly exported and which names go through `_DEPRECATED_NAMES`.
- [ ] Skim the existing test directory (`testing/`) to find the matching test file/area before adding a new one.
- [ ] Skim the relevant `docs/` subfolder (or the closest example) before changing public docs.

---

## 2. Code Placement & Public API

- [ ] New logic lives in **`_errortools/`**, not in `errortools/`.
- [ ] Anything new exported publicly is re-exported from [`errortools/__init__.py`](../errortools/__init__.py).
- [ ] New public symbol is added to `__all__` **alphabetically** in the appropriate bucket (functions / classes / type hints / metadata / submodules).
- [ ] If a new submodule is needed, it is registered in the lazy `__getattr__` block:
  ```python
  if name in ("future", "logging", "partial", "<new_submodule>"):
      return importlib.import_module(f"_errortools.{name}")
  ```
- [ ] Did **not** touch `errortools/` files other than `__init__.py`, `future.py`, `logging.py`, `partial.py` (no logic in the public shim).
- [ ] Did **not** edit `_errortools/__init__.py` (it is intentionally empty by design).
- [ ] If introducing a new module, set up `__all__` + a module-level docstring (Google style).

---

## 3. Backward Compatibility & Deprecation

- [ ] Did **not** remove, rename, or change the signature of any name currently in `errortools/__all__`.
- [ ] If a name must go away, route it through `_DEPRECATED_NAMES` in `errortools/__init__.py` and emit `ErrortoolsDeprecationWarning`. Do **not** silently delete it.
- [ ] The four deprecated type aliases in `_errortools/typing.py` (`InputError`, `AccessError`, `LookupError_`, `RuntimeError_`) remain functional (target removal is v5.0).
- [ ] The deprecated `fast_ignore` in `_errortools/ignore.py` still emits `DeprecationWarning` and is still re-exported.
- [ ] The deprecated name in `errortools.__all__` keeps its entry so `dir(errortools)` does not regress.
- [ ] New public behaviour is opt-in (default values preserved; no new required args without a deprecation path).

---

## 4. Style & Formatting

- [ ] All lines ≤ **120** characters (`.editorconfig`, `[tool.black] line-length = 120`).
- [ ] Code is **black**-formatted: `black .` exits 0.
- [ ] `flake8` is clean: `flake8` exits 0 (excludes `.venv`, `testing`, `__pycache__`, `htmlcov`; ignores `E203,E501,W503`; per-file ignores on `_errortools/classes/protocol.py`).
- [ ] `flake8 --doctests` is clean.
- [ ] `python -m pyflakes _errortools/` is clean.
- [ ] `autoflake --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports -r -i .` produces no remaining diff.
- [ ] `autopep8 . --recursive --in-place --pep8-passes 2000` produces no remaining diff.
- [ ] **Indentation: 4 spaces** (`.editorconfig` `[*]`).
- [ ] **End of line: LF** (`.editorconfig` `end_of_line = lf`).
- [ ] **UTF-8** encoding, no BOM (`.editorconfig charset = utf-8`).
- [ ] **Trim trailing whitespace** except in `*.md` / `*.txt` (`.editorconfig`).
- [ ] **Final newline** at EOF except where `*.md` / `*.txt` opt out.
- [ ] New public symbols have a **Google-style** docstring (Args / Returns / Raises / Example).
- [ ] Doctest-friendly `Example:` blocks render in Sphinx (no side-effects, no reliance on external state).
- [ ] New `__init__.py` or public module uses `from __future__ import annotations`.

---

## 5. Type Hints & `mypy`

- [ ] `mypy _errortools/` exits 0 with the existing flags (`warn_return_any`, `warn_unused_configs`, `warn_unused_ignores`, `python_version = "3.13"`).
- [ ] **No PEP 604 union syntax** (`X | Y`) — use `Union[X, Y]` from `typing` (3.8/3.9 compat).
- [ ] **No `match` statements** — not supported on Python 3.8.
- [ ] **No `typing.Self`** — use `from typing_extensions import Self` if truly needed; otherwise annotate the concrete return type.
- [ ] `TypeAlias` is imported from `typing` on 3.10+ and from `typing_extensions` on 3.8/3.9 (the `if sys.version_info <= (3, 10):` pattern already used in this repo).
- [ ] `disjoint_base` is imported from `typing` on 3.15+ and from `typing_extensions` otherwise.
- [ ] Reuse existing aliases (`ExceptionType`, `WarningType`, `PureBaseExceptionType`, `BaseErrorCodesType`, `AnyErrorCode`, `TracebackType`, `FrameType`) instead of redefining them.
- [ ] `# type: ignore[reason]` carries a short justification comment; prefer fixing the type instead.
- [ ] New public attributes / dunder names also appear in the `__all__` of the defining module and the public re-export.

---

## 6. Python 3.8 Compatibility

- [ ] Verified by reading the relevant control-flow constructs (no walrus operator abuse that breaks 3.8, no positional-only params without a 3.8 fallback).
- [ ] `from __future__ import annotations` is present in new files (so PEP 604 syntax in annotations is OK; runtime code still must use `Union`).
- [ ] `datetime.UTC` is gated with `if sys.version_info >= (3, 9):` (pattern already in `_errortools/logging/record.py`, `_errortools/logging/sink.py`).
- [ ] `ExceptionGroup` / `BaseExceptionGroup` / `GroupErrors` / `BaseExceptionGroupLike` / `ExceptionGroupLike` / `GroupErrorsLike` are gated with `if sys.version_info >= (3, 11):` (see `errortools/__init__.py`, `_errortools/classes/group.py`, `_errortools/classes/protocol.py`).
- [ ] `AttributeErrorLike` / `NameErrorLike` are gated with `if sys.version_info >= (3, 10):`.
- [ ] `argparse(color=True)` is gated with `if sys.version_info >= (3, 14):` (see `_errortools/cli.py:_make_parser`).

---

## 7. Performance & Hot Paths

- [ ] Any new class in `_errortools/future.py` (or other hot paths) uses `__slots__` — no per-instance `__dict__`.
- [ ] `__exit__` of `super_fast_*` / `ErrorIgnoreWrapper` is trivial: no hidden allocations, no traceback capture unless explicitly required.
- [ ] If a C speedup is added in `_errortools/_speedup.c`, the **pure-Python fallback** in the importing module is preserved and is semantically identical.
- [ ] C functions feature-gate modern CPython API (`Py_IsNone`, `Py_NewRef`, etc.) the same way `_speedup.c` does today (see header comments at the top of `_speedup.c`).
- [ ] No use of `cast(...)` in hot paths unless there is a benchmark showing the win is real.
- [ ] New performance-sensitive code is mirrored by a benchmark in `testing/benchmark/test_future_perf.py` (or a new benchmark file).

---

## 8. Tests

- [ ] Added tests in the same sub-area as the code touched:
  `_errortools/ignore.py` ↔ `testing/test_ignore.py`
  `_errortools/raises.py` ↔ `testing/test_raises.py`
  `_errortools/decorator/*` ↔ `testing/test_decorator.py`
  `_errortools/classes/*` ↔ `testing/classes/test_*.py`
  `_errortools/logging/*` ↔ `testing/logging/test_*.py`
  `_errortools/future.py` ↔ `testing/submodules/test_future.py`
  `_errortools/version.py` ↔ `testing/meta/test_version.py` + `testing/doctest/test_version.py`
  `_errortools/plugins.py` ↔ `testing/test_plugins.py`
  `_errortools/descriptor/*` ↔ `testing/test_descriptor.py`
  `_errortools/errno.py` ↔ `testing/test_errno.py`
  `_errortools/typing.py` ↔ `testing/test_typing.py`
  `testing/test_groups.py` covers `BaseGroup` / `GroupErrors`.
- [ ] Tests follow the `test_*.py` / `Test*` / `test_*` discovery rules declared in `pyproject.toml [tool.pytest.ini_options]`.
- [ ] Tests are **deterministic, fast, isolated**: no network, no `time.sleep` / `asyncio.sleep` outside a fake.
- [ ] If a doctest was added, it is collected by `pytest --doctest-modules` (the `cli-test.yml`/`run-tests.yml` jobs run this).
- [ ] Coverage is **not** disabled locally. The default `pytest` run includes `--cov=_errortools`.
- [ ] The pre-existing `filterwarnings = ["ignore::DeprecationWarning"]` is **not** relied on for new warnings. New `DeprecationWarning` subclasses are emitted explicitly.
- [ ] `pytest --doctest-modules --no-cov` exits 0 (this is what CI runs).
- [ ] For exception-collection code, cover `BaseException`-edge-cases (e.g. `KeyboardInterrupt`) only with a narrow `tuple` filter — never a bare `except:`.

---

## 9. CLI Surface

- [ ] `python -m errortools --help` renders without error.
- [ ] `python -m errortools -v/--version` prints `errortools <version>` in the same shape as `--info`.
- [ ] `python -m errortools -i/--info` exits 0.
- [ ] `python -m errortools -c/--copyrights`, `-a/--author`, `-e/--email`, `-l/--license`, `-u/--url` all exit 0.
- [ ] `python -m errortools --run-tests` exits 0 (delegates to `testing.run_tests.run_tests`).
- [ ] `python -m _errortools --debug`, `--reset`, `--check` all behave as documented.
- [ ] `logger emit --level info|debug|warning|error|critical --output stdout|stderr "msg"` emits a single log line and exits 0.
- [ ] `logger shell` launches an interactive REPL with the documented pre-imported names (`info`, `debug`, `error`, `warning`, `critical`, `trace`, `success`, `exception`, `catch`, `logger`, `Level`, `LEVELS`, `BaseLogger`, `Record`, `StreamSink`, `FileSink`, `CallableSink`, `Logger`, `Handler`, `Filter`, `Formatter`).
- [ ] The CLI dispatcher still distinguishes `errortools` vs `logger` by **basename** of `argv[0]` (with `.exe`, `.py`, `.pyw`, `.pyz`, `.sh` suffixes stripped) — paths like `/usr/bin/logger` and `my_logger_tool` do not mis-detect.
- [ ] If a new CLI flag is added, update `.github/workflows/cli-test.yml` with at least one `python -m errortools <flag>` or `logger …` invocation.
- [ ] If a new CLI flag is added, update `docs/cli_tools/index.md` with the new option/short flag, defaults, and an example.

---

## 10. Documentation (Sphinx / Read the Docs)

- [ ] `docs/conf.py` still resolves `__version_tuple__` (used for `version` / `release`).
- [ ] New public symbols are documented under `docs/api_reference/` (or the appropriate subfolder) — at minimum a one-line description.
- [ ] Non-trivial public additions have a runnable example in `docs/examples/` (the existing examples are a good template).
- [ ] When a feature is added, a `versionadded` directive is included (e.g. `.. versionadded:: 3.6`).
- [ ] When behaviour is removed, a `versionremoved` directive is included (e.g. `.. remove:: 5.0`).
- [ ] When a parameter is deprecated, a `deprecated` directive is included (e.g. `.. deprecated:: 3.0`).
- [ ] User-visible changes are reflected in `ChangeLog.md` and, when significant, in a new entry under `docs/whatsnew/`.
- [ ] `sphinx-build -b html . _build/html` (run from `docs/`) completes with no warnings that you can fix.
- [ ] `html_title`, `html_theme` (`furo`), and theme options in `docs/conf.py` are not regressed.
- [ ] If you add a `myst_enable_extensions` consumer (e.g. `tasklist`, `colon_fence`, `dollarmath`), the corresponding MyST syntax is used correctly in the new docs.
- [ ] Docstrings flagged as doctests in the source remain doctest-safe (no randomness, no real time, no network).

---

## 11. CI Workflows (`.github/workflows/`)

Each PR must keep the following green. Re-verify locally before pushing.

- [ ] `run-tests.yml` — `pytest --doctest-modules --no-cov` on Python 3.13 (Linux).
- [ ] `pep8-check.yml` — `black .` + `autopep8` (auto-fix bot) + `flake8` + `flake8 --doctests` + `pyflakes _errortools/`.
- [ ] `type-check.yml` — `mypy _errortools/`.
- [ ] `code-complexity.yml` — `flake8 --max-complexity 8 --select C901 _errortools/`.
- [ ] `cli-test.yml` — every flag exercised end-to-end.
- [ ] `autoflake-check.yml` — `autoflake --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports -r -i .` (auto-fix bot).
- [ ] `docs.yml` — `sphinx-build -b html . _build/html`.

If you changed a CI behaviour, update the corresponding workflow YAML.

---

## 12. Versioning, Changelog, Metadata

- [ ] Bumped `version` in `pyproject.toml` **and** `__version__` in `_errortools/version.py` (they must match — `__version__` flows from there into the public API).
- [ ] If you bumped, also update the `docs/whatsnew/<next>.md` file.
- [ ] Added an entry to `ChangeLog.md` (`## [Unreleased]` for not-yet-released work, or a dated `## vX.Y.Z - YYYY-MM-DD` block on release).
- [ ] `__version_info__` (the `VersionInfo` value) is consistent with `__version__` and `__version_tuple__`.
- [ ] New public names do not collide with reserved dunders (`__version__`, `__author__`, `__license__`, `__commit_id__`, `__author_email__`, `__copyright__`, `__description__`, `__title__`, `__url__`, `__fullname__`, `__signature__`, `__slug__`, `__uid__`).
- [ ] Did **not** modify or commit `pypi_token.txt` or any other secret file (per `AGENTS_PREVIEW.md` §5.8.3).

---

## 13. Issue Templates & PR Hygiene

- [ ] If the change addresses an issue, the PR description uses `Closes #N` or `Relates to #N`.
- [ ] The PR description follows `.github/PULL_REQUEST_TEMPLATE.md` (Description, Related Issues, Type of Change, Key Changes, Testing, Checklist, Additional Notes).
- [ ] The PR's "Type of Change" tick box is set; "Checklist" boxes are all ticked.
- [ ] The branch name follows the convention: `feature/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`, `perf/<name>`.
- [ ] Commits are atomic; messages are imperative-mood (`Add …`, `Fix …`, `Refactor …`).
- [ ] If you are filing a follow-up issue, used the right template under `.github/ISSUE_TEMPLATE/` (`bug_report.md`, `feature_request.md`, `docs.md`, `refactor.md`, `performance.md`, `add_label.md`) and respected `.github/ISSUE_TEMPLATE/config.yml` (no blank issues, `issue_body_requires_title: true`).
- [ ] The "Contact links" in `config.yml` (Documentation, Ask a question) were not broken by a URL change.

---

## 14. CODEOWNERS & Permission

- [ ] If you edited a path owned by `@more-abc/core-dev-team` (`/testing/`, `/_errortools/`, `/errortools/`, `/.github/`, `README.md`, `ChangeLog.md`, `pyproject.toml`, `AGENTS_PREVIEW.md`, `AUTHORS.txt`, `LICENSE.txt`, `.gitignore`), the appropriate reviewer has been requested.
- [ ] If you edited `/.editorconfig`, `/.flake8`, or `/.pre-commit-config.yaml`, the `@aiwonderland` reviewer has been requested.
- [ ] If you edited `/docs/` or `/.readthedocs.yaml`, the `@more-abc/doc` reviewer has been requested.

---

## 15. Anti-Patterns to Avoid

- [ ] No edits inside `errortools/` other than `__init__.py` and the three lazy submodule accessors.
- [ ] No `except BaseException:` (or `except:`) without an explicit narrowing tuple.
- [ ] No mutable default arguments (`def f(x=[]): …`); use `None` + sentinel.
- [ ] No silently-swallowed exceptions in new code; deliberate suppression is documented.
- [ ] No re-implementation of existing utilities (`ignore`, `retry`, `error_cache`, `ExceptionCollector`, `BaseLogger`, …) — reuse them.
- [ ] No bypassing `_DEPRECATED_NAMES` to remove a public name.
- [ ] No large diffs inside `_errortools/classes/protocol.py` (Black is configured to skip it; align manually).
- [ ] No new dependencies added to `pyproject.toml [project.dependencies]`; the project is zero-deps at runtime (`namebyauthor` and `typing_extensions` only).
- [ ] No `print(...)` left in library code paths (use `errortools.logging.logger`).
- [ ] No global mutable state added without a clear owner and tests (the only intentional globals are `_REGISTRY` in `plugins.py` and the module-level `logger` in `logging/logger.py`).
- [ ] No new top-level package; everything new lives under `_errortools/`.

---

## 16. Local Pre-Push Verification (run in order)

```bash
# 1. Install (editable + dev extras)
pip install -e .[dev]   # or: pip install -r docs/requirements.txt
pip install pytest pytest-cov black flake8 mypy autoflake autopep8 pyflakes \
            flake8-comprehensions flake8-bugbear

# 2. Static analysis & formatting
black .
flake8
flake8 --doctests
python -m pyflakes _errortools/
mypy _errortools/
flake8 --max-complexity 8 --select C901 _errortools/

# 3. Autoflake / autopep8 must be no-ops after running
autoflake --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports -r -i .
autopep8 . --recursive --in-place --pep8-passes 2000

# 4. Tests + doctests + coverage
pytest                                  # with coverage
pytest --doctest-modules --no-cov       # mirrors CI run-tests.yml

# 5. CLI smoke tests
python -m errortools --help
python -m errortools -v
python -m errortools -i
python -m errortools --run-tests
python -m _errortools --debug
python -m _errortools --check
logger emit "smoke test" --level info
logger emit "warn" --level warning --output stderr

# 6. Docs build
cd docs
sphinx-build -b html . _build/html
```

All commands above must exit `0`. If any is intentionally skipped, state the reason in your final report.

---

## 17. Final Report (include in your completion message)

- [ ] Summary of the change (1–3 sentences).
- [ ] List of files added / modified / deleted, grouped by area (`_errortools/`, `testing/`, `docs/`, `tests`, `pyproject.toml`, etc.).
- [ ] Local commands run and their exit codes (from §16).
- [ ] Any skipped checks from this list, with a one-line justification.
- [ ] Risk / compatibility notes (deprecations, new public surface, migration steps).
- [ ] Linked issue(s) and PR number (if any).
- [ ] Screenshots / sample output (only if user-facing).

---

## 18. Pointers

- Public docs: <https://errortools.readthedocs.io>
- Repo: <https://github.com/more-abc/errortools>
- Companion document: [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md)
- Maintainer guide: [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md)
- Code of conduct: [`.github/CODE_OF_CONDUCT.md`](../.github/CODE_OF_CONDUCT.md)
- Security policy: [`.github/SECURITY.md`](../.github/SECURITY.md)
- Support: [`.github/SUPPORT.md`](../.github/SUPPORT.md)
- Issue templates: [`.github/ISSUE_TEMPLATE/`](../.github/ISSUE_TEMPLATE/) (`bug_report.md`, `feature_request.md`, `docs.md`, `refactor.md`, `performance.md`, `add_label.md`)
- CI: [`.github/workflows/`](../.github/workflows/) (`run-tests.yml`, `pep8-check.yml`, `type-check.yml`, `code-complexity.yml`, `cli-test.yml`, `autoflake-check.yml`, `docs.yml`, plus auto-merge/lock helpers)

---

*Keep this file in sync with `pyproject.toml`, `_errortools/`, `errortools/__init__.py`, `.flake8`, `.pre-commit-config.yaml`, `.editorconfig`, `AGENTS_PREVIEW.md`, and `.github/` whenever those change.*
