---
name: update-changelog
description: Add a ChangeLog.md entry for the change you just made.
when_to_use:
  - "add a changelog entry"
  - "document a change"
  - "release notes"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Record every user-visible change in `ChangeLog.md` so that:

- a new entry sits under `## [Unreleased]` (or under a dated block on
  release),
- the wording matches the project's terse, action-first style,
- the line is dated when the change ships in a release.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §6 (Cheat Sheet).
- [ ] Skim the last 10 entries in `ChangeLog.md` to match the local
      house style.

## Procedure

1. **Open `ChangeLog.md`.** Identify the topmost block. For most
   work-in-progress, that is the `## [Unreleased]` block. If the bump
   is happening in the same commit, follow
   [`bump-version.md`](bump-version.md) first.

2. **Add a single bullet** under the appropriate block. The line should
   start with a capitalised verb (past tense) and reference the
   specific module path so the entry is grep-able. The existing
   `ChangeLog.md` style is:

   ```text
   - <Verb> <thing> in `_errortools/<file>.py`.
   - <Verb> <behaviour>. <optional one-line context>.
   ```

3. **Group related bullets** (e.g. the bullets from a single
   feature/refactor). Skip blank lines between bullets inside the same
   group; use a blank line between groups.

4. **If you removed a deprecated public name**, add a bullet that names
   the version that introduces the removal (e.g. `Removed <name>
   deprecated since 3.0.0.`). Do not silently delete the entry.

5. **If you added a new public symbol**, include a one-line usage
   example or a short rationale so the entry is informative.

6. **Avoid meta-noise.** Do not write "Update CHANGELOG" or "Fix typo";
   the bullet must describe the user-visible effect.

7. **When the release ships** (a maintainer runs the release), move the
   `[Unreleased]` bullets into a dated block and bump
   `## v<X>.<Y>.<Z> - YYYY-MM-DD`. Agents do **not** perform this move
   without explicit user approval.

## Examples

### Real example — entry from `ChangeLog.md`

```markdown
## v3.5.6 - 2026-06-27
- Move `_print_info` and `_cmd_log` function from `_errortools/_cli.py` to `_errortools/cli.py` and delete `_errortools/_cli.py`.

## v3.5.5 - 2026-06-26
- Change PEP 604 union type hints (e.g. `a | b`) to `Union[a, b]` form across all source files for compatibility with Python 3.8 and 3.9.
```

### Adding a new entry under `[Unreleased]`

```markdown
## [Unreleased]
- Add `is_iterable` to `_errortools/types.py` for runtime iterable checks.
- Document the `Add ignore_subclass()` user-guide example in `docs/user_guide/exception_handling.md`.
```

## Verification

```bash
# Bullet is reachable via grep
grep -n "is_iterable" ChangeLog.md

# No trailing whitespace on the new line
grep -nE " +$" ChangeLog.md   # should return nothing

# Whole CHANGELOG is still valid Markdown
python -c "import markdown_it; markdown_it.MarkdownIt().render(open('ChangeLog.md').read())"
```

## Common pitfalls

- ❌ **Writing the entry in present tense.** Past tense reads better
  for shipped changes; existing entries are all past tense.
- ❌ **Skipping the file path.** Bullets without a path are
  unactionable when something breaks.
- ❌ **Adding emoji or marketing copy.** The project tone is terse and
  technical.
- ❌ **Modifying dated historical entries** (`## v3.5.0 - …`) to "fix
  typos". Those are immutable once a release ships.
- ❌ **Forgetting the leading `## [Unreleased]` block** when starting
  fresh. It is the only writable section until a release.

## Related skills

- [`bump-version.md`](bump-version.md) — required for a release.
- [`add-public-api.md`](add-public-api.md) — user-visible additions
  always need a ChangeLog line.
- [`deprecate-public-name.md`](deprecate-public-name.md) — removals
  need a ChangeLog line that names the version.
