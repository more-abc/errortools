---
name: update-docs
description: Update the Sphinx / readthedocs docs for a change in errortools.
when_to_use:
  - "document this"
  - "update Sphinx"
  - "add a doc example"
  - "update docs"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Keep the documentation in lock-step with the code so that:

- new public symbols have a docstring **and** an entry in
  `docs/api_reference/` (or the matching user guide),
- new behaviours have a runnable example in `docs/examples/`,
- significant releases have a `docs/whatsnew/<X>_<Y>.md` page,
- the Sphinx build (`docs.yml` CI job) stays green.

## Prerequisites

- [ ] `pip install -r docs/requirements.txt`
- [ ] `pip install -e .`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §5.7.
- [ ] Read [`docs/conf.py`](../../docs/conf.py) to know which Sphinx
      extensions and theme options are in use (currently `furo` +
      `myst_parser` + `sphinx_rtd_theme` + `sphinx_copybutton`).

## Procedure

1. **Pick the destination page(s).** The repo is split as:

   | Kind of change | Destination |
   |----------------|-------------|
   | New public function / class | `docs/api_reference/` or matching `docs/user_guide/<topic>.md` |
   | New decorator | `docs/user_guide/decorators.md` |
   | New exception subclass | `docs/user_guide/custom_exceptions.md` |
   | New warning subclass | `docs/user_guide/warnings.md` |
   | New logging sink / feature | `docs/user_guide/logging.md` |
   | New CLI flag / subcommand | `docs/cli_tools/index.md` |
   | New `errortools.future` symbol | `docs/user_guide/future_module.md` |
   | New plugin helper | `docs/extending/plugins.md` |
   | Non-trivial usage example | `docs/examples/index.md` |
   | Significant release | `docs/whatsnew/<X>_<Y>.md` + toctree update |

2. **Use the existing layout.** Each user guide starts with a short
   intro, then a section per concept, and ends with a "See also" or
   "Next" pointer. Match that shape; do not invent a new structure
   for one feature.

3. **MyST Markdown is the source format** (`source_suffix = {".md":
   "markdown"}`). You can use:

   - ` ```{eval-rst}` / ` ``` ` blocks for embedded RST (rare),
   - ` ```{versionadded} 3.6` directives,
   - ` ```{deprecated} 3.0` directives,
   - the colon-fence and dollarmath extensions (already on).

4. **Add a runnable example** to `docs/examples/index.md` when the
   change is non-trivial. Examples should be self-contained — no
   project-specific imports beyond `errortools` and the standard
   library — and copy-pasteable into a REPL.

5. **Update `docs/whatsnew/index.md`'s toctree** if you add a new
   release page.

6. **Run the docs build locally** before pushing:

   ```bash
   cd docs
   sphinx-build -b html . _build/html
   sphinx-build -b html . _build/html -W --keep-going   # strict warnings
   ```

7. **Update [`AGENTS_CHECK_LIST.md`](../AGENTS_CHECK_LIST.md) §10** if
   the destination page is genuinely new (not in the table above).

## Examples

### Real example — adding a decorator to `docs/user_guide/decorators.md`

```markdown
## @error_cache()

Cache exceptions raised by functions, similar to `functools.lru_cache`.

```{versionadded} 3.2
```

```python
from errortools import error_cache, ignore

@error_cache(maxsize=64)
def load(user_id: int) -> dict:
    if user_id < 0:
        raise ValueError(f"invalid id: {user_id}")
    return {"id": user_id}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `maxsize` | `int \| None` | Maximum cache size (`None` = unlimited) |
```

### Real example — adding a whatsnew entry

`docs/whatsnew/3_6.md`:

```markdown
# Release 3.6.0

Release date: 2026-07-XX

## ChangeLog

- Add `is_iterable` runtime check.
- Add `BaseErrorCodes.quota_exceeded` factory for the new `QuotaExceededError`.
```

`docs/whatsnew/index.md`:

```markdown
```{toctree}
---
maxdepth: 2
caption: Contents
---

3_4
3_5
3_6
```
```

## Verification

```bash
cd docs
sphinx-build -b html . _build/html
sphinx-build -b html . _build/html -W --keep-going   # catch warnings
cd ..

# All example snippets in the docs still run
python -c "
import doctest, re, pathlib
for p in pathlib.Path('docs').rglob('*.md'):
    text = p.read_text(encoding='utf-8')
    # illustrative — real extraction is more careful
    if '>>>' in text:
        print(f'has doctest: {p}')
"

# Format / lint (the docs are Markdown; no Python lint applies)
black .  # no-op on .md, but keeps the workspace tidy
flake8   # ditto
```

## Common pitfalls

- ❌ **Editing `docs/_build/`.** It is generated; commit nothing under
  it. `AGENTS_CHECK_LIST.md` §0 lists it as a generated path.
- ❌ **Forgetting the `toctree` entry.** New pages do not appear in
  the sidebar until they are added to a `toctree`.
- ❌ **Inlining code that requires `pip install requests` or
  similar.** Examples must work in a clean environment.
- ❌ **Re-using a `versionadded` directive that is already shipped.**
  The directive is per-page; if you add a new feature to an existing
  page, prefer `**New in 3.6:**` inline instead.
- ❌ **Skipping the strict build (`-W --keep-going`).** CI uses the
  default build; the strict build catches `WARNING: undefined label`
  and similar issues before they ship.

## Related skills

- [`add-public-api.md`](add-public-api.md) — for the symbol itself.
- [`add-decorator.md`](add-decorator.md) — for new decorators.
- [`add-exception-class.md`](add-exception-class.md) — for new error
  codes.
- [`add-warning-class.md`](add-warning-class.md) — for new warnings.
- [`add-cli-flag.md`](add-cli-flag.md) — for new CLI flags.
- [`bump-version.md`](bump-version.md) — required for a new
  `whatsnew/` page.
