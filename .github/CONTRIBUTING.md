# Contributing to errortools

Thank you for your interest in contributing to **errortools** — a toolset for
working with Python exceptions, warnings, and logging. We welcome bug reports,
documentation improvements, feature requests, refactors, performance work, and
code submissions from the community.

> Something needs to change or be refactored? Contact email
> <errortools.docs@proton.me>

Before you start, please skim these three documents — they are the source of
truth that this guide points at:

| Document | Why read it |
|----------|-------------|
| [`PHILOSOPHY.md`](../PHILOSOPHY.md) | The *why* — the values, tradeoffs, and opinions that shape every design decision. |
| [`.agents/AGENTS_PREVIEW.md`](../.agents/AGENTS_PREVIEW.md) | The project snapshot: layout, public API map, conventions, anti-patterns. |
| [`.agents/AGENTS_CHECK_LIST.md`](../.agents/AGENTS_CHECK_LIST.md) | The pre-completion verification gate (style, typing, tests, CLI, docs, CI, version, anti-patterns). |
| [`.agents/skills/`](../.agents/skills/) | Reusable, task-shaped playbooks (e.g. *add a public symbol*, *bump version*, *write tests*). |

---

## Table of contents

- [Code of conduct](#code-of-conduct)
- [Project at a glance](#project-at-a-glance)
- [Getting started](#getting-started)
- [Reporting issues](#reporting-issues)
- [Submitting changes](#submitting-changes)
- [Style and quality bar](#style-and-quality-bar)
- [Pull request guidelines](#pull-request-guidelines)
- [Code review process](#code-review-process)
- [Release and versioning](#release-and-versioning)
- [For AI coding agents](#for-ai-coding-agents)
- [Where to get help](#where-to-get-help)

---

## Code of conduct

We are committed to a welcoming and inclusive environment. Please be respectful
to all contributors and community members. The full expectations, examples of
unacceptable behaviour, and reporting process are in
[`.github/CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

---

## Project at a glance

| Item | Value |
|------|-------|
| **Package name** | `errortools` |
| **License** | MIT (see [`LICENSE.txt`](../LICENSE.txt)) |
| **Python support** | `>=3.8`; type-checked against 3.13; 3.14 wheels shipped |
| **Runtime dependencies** | Exactly two: `namebyauthor==1.2.0`, `typing_extensions>=4.16.0` |
| **Code style** | Google docstrings; `black` (line-length 120); `flake8`; `mypy` |
| **Layout** | Two-package: `errortools/` (thin public re-export) → `_errortools/` (real implementation) |
| **CLI** | `python -m errortools …` and `logger …` (console script from `[project.scripts]`) |
| **Test runner** | `pytest` with coverage on `_errortools/` |
| **Optional C extension** | `errortools_speedbelt._speedup` / `._ignore_speed` — pure-Python fallback is always present |

For a deeper orientation, see
[`.agents/AGENTS_PREVIEW.md`](../.agents/AGENTS_PREVIEW.md) §1 and §2.

---

## Getting started

### Prerequisites

- Python **3.8** or newer (the project is tested on 3.8 through 3.14).
- Git.
- A GitHub account.

### Set up your development environment

```bash
# 1. Fork and clone
git clone https://github.com/more-abc/errortools.git
cd errortools

# 2. Create and activate a virtualenv
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows (cmd.exe):
.venv\Scripts\activate.bat
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3. Install in editable mode with dev extras
pip install -e .[dev]

# 4. (Optional) Install the extra lint tools referenced in CI
pip install pytest pytest-cov black flake8 mypy autoflake autopep8 pyflakes \
            flake8-comprehensions flake8-bugbear
```

> **Tip.** The CI workflows under `.github/workflows/` are the source of truth
> for *exactly* which commands must pass. The list at
> [`.agents/AGENTS_CHECK_LIST.md` §16](../.agents/AGENTS_CHECK_LIST.md#16-local-pre-push-verification-run-in-order)
> mirrors them and is the most reliable copy-pasteable checklist.

---

## Reporting issues

Blank issues are disabled (see `.github/ISSUE_TEMPLATE/config.yml`). Please
pick the template that matches what you want to report:

| Template | Use it for |
|----------|------------|
| [`.github/ISSUE_TEMPLATE/bug_report.md`](ISSUE_TEMPLATE/bug_report.md) | A reproducible bug in `errortools`. |
| [`.github/ISSUE_TEMPLATE/feature_request.md`](ISSUE_TEMPLATE/feature_request.md) | A new capability, public symbol, or CLI flag. |
| [`.github/ISSUE_TEMPLATE/refactor.md`](ISSUE_TEMPLATE/refactor.md) | A code-structure, readability, or maintainability improvement. |
| [`.github/ISSUE_TEMPLATE/performance.md`](ISSUE_TEMPLATE/performance.md) | A slowness, memory, or allocation regression. |
| [`.github/ISSUE_TEMPLATE/docs.md`](ISSUE_TEMPLATE/docs.md) | Missing, wrong, or unclear documentation. |
| [`.github/ISSUE_TEMPLATE/add_label.md`](ISSUE_TEMPLATE/add_label.md) | A proposal to add or update a label taxonomy. |

For everything else, start a thread in
[GitHub Discussions](https://github.com/more-abc/errortools/discussions).

### Bug reports — please include

- Python version, OS, and `errortools` version (`python -m errortools --version`).
- Minimal steps to reproduce (ideally a self-contained script).
- Expected vs. actual behaviour.
- Full traceback and any logs.

### Security issues

**Do not** file public issues for security vulnerabilities. Follow
[`.github/SECURITY.md`](SECURITY.md) and contact
<errortools-security@proton.me> privately, or open a GitHub Security
Advisory.

---

## Submitting changes

### 1. Pick a branch name

Branches follow the convention `type/<name>`, where `type` is one of:

```text
feature/<name>    new user-visible functionality
fix/<name>        bug fix
refactor/<name>   code structure / readability
docs/<name>       documentation only
perf/<name>       performance improvement
```

Example:

```bash
git checkout -b feature/exception-collector-benchmark
```

### 2. Make your change

- Read [`PHILOSOPHY.md`](../PHILOSOPHY.md) and
  [`.agents/AGENTS_PREVIEW.md`](../.agents/AGENTS_PREVIEW.md) before you start.
- Place logic in `_errortools/`. The public `errortools/` package is a
  re-export shim — do not add logic there except in `__init__.py` and the
  three lazy submodule accessors (`future.py`, `logging.py`, `partial.py`).
- Match the existing module style (Google docstrings, type hints,
  `from __future__ import annotations`, no PEP 604 union syntax in runtime
  code — the project supports Python 3.8).
- Keep changes atomic; one logical change per commit.
- Write commit messages in the imperative mood (`Add …`, `Fix …`,
  `Refactor …`).
- **Never** commit secrets. `pypi_token.txt` and similar credentials are
  local-only.

### 3. Add tests

Tests live under `testing/` and follow the project's pytest discovery
rules (`test_*.py` files, `Test*` classes, `test_*` functions). The rule
of thumb is one concept per file — mirror the source path:

| Source | Test file |
|--------|-----------|
| `_errortools/ignore.py` | `testing/test_ignore.py` |
| `_errortools/raises.py` | `testing/test_raises.py` |
| `_errortools/future.py` | `testing/submodules/test_future.py` |
| `_errortools/decorator/*` | `testing/test_decorator.py` |
| `_errortools/classes/*` | `testing/classes/test_*.py` |
| `_errortools/logging/*` | `testing/logging/test_*.py` |
| `_errortools/version.py` | `testing/meta/test_version.py` + `testing/doctest/test_version.py` |
| `_errortools/plugins.py` | `testing/test_plugins.py` |
| `_errortools/descriptor/*` | `testing/test_descriptor.py` |
| `_errortools/errno.py` | `testing/test_errno.py` |
| `_errortools/typing.py` | `testing/test_typing.py` |
| `BaseGroup` / `GroupErrors` | `testing/test_groups.py` |
| data-driven helpers | `testing/test_data_driven.py` |

Tests must be deterministic, fast, and isolated: no network, no real
`time.sleep` / `asyncio.sleep`, no reliance on wall-clock. If you add a
doctest, it is collected by `pytest --doctest-modules` in CI. See
[`.agents/skills/write-tests.md`](../.agents/skills/write-tests.md) for
the full playbook.

### 4. Add a reproducer for bug fixes

If your PR fixes a bug, the workflow is:

1. Before the fix, add a self-contained reproducer under
   `reproduce/sandbox/reproduce_issue_<N>.py` (where `<N>` is the GitHub
   issue number). See [`reproduce/sandbox/README.md`](../reproduce/sandbox/README.md)
   for the naming convention.
2. Promote the reproducer body into the matching test under
   `testing/<area>/test_<file>.py`.
3. Mark both items in the PR template.

This guarantees the bug is reproducible from a fresh clone before the fix
lands, and that the regression is locked in afterwards.

### 5. Add a newsfragment for user-visible changes

For any user-visible change (new public symbol, behaviour change, bug
fix, performance improvement, deprecation), add a one-line newsfragment:

```text
reproduce/changelog/<PR>.<type>.md
```

where `<PR>` is the GitHub PR number and `<type>` is one of:

```text
bug        feature      performance
refactor   deprecation  docs
```

Example: `reproduce/changelog/123.performance.md`

```markdown
<!-- 123.performance.md -->
[#123](https://github.com/more-abc/errortools/issues/123) Avoid re-allocating `Record.extras` in `BaseLogger.info` hot path.
```

On release, newsfragments are folded into `ChangeLog.md` and the file is
moved to `reproduce/used_changelog/`. See
[`reproduce/changelog/README.md`](../reproduce/changelog/README.md).

### 6. Update documentation

When you change public behaviour, update:

- The docstring of the affected symbol (Google style, with an
  `Example:` block where reasonable).
- A one-line entry under `docs/api_reference/` (or the closest
  user-guide page).
- A runnable example under `docs/examples/` if the change is non-trivial.
- A `versionadded` / `versionchanged` / `deprecated` / `versionremoved`
  directive as appropriate.
- `ChangeLog.md` (under `## [Unreleased]` for in-flight work, or under a
  dated block on release).

### 7. Run every quality check locally

Before pushing, every command below must exit `0`:

```bash
# Static analysis and formatting
black .
flake8
flake8 --doctests
python -m pyflakes _errortools/
mypy _errortools/
flake8 --max-complexity 8 --select C901 _errortools/

# Autoflake / autopep8 must be no-ops after running once
autoflake --remove-all-unused-imports --remove-unused-variables \
          --ignore-init-module-imports -r -i .
autopep8 . --recursive --in-place --pep8-passes 2000

# Tests + doctests + coverage
pytest                              # with coverage on _errortools
pytest --doctest-modules --no-cov   # mirrors CI run-tests.yml

# CLI smoke tests
python -m errortools --help
python -m errortools -v
python -m errortools -i
python -m errortools --run-tests
python -m _errortools --debug
python -m _errortools --check
logger emit "smoke test" --level info
logger emit "warn" --level warning --output stderr

# Docs build
cd docs && sphinx-build -b html . _build/html
```

If you must skip a step, state the reason in the PR description.

### 8. Commit, push, and open a PR

```bash
git add <files>
git commit -m "Add <thing> in _errortools/<file>.py"
git push origin <type>/<branch-name>
```

Open a pull request against `main` and fill in
[`.github/PULL_REQUEST_TEMPLATE.md`](PULL_REQUEST_TEMPLATE.md). It has
six sections:

- Description — link the relevant `.agents/skills/<name>.md` you followed.
- Related Issues — use `Closes #N` or `Relates to #N`.
- Type of Change — tick exactly one.
- Scope — mark `Public API change`, `Behaviour change`, or `Internal`.
- Newsfragment — required for user-visible changes.
- Reproducer / Sandbox — required for bug fixes.

---

## Style and quality bar

This is the short version. The canonical list is
[`.agents/AGENTS_CHECK_LIST.md`](../.agents/AGENTS_CHECK_LIST.md).

### Backward compatibility

- **Never** silently delete a public name. The deprecation pipeline
  (`_DEPRECATED_NAMES` in `errortools/__init__.py`) is the only blessed
  way to retire a symbol — see
  [`.agents/skills/deprecate-public-name.md`](../.agents/skills/deprecate-public-name.md).
- New parameters are always keyword-only with sensible defaults.
- New behaviour is opt-in: do not change defaults without a deprecation
  path.

### Style

- Line length **120** (`pyproject.toml [tool.black]`, `.editorconfig`).
- Black's `target-version` is `["py313"]`, but the runtime floor is
  Python 3.8 — use `Union[X, Y]`, not `X | Y`.
- Google-style docstrings; doctest-friendly `Example:` blocks render in
  Sphinx.
- New files start with `from __future__ import annotations`.

### Typing

- `mypy _errortools/` exits 0 with the project's existing flags
  (`warn_return_any`, `warn_unused_configs`, `warn_unused_ignores`,
  `python_version = "3.13"`).
- Reuse the existing aliases in `_errortools/typing.py`
  (`ExceptionType`, `WarningType`, `PureBaseExceptionType`,
  `BaseErrorCodesType`, `AnyErrorCode`, `TracebackType`, `FrameType`).
- Add `# type: ignore[reason]` only with a short justification comment;
  prefer fixing the type.

### Tests

- Tests are deterministic, fast, isolated. No network, no real `sleep`.
- The default pytest run includes `--cov=_errortools`; do not disable
  coverage locally unless debugging.
- `pytest --doctest-modules --no-cov` mirrors CI and must be green.

### CLI

- `python -m errortools --help`, `-v`, `-i`, `-c`, `-a`, `-e`, `-l`, `-u`
  all exit 0.
- `logger emit --level info|debug|warning|error|critical
  --output stdout|stderr "msg"` emits a single log line and exits 0.
- `logger shell` launches an interactive REPL with the documented
  pre-imported names (`info`, `debug`, `error`, `warning`, `critical`,
  `trace`, `success`, `exception`, `catch`, `logger`, `Level`, `LEVELS`,
  `BaseLogger`, `Record`, `StreamSink`, `FileSink`, `CallableSink`,
  `Logger`, `Handler`, `Filter`, `Formatter`).
- If you add a CLI flag, update both `.github/workflows/cli-test.yml`
  and `docs/cli_tools/index.md` in the same commit.

### Documentation

- Sphinx docs live under `docs/` and are built on Read the Docs from
  `.readthedocs.yaml`.
- New public symbols need a corresponding entry under
  `docs/api_reference/` (or the appropriate subfolder).
- Non-trivial additions need a runnable example under `docs/examples/`.
- Use `versionadded`, `versionchanged`, `deprecated`, `versionremoved`
  directives where appropriate.

### Performance

- New classes in `_errortools/future.py` (or other hot paths) use
  `__slots__`; no per-instance `__dict__`.
- The optional `_speedup.c` extension has a pure-Python fallback in
  every module that uses a C helper — never break the fallback.
- Performance-sensitive code should be mirrored by a benchmark under
  `testing/benchmark/`.

---

## Pull request guidelines

Before submitting, ensure every applicable box is ticked:

- [ ] Branch name follows `feature/<name>` / `fix/<name>` /
      `refactor/<name>` / `docs/<name>` / `perf/<name>`.
- [ ] Commits are atomic and use the imperative mood
      (`Add …`, `Fix …`, `Refactor …`).
- [ ] New logic lives in `_errortools/`; nothing was added under
      `errortools/` except re-exports in `__init__.py`.
- [ ] New public symbols are added to `__all__` **alphabetically** in
      the appropriate bucket (`functions` / `classes` / `type hints` /
      `plugins` / `metadata` / `submodules`).
- [ ] No backward-incompatible change to the public API.
- [ ] Tests added or updated in the matching `testing/<area>/` file.
- [ ] `reproduce/sandbox/reproduce_issue_<N>.py` added for bug fixes.
- [ ] `reproduce/changelog/<PR>.<type>.md` added for user-visible
      changes.
- [ ] Docs updated: docstring, `docs/api_reference/`, `docs/examples/`
      as needed.
- [ ] `ChangeLog.md` updated under `## [Unreleased]`.
- [ ] `black .`, `flake8`, `flake8 --doctests`, `pyflakes`,
      `mypy _errortools/`, `autoflake …`, `autopep8 …`,
      `pytest`, `pytest --doctest-modules --no-cov`, CLI smoke tests,
      and `sphinx-build` all exit 0.
- [ ] PR description follows
      [`.github/PULL_REQUEST_TEMPLATE.md`](PULL_REQUEST_TEMPLATE.md).
- [ ] Linked issues use `Closes #` or `Relates to #`.
- [ ] Reviewers requested per
      [`.github/CODEOWNERS`](CODEOWNERS).

---

## Code review process

1. **Automated CI** runs on every PR via `.github/workflows/`:
   - `run-tests.yml` — `pytest --doctest-modules --no-cov` on Python
     3.13 (Linux).
   - `pep8-check.yml` — `black .`, `autopep8`, `flake8`,
     `flake8 --doctests`, `pyflakes _errortools/`.
   - `type-check.yml` — `mypy _errortools/`.
   - `code-complexity.yml` — `flake8 --max-complexity 8 --select C901
     _errortools/`.
   - `autoflake-check.yml` — `autoflake --remove-all-unused-imports
     --remove-unused-variables …`.
   - `cli-test.yml` — every CLI flag exercised end-to-end.
   - `docs.yml` — `sphinx-build -b html . _build/html`.
   - Plus the auto-merge / lock / label helpers
     (`auto-awaiting-merge.yml`, `auto-comment.yml`,
     `auto-delete-branch.yml`, `auto-label.yml`,
     `block-merge-if-label.yml`, `lock-threads.yml`).
2. **A maintainer reviews** your code against the checklist above and
   the project's [`PHILOSOPHY.md`](../PHILOSOPHY.md).
3. **You address** any requested changes by pushing follow-up commits
   (do not force-push during review unless asked).
4. **Once approved**, the PR is merged by a maintainer with write
   access. The auto-merge helper will handle the squash / rebase.

---

## Release and versioning

`errortools` follows [Semantic Versioning](https://semver.org/) and ships
from the `main` branch.

- **Patch** (`X.Y.Z+1`) — backward-compatible bug fixes.
- **Minor** (`X.Y+1.0`) — backward-compatible features, new public
  symbols, new optional parameters, new deprecations.
- **Major** (`X+1.0.0`) — allowed to break the public API; the
  deprecation pipeline in `_DEPRECATED_NAMES` is the runway.

When you ship a user-visible change, the version bump is the
maintainer's job — but the inputs come from you:

1. Make sure `ChangeLog.md` has an `## [Unreleased]` bullet (or
   newsfragment) describing the change.
2. If you deprecated or removed a public name, the ChangeLog bullet
   names the version that retires it.
3. For a `minor` or `major` bump, a `docs/whatsnew/<X>_<Y>.md` entry is
   added (linked from `docs/whatsnew/index.md`).

The version itself lives in two places that **must** stay in sync:

- `pyproject.toml` → `[project] version = "X.Y.Z"`.
- `_errortools/version.py` → `__version__: Final[str] = "X.Y.Z"`.

The full playbook is
[`.agents/skills/bump-version.md`](../.agents/skills/bump-version.md).

---

## For AI coding agents

This project ships a dedicated agent-oriented knowledge base under
[`.agents/`](../.agents/README.md). If you are an AI coding agent
(Cline, Cursor, Copilot, Claude Code, or similar), read it before doing
anything:

1. [`.agents/AGENTS_PREVIEW.md`](../.agents/AGENTS_PREVIEW.md) —
   project snapshot, public API map, conventions, anti-patterns.
2. [`.agents/AGENTS_CHECK_LIST.md`](../.agents/AGENTS_CHECK_LIST.md) —
   the pre-completion gate (the one you must tick every box of).
3. [`.agents/skills/`](../.agents/skills/README.md) — task-shaped
   playbooks (add a public API, write tests, bump version, etc.).

Human contributors are welcome to skim the same documents — they
reflect the project's actual conventions.

---

## Where to get help

- **First read** [`README.md`](../README.md) and
  <https://errortools.readthedocs.io>.
- **Then check** [`PHILOSOPHY.md`](../PHILOSOPHY.md) for the values
  behind a decision.
- **Then open** a
  [GitHub Discussion](https://github.com/more-abc/errortools/discussions)
  for questions and ideas.
- **For bugs / features**, file an issue using the
  [issue templates](#reporting-issues).
- **For security**, follow [`.github/SECURITY.md`](SECURITY.md)
  privately — do **not** open a public issue.
- **For support**, see [`.github/SUPPORT.md`](SUPPORT.md).
- **By email**:
  - Documentation / general inquiries: <errortools.docs@proton.me>
  - Security reports: <errortools-security@proton.me>
  - General support: <errortools-support@proton.me>

---

Thank you for contributing! 🎉
