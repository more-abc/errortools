---
name: add-subcommand
description: Add a brand-new `logger <subcmd>` subcommand.
when_to_use:
  - "add a new subcommand to logger"
  - "add `logger <thing>`"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Introduce a brand-new subcommand under the `logger` CLI family (e.g.
`logger diagnose …`) without touching the `errortools` family. The new
subcommand must:

- be registered on the `logger` subparser in `_errortools/cli.py`,
- dispatch to a dedicated `_dispatch_<subcmd>(args)` function,
- be exercised in `.github/workflows/cli-test.yml`,
- be documented in `docs/cli_tools/index.md`,
- show up in `ChangeLog.md`.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §4.
- [ ] Read [`_errortools/cli.py`](../../_errortools/cli.py) — the
      `_build_logger_parser` and `_dispatch_logger` functions are the
      reference implementation.

## Procedure

1. **Add the subparser** inside `_build_logger_parser`, alongside
   `parser_emit` and the `shell` subparser. Pass a one-line
   `help=` and `description=`:

   ```python
   parser_<subcmd> = subparsers.add_parser(
       "<subcmd>",
       help="<one-line help text>",
       description="<longer description for --help>.",
   )
   parser_<subcmd>.add_argument(
       # positional, optional, flags, ...
   )
   ```

2. **Add a dispatch branch** in `_dispatch_logger`:

   ```python
   def _dispatch_logger(args: argparse.Namespace) -> None:
       if args.subcmd == "shell":
           from _errortools._logger_shell import start_shell
           start_shell()
           return
       if args.subcmd == "emit":
           _cmd_log(args.message, args.level, args.output)
           return
       if args.subcmd == "<subcmd>":
           _cmd_<subcmd>(args)            # your new handler
           return
       sys.stderr.write(f"errortools: unknown logger subcommand {args.subcmd!r}\n")
       sys.exit(2)
   ```

3. **Write a dedicated handler function** in `_errortools/cli.py` (or
   in a new helper module). Keep it focused: parse args, do one thing,
   return.

4. **Cover the new subcommand in `cli-test.yml`.** Add at least one
   `run:` step that exercises the happy path and one that exercises
   `--help`.

5. **Document the new subcommand** in `docs/cli_tools/index.md` — add a
   row to the *Subcommands* table and a section with usage + at least
   one example.

6. **Add a ChangeLog entry** under `## [Unreleased]`.

7. **If the subcommand is interactive**, follow the pattern of
   `logger shell` (see `_errortools/_logger_shell/`) and register the
   namespace symbols the REPL pre-imports.

## Examples

### Real example — `logger shell`

The existing `shell` subcommand is the canonical reference: it builds
a `code.interact()` REPL, pre-imports a curated namespace, and is
fully covered by `cli-test.yml` indirectly via `--help`. Mirror its
subparser shape exactly.

### Real example — adding `logger tail <file>`

`_errortools/cli.py`:

```python
parser_tail = subparsers.add_parser(
    "tail",
    help="Stream the last lines of a log file",
    description="Stream the last lines of a log file, loguru-style.",
)
parser_tail.add_argument("path", help="Path to the log file")
parser_tail.add_argument("-n", "--lines", type=int, default=10, help="How many lines")
```

```python
def _cmd_tail(path: str, lines: int) -> None:
    """Print the last *lines* lines of *path*."""
    with open(path, "r", encoding="utf-8") as f:
        tail = f.readlines()[-lines:]
    sys.stdout.write("".join(tail))
```

In `.github/workflows/cli-test.yml`:

```yaml
- name: Test logger tail --help
  run: logger tail --help
```

In `docs/cli_tools/index.md`, add a section:

```markdown
### `logger tail`

Stream the last lines of a log file.

\```bash
logger tail logs/app.log --lines 50
\```
```

## Verification

```bash
# Subcommand is registered
logger --help
logger <subcmd> --help

# Happy path
logger <subcmd> <args>

# CI workflow still parses
python -c "import yaml; yaml.safe_load(open('.github/workflows/cli-test.yml'))"

# Format / lint / type
black .
flake8
mypy _errortools/
```

## Common pitfalls

- ❌ **Forgetting to update the defensive fallback** in
  `_dispatch_logger`. The `required=True` on the subparsers guards
  against `None`, but a fallback branch still helps if `required=True`
  is ever loosened.
- ❌ **Mixing families.** The dispatcher is keyed on `argv[0]`
  basename; do not register a `logger`-family subcommand inside
  `_build_errortools_parser`.
- ❌ **Putting the handler inside the dispatch function.** Always
  extract it to a `_cmd_<subcmd>(args)` function — the dispatch
  function must stay trivial for cyclomatic complexity (`flake8
  --max-complexity 8`).
- ❌ **Skipping `--help` coverage in CI.** Every new subcommand needs at
  least a `logger <subcmd> --help` step.

## Related skills

- [`add-cli-flag.md`](add-cli-flag.md) — when the change is a single
  flag under an existing subcommand, not a new subcommand.
- [`update-docs.md`](update-docs.md) — required.
- [`update-changelog.md`](update-changelog.md) — required.
- [`write-tests.md`](write-tests.md) — required for any non-trivial
  handler logic.
