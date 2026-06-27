---
name: add-cli-flag
description: Add a new --flag to the errortools or logger CLI.
when_to_use:
  - "add a new CLI flag"
  - "add an option to errortools"
  - "add an option to logger"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Add a new `--<flag>` (with optional short form `-x`) to **either**:

- the `errortools` family (`python -m errortools`), or
- the `logger` family (`logger`).

The flag must:

- be parsed by the right family-specific parser,
- dispatch to a dedicated handler function in `_FLAG_ACTIONS` (or the
  logger equivalent),
- be exercised in `.github/workflows/cli-test.yml`,
- be documented in `docs/cli_tools/index.md`,
- show up in `ChangeLog.md`.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §4 and the top of
      [`AGENTS_CHECK_LIST.md`](../AGENTS_CHECK_LIST.md) §9.
- [ ] Read [`_errortools/cli.py`](../../_errortools/cli.py) to understand
      the family detection and the `_FLAG_ACTIONS` dispatcher.

## Procedure

1. **Confirm the family.** Re-read the `_detect_mode` helper — flags
   belong to the family that owns the `argv[0]` basename. Pick the
   correct family up front; do not move flags between families later.

2. **Add a parser argument** in the right `_build_*_parser` function:

   For the `errortools` family:

   ```python
   parser.add_argument(
       "--<flag>",
       "-<x>",                           # optional short flag
       action="store_true",              # or store/store_const/count/...
       help="<one-line help text shown in --help>",
   )
   ```

   For the `logger` family (subcommands like `emit`), add the argument
   to `parser_emit` (or the new sub-parser).

3. **Add a dedicated action function** named `_show_<flag>` (verb-first
   so they sort together) or a more domain-specific name. Keep functions
   trivial — they only print / write one thing.

   ```python
   def _show_<flag>() -> None:
       """Print <thing>."""
       print(<thing>)
   ```

4. **Register the function in `_FLAG_ACTIONS`** (or the logger dispatcher
   dict) in alphabetical order. The dispatcher iterates the dict and
   calls the first one whose attribute is truthy on the parsed namespace.

5. **Cover the new flag in `cli-test.yml`.** Add a `run:` step that
   invokes the flag end-to-end on Python 3.13. Look at the existing
   entries (e.g. `Test --author (-a)`) and mirror their style.

6. **Document the new flag** in `docs/cli_tools/index.md` — add a row to
   the matching *Options* table and a one-line example in the
   *Examples* block.

7. **Add a ChangeLog entry** under `## [Unreleased]`.

8. **If the flag requires new metadata** (e.g. a new author email), add
   it to `_errortools/metadata.py` and to the `--info` output if
   appropriate.

## Examples

### Real example — adding `--tagline` to the `errortools` family

In `_errortools/cli.py`:

```python
# inside _build_errortools_parser
parser.add_argument(
    "--tagline",
    "-t",
    action="store_true",
    help="Show the project tagline",
)

# a dedicated handler
def _show_tagline() -> None:
    """Print the project tagline."""
    print("Lightweight Python exception handling, batteries included.")

# register alphabetically
_FLAG_ACTIONS: Final[dict[str, Callable[[], None]]] = {
    # ...
    "tagline": _show_tagline,
    "url": _show_url,
    # ...
}
```

In `.github/workflows/cli-test.yml`:

```yaml
- name: Test --tagline (-t)
  run: python -m errortools --tagline
```

In `docs/cli_tools/index.md`, add a row:

```markdown
| `--tagline` | `-t` | Show the project tagline |
```

## Verification

```bash
# The new flag is recognized
python -m errortools --help
python -m errortools --<flag>
python -m errortools -<x>     # if a short form was added

# The CI workflow file is valid YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/cli-test.yml'))"

# Format / lint / type
black .
flake8
mypy _errortools/
```

## Common pitfalls

- ❌ **Adding a flag to the wrong family.** The dispatcher is determined
  by `argv[0]` basename; mixing up the family yields surprising `--help`
  output. Use the correct `_build_*_parser`.
- ❌ **Inlining a multi-line body in the action function.** Keep handlers
  one or two lines; extract a helper if you need more.
- ❌ **Forgetting the CLI workflow step.** The CI smoke test is the
  single source of truth for "does the CLI still work".
- ❌ **Forgetting the docs row.** Users find flags via the docs table.
- ❌ **Using `argparse(color=True)` unconditionally.** Gate it behind
  `if sys.version_info >= (3, 14):` like the existing `_make_parser`.

## Related skills

- [`add-subcommand.md`](add-subcommand.md) — when the change is a whole
  new subcommand (`logger <thing>`), not just a flag.
- [`update-docs.md`](update-docs.md) — required (`docs/cli_tools/index.md`).
- [`update-changelog.md`](update-changelog.md) — required.
- [`write-tests.md`](write-tests.md) — required for any non-trivial
  handler logic.
