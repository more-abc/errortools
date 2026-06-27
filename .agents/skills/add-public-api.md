---
name: add-public-api
description: Add a new public function, class, or constant to errortools.
when_to_use:
  - "add a public function"
  - "expose a new symbol"
  - "extend errortools public API"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Introduce a new public symbol under `errortools.*` that is:

- implemented in `_errortools/`,
- re-exported from `errortools/__init__.py`,
- listed in `__all__` alphabetically,
- covered by a unit test,
- mentioned in `ChangeLog.md` and `docs/`.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §3 and §5.
- [ ] Confirm the symbol is **not** already provided by the standard library
      or an existing utility in `_errortools/`.

## Procedure

1. **Decide the module.** Place the new symbol in the module that owns the
   concept. The rule of thumb in this repo is one concept per file:
   - `ignore.py` → `ignore`, `ignore_subclass`, `ignore_warns`
   - `raises.py` → `raises`, `raises_all`, `reraise`, `assert_raises`
   - `errno.py` → errno helpers
   - `future.py` → `super_fast_*`, `ExceptionCollector`
   - `decorator/<name>.py` → `@<name>` decorators
   - `classes/errorcodes.py` → `BaseErrorCodes` and subclasses
   - `classes/warn.py` → `BaseWarning` and subclasses
   - `descriptor/<name>.py` → descriptor-based validators
   - `logging/<name>.py` → logger internals
   - `wrappers/<name>.py` → low-overhead wrappers

2. **Implement in `_errortools/<file>.py`.** New files need a module-level
   docstring and an `__all__` list. Follow the existing patterns:
   - Use `from __future__ import annotations` at the top.
   - `Union[X, Y]` instead of `X | Y` (3.8 compat).
   - Reuse existing type aliases (`ExceptionType`, `WarningType`, etc.).
   - Google-style docstring with `Example:` block.
   - Reject malformed inputs with `TypeError` / `ValueError` like the
     surrounding code does.

3. **Re-export from `errortools/__init__.py`.** Add the import inside the
   appropriate block, then add the name to `__all__` in the matching
   alphabetical bucket. Buckets are, in order:
   `# functions`, `# classes`, `# for type hints`, `# plugins`, `# metadata`,
   `# submodules`.

4. **Make submodules lazy if appropriate.** A whole new submodule (e.g. a
   new `errortools.io` sub-namespace) must be loaded via
   `__getattr__`:
   ```python
   if name in ("future", "logging", "partial", "<new_submodule>"):
       return importlib.import_module(f"_errortools.{name}")
   ```

5. **Write at least one unit test.** Mirror the source path:
   `_errortools/<file>.py` ↔ `testing/test_<file>.py` (or the matching
   sub-area). See [`write-tests.md`](write-tests.md).

6. **Update docs.** Add a one-line entry under `docs/api_reference/` (or
   the closest user-guide page) and, if the example is non-trivial, an
   entry in `docs/examples/`. See [`update-docs.md`](update-docs.md).

7. **Add a ChangeLog entry.** Put it under `## [Unreleased]` in
   `ChangeLog.md` (see [`update-changelog.md`](update-changelog.md)).

## Examples

### Minimal example — add `is_iterable`

`_errortools/types.py`:

```python
"""Public type-checking helpers."""

from __future__ import annotations
from collections.abc import Iterable
from typing import Any

__all__ = ["is_iterable"]


def is_iterable(obj: Any) -> bool:
    """Return True if *obj* can be iterated over.

    Example:
        >>> is_iterable([1, 2, 3])
        True
        >>> is_iterable(42)
        False
    """
    return isinstance(obj, Iterable)
```

`errortools/__init__.py` (insert in alphabetical order inside `# functions`):

```python
from _errortools.types import is_iterable
```

```python
# inside __all__, in the '# functions' bucket
"is_iterable",
```

### Real example from errortools

`_errortools/decorator/handlers.py` defines `suppress` and `convert`. They
are imported in `errortools/__init__.py` and listed in `__all__` exactly as
shown above.

## Verification

```bash
# New symbol resolves and behaves as documented
python -c "from errortools import <NewSymbol>; <NewSymbol>(...)"

# All exports are still alphabetical in __all__
python -c "import errortools; from _errortools.metadata import __version__; assert errortools.__all__ == sorted(errortools.__all__)"

# Format, lint, type, test
black .
flake8
mypy _errortools/
pytest testing/test_<file>.py
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Putting implementation in `errortools/<file>.py`.** That package
  only re-exports; the public shim must stay logic-free.
- ❌ **Appending to `__all__` out of order.** The existing list is
  alphabetical; CI reviewers will flag a regression.
- ❌ **Re-defining existing type aliases** (`ExceptionType`, etc.). Reuse
  the ones in `_errortools/typing.py`.
- ❌ **Using PEP 604 union syntax** (`X | Y`) in runtime code — the project
  supports Python 3.8/3.9.
- ❌ **Forgetting `from __future__ import annotations`** in a new file.
- ❌ **Skipping the test.** See [`write-tests.md`](write-tests.md).

## Related skills

- [`add-decorator.md`](add-decorator.md) — when the symbol is a decorator.
- [`add-exception-class.md`](add-exception-class.md) — when the symbol is
  an exception subclass.
- [`add-warning-class.md`](add-warning-class.md) — when the symbol is a
  warning subclass.
- [`deprecate-public-name.md`](deprecate-public-name.md) — when the new
  symbol replaces an older one.
- [`update-changelog.md`](update-changelog.md) — required after every
  public-surface change.
- [`update-docs.md`](update-docs.md) — required after every public-surface
  change.
- [`write-tests.md`](write-tests.md) — required after every public-surface
  change.
