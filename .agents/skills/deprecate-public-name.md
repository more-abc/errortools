---
name: deprecate-public-name
description: Mark a public name as deprecated and route it through _DEPRECATED_NAMES.
when_to_use:
  - "deprecate a name"
  - "remove an old API"
  - "soft-delete a public symbol"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Soften-delete a public name without breaking existing users:

- the name still imports (returns the same object as the replacement),
- a `DeprecationWarning` is raised on access,
- `errortools.<name>` still appears in `dir(errortools)` and `__all__`,
- the replacement is documented as the preferred path,
- a `ChangeLog.md` line names the version and removal target.

Hard deletion is **never** the right move in this project.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §5.1.3 and §5.1.4.
- [ ] Confirm there is a clearly better replacement (otherwise the
      name does not need to be deprecated).
- [ ] Read `_DEPRECATED_NAMES` in `errortools/__init__.py` to see the
      existing entries (already includes `InputError`, `AccessError`,
      `LookupError_`, `RuntimeError_`, `fast_ignore`).

## Procedure

1. **Pick the deprecation target version** (e.g. "remove in 5.0").
   Update the `version` field of the `.. deprecated::` directive.

2. **Route the name through `_DEPRECATED_NAMES`** in
   [`errortools/__init__.py`](../../errortools/__init__.py). The entry
   is a `(attr_name, reason)` tuple; the existing
   `ErrortoolsDeprecationWarning` is emitted on access:

   ```python
   _DEPRECATED_NAMES: dict[str, tuple[str, str]] = {
       "<old_name>": ("<old_name>", "Use <NewName> directly."),
       # ...
   }
   ```

3. **Keep the name in `__all__`.** The list is consulted by
   `__dir__()`; removing the entry would make `dir(errortools)` lose
   the name and break code that does `from errortools import *`.

4. **Add a `.. deprecated::` directive** to the docstring of the
   replacement symbol (or the deprecated one, if it has a public
   docstring). For type aliases, the existing pattern in
   `_errortools/typing.py` is:

   ```python
   InputError: TypeAlias = InvalidInputError
   """Alias for `InvalidInputError` (1001).

   .. remove:: 5.0
   .. deprecated:: 3.0
       This type alias is deprecated as it is redundant.
   """
   ```

5. **Add a ChangeLog bullet** under `## [Unreleased]` (or the dated
   block if shipping now) that names the version, the deprecated
   name, the replacement, and the planned removal version. Example:

   ```markdown
   - Deprecate `fast_ignore` in `_errortools/ignore.py`; use
     `errortools.future.super_fast_ignore` instead. Removal planned
     for 5.0.
   ```

6. **Add a test** that the deprecation warning fires on access, and
   that the returned object is the same instance the replacement
   returns. See
   [`write-tests.md`](write-tests.md).

7. **Update the docs.** If the deprecated name had a page in
   `docs/api_reference/` or a `toctree` entry, add a banner pointing
   to the replacement, but **do not** delete the page yet — it stays
   until the removal version.

8. **(Optional) Schedule the actual removal.** Add a TODO comment in
   the source pointing at the removal version, so the next agent
   knows when to do the hard delete (and to put a final ChangeLog
   line in the removal release).

## Examples

### Real example — deprecating `fast_ignore`

```python
# In _errortools/ignore.py
class fast_ignore:
    """Ultra-lightweight context manager to suppress exceptions.

    .. deprecated:: 3.0.0
        This class is deprecated as it is functionally redundant.
    """
    __slots__ = ("_excs",)

    def __init__(self, *excs: ExceptionType) -> None:
        warnings.warn(
            "fast_ignore is deprecated as it is functionally redundant.",
            DeprecationWarning,
            stacklevel=2,
        )
        ...
```

```python
# In errortools/__init__.py
_DEPRECATED_NAMES: dict[str, tuple[str, str]] = {
    "fast_ignore": ("fast_ignore", "Use errortools.future.super_fast_ignore instead."),
    # ...
}
```

### Real example — deprecating a type alias

```python
# In _errortools/typing.py
InputError: TypeAlias = InvalidInputError
"""Alias for `InvalidInputError` (1001).

.. remove:: 5.0
.. deprecated:: 3.0
    This type alias is deprecated as it is redundant."""
```

## Verification

```bash
# Deprecation warning fires
python -W error::DeprecationWarning -c "from errortools import <OldName>"

# Returned object is the same as the replacement
python -c "
import errortools
assert errortools.<OldName> is errortools.<NewName>
"

# The name is still in __all__ and __dir__
python -c "
import errortools
assert '<OldName>' in errortools.__all__
assert '<OldName>' in dir(errortools)
"

# Quality gate
black .
flake8
mypy _errortools/
pytest
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Hard-deleting the name.** This breaks every user who still
  imports it. Always go through `_DEPRECATED_NAMES`.
- ❌ **Removing the entry from `__all__`.** `dir(errortools)` and
  `from errortools import *` rely on `__all__`; dropping the entry
  breaks those quietly.
- ❌ **Emitting a bare `DeprecationWarning`.** Prefer
  `ErrortoolsDeprecationWarning` (already defined) for the
  `__getattr__` path so consumers can filter on a specific subclass.
- ❌ **Forgetting the `.. remove::` version.** Without it, the next
  agent has no signal for when the hard delete is allowed.
- ❌ **Documenting the replacement in code but not in docs.** Both the
  docstring *and* `docs/` must point at the new name; users find it
  via the docs first.

## Related skills

- [`add-public-api.md`](add-public-api.md) — for the replacement.
- [`update-changelog.md`](update-changelog.md) — required.
- [`update-docs.md`](update-docs.md) — required.
- [`write-tests.md`](write-tests.md) — required.
