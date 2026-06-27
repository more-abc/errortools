---
name: bump-version
description: Bump the errortools version number across all locations.
when_to_use:
  - "bump version"
  - "prepare release"
  - "update version"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Bump the package version in **every** place it appears so that:

- `pip show errortools` shows the new version,
- `python -m errortools --version` prints the new version,
- `docs/conf.py` reads the new version for `version` / `release`,
- `__version_tuple__` and `__version_info__` stay consistent with
  `__version__`.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §6 (Cheat Sheet).
- [ ] Decide the bump type: `major`, `minor`, or `patch` per SemVer.

## Procedure

1. **Pick the new version** (e.g. `3.6.0`). Follow SemVer:
   - `major` for incompatible API changes,
   - `minor` for backward-compatible features,
   - `patch` for backward-compatible bug fixes.

2. **Edit [`pyproject.toml`](../../pyproject.toml)** — change
   `version = "<old>"` to `version = "<new>"`.

3. **Edit [`_errortools/version.py`](../../_errortools/version.py)** —
   change `__version__: Final[str] = "<old>"` to
   `__version__: Final[str] = "<new>"`. The downstream constants
   (`__version_info__`, `__version_tuple__`, `version`,
   `version_info`, `version_tuple`) are derived and will pick up the
   new value automatically.

4. **Add a `docs/whatsnew/<X>_<Y>.md`** entry with a `## ChangeLog`
   section. Mirror the structure of `docs/whatsnew/3_5.md` /
   `docs/whatsnew/3_4.md`. Add it to the `toctree` in
   `docs/whatsnew/index.md` if one already exists.

5. **Update `ChangeLog.md`** — move the `## [Unreleased]` block (if any)
   into a dated `## v<X>.<Y>.<Z> - YYYY-MM-DD` block, and create a new
   empty `## [Unreleased]` block at the top.

6. **(Optional) Add a git tag** — only on a real release, never on
   `pip install -e .`. The maintainer team runs the tag; agents do
   **not** push tags without explicit user approval.

7. **Run [`update-changelog.md`](update-changelog.md) and
   [`update-docs.md`](update-docs.md) procedures** if any ChangeLog or
   doc string mentions the old version number.

## Examples

### Real example — `3.5.5` → `3.5.6`

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
-version = "3.5.5"
+version = "3.5.6"

--- a/_errortools/version.py
+++ b/_errortools/version.py
-__version__: Final[str] = "3.5.5"
+__version__: Final[str] = "3.5.6"
```

`ChangeLog.md`:

```diff
 ## [Unreleased]
+

+## v3.5.6 - 2026-06-27
+- Move `_print_info` and `_cmd_log` function from `_errortools/_cli.py` to `_errortools/cli.py` and delete `_errortools/_cli.py`.
```

### Real example — first minor release

For `3.5.6` → `3.6.0`, also add `docs/whatsnew/3_6.md`:

```markdown
# Release 3.6.0

Release date: 2026-07-XX

## ChangeLog

- One-line summary of each user-visible change since 3.5.x.
```

…and list it in `docs/whatsnew/index.md`'s `toctree`.

## Verification

```bash
# Both files agree
grep -n '^version ' pyproject.toml
grep -n '^__version__:' _errortools/version.py

# At runtime
python -c "import errortools; print(errortools.__version__)"
python -m errortools --version          # should print `errortools 3.6.0`
python -c "import errortools; assert errortools.__version_tuple__ == (3, 6, 0)"
python -c "import errortools; assert errortools.__version_info__.to_tuple() == (3, 6, 0)"

# Docs build
cd docs && sphinx-build -b html . _build/html && cd ..

# Full quality gate
black .
flake8
mypy _errortools/
pytest
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Bumping `pyproject.toml` but forgetting `__version__`.** Both must
  match; the version in `pyproject.toml` is the build-time value, and
  `__version__` is the runtime value.
- ❌ **Hard-coding the version in docs prose.** Sphinx already reads
  `version` / `release` from `_errortools/version.py`; use those
  substitutions or just say "the current release" instead of writing
  out a number.
- ❌ **Pushing a git tag as an agent.** Tagging is a maintainer action;
  only do it if the user explicitly asks.
- ❌ **Skipping the `whatsnew/` entry.** Major and minor bumps always
  need one; patch bumps can skip it if the only changes are
  internal/CI.
- ❌ **Forgetting the Sphinx substitution cache.** If the docs HTML
  still shows the old version, delete `docs/_build/` and rebuild.

## Related skills

- [`update-changelog.md`](update-changelog.md) — required for every bump.
- [`update-docs.md`](update-docs.md) — required (`whatsnew/` entry).
- [`add-public-api.md`](add-public-api.md) — if the bump introduces a
  new public symbol.
- [`deprecate-public-name.md`](deprecate-public-name.md) — if the bump
  deprecates a public name.
