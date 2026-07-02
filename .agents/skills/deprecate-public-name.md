---
name: deprecate-public-name
description: Mark a public name as deprecated and route it through the structured deprecation catalogue in errortools/__init__.py.
when_to_use:
  - "deprecate a name"
  - "remove an old API"
  - "soft-delete a public symbol"
version: 0.2.0
applies_to: [errortools >= 3.6.2]
---

## Goal

Soften-delete a public name without breaking existing users:

- the name still imports (returns the *same object* as the canonical replacement),
- a structured `ErrortoolsDeprecationWarning` fires on access — carrying the
  original message, suggestion, deprecated version, and removal version,
- `errortools.<name>` still appears in `dir(errortools)` and `__all__`,
- the replacement is documented as the preferred path,
- a `ChangeLog.md` line names the version and removal target.

Hard deletion is **never** the right move in this project.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §5.1.3 and §5.1.4.
- [ ] Confirm there is a clearly better replacement (otherwise the
      name does not need to be deprecated).
- [ ] Read the **three-table deprecation catalogue** in
      [`errortools/__init__.py`](../../errortools/__init__.py):
      - `_DEPRECATED_NAMES`  — `(display_name, reason)` tuples
      - `_DEPRECATED_VERSIONS` — `(deprecated_in, removed_in)` tuples
      - `_DEPRECATED_RESOLVERS` — lazy zero-arg callables that return
        the canonical replacement object
      All three tables must share the **same key set** — this invariant
      is enforced by `testing/test_init.py::TestDeprecationCatalogue`.

## Procedure

1. **Pick the deprecation target version** (e.g. "remove in 5.0").
   Update the `version` field of the `.. deprecated::` directive.

2. **Route the name through all three deprecation tables** in
   [`errortools/__init__.py`](../../errortools/__init__.py). Adding to
   only `_DEPRECATED_NAMES` will leave the dispatcher's alias-return
   bug unfixed (see the pitfall at the bottom):

   ```python
   # 1. Public-facing display + reason (kept 2-tuple shape for backward
   #    compatibility with existing tooling).
   _DEPRECATED_NAMES["<old_name>"] = ("<old_name>", "Use <NewName> directly.")

   # 2. Structured version metadata so consumers can filter on the
   #    structured warning (`rec.category.removed_version` etc.).
   _DEPRECATED_VERSIONS["<old_name>"] = ("3.6.2", "5.0")

   # 3. Lazy zero-arg resolver returning the canonical replacement.
   #    Crucial: returning the replacement (not ``None``) is what makes
   #    ``from errortools import <old_name>`` keep working.
   def _resolve_<old_name>() -> Any:
       from <canonical_module> import <NewName> as _cls
       return _cls

   _DEPRECATED_RESOLVERS["<old_name>"] = _resolve_<old_name>
   ```

   Order the new key alphabetically in each table.

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

6. **Add a test** in `testing/test_init.py`. The existing test
   `TestDeprecatedNamesDispatcher` and `TestDeprecationCatalogue`
   already cover the structural invariants. For a new entry, the
   minimum new tests are:

   ```python
   def test_<old_name>_emits_warning_with_structured_version(self):
       with warnings.catch_warnings(record=True) as caught:
           warnings.simplefilter("always", errortools.ErrortoolsDeprecationWarning)
           errortools.<old_name>  # noqa: B018
       rec = next(c for c in caught if issubclass(c.category, errortools.ErrortoolsDeprecationWarning))
       assert rec.message.removed_version == "5.0"
       assert rec.message.deprecated_version == "3.6.2"

   def test_<old_name>_returns_canonical_replacement(self):
       with warnings.catch_warnings():
           warnings.simplefilter("ignore")
           assert errortools.<old_name> is errortools.<NewName>  # noqa: B018
   ```

   See [`write-tests.md`](write-tests.md) for more.

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

    .. deprecated:: 3.5.0
        This class is deprecated as it is functionally redundant.
    """
    __slots__ = ("_excs",)

    def __init__(self, *excs: ExceptionType) -> None:
        ErrortoolsDeprecationWarning.emit(
            "fast_ignore is deprecated as it is functionally redundant.",
            use_instead="Use errortools.future.super_fast_ignore instead.",
            deprecated_version="3.5.0",
            removed_version="5.0",
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
_DEPRECATED_VERSIONS["fast_ignore"] = ("3.5.0", "5.0")
def _resolve_fast_ignore() -> Any:
    from _errortools.ignore import fast_ignore as _cls
    return _cls
_DEPRECATED_RESOLVERS["fast_ignore"] = _resolve_fast_ignore
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

```python
# In errortools/__init__.py
_DEPRECATED_NAMES["InputError"] = ("InputError", "Use InvalidInputError directly.")
_DEPRECATED_VERSIONS["InputError"] = ("3.0", "5.0")
def _resolve_input_error() -> Any:
    from _errortools.classes.errorcodes import InvalidInputError as _cls
    return _cls
_DEPRECATED_RESOLVERS["InputError"] = _resolve_input_error
```

## Verification

```bash
# Deprecation warning fires, with structured fields populated
python -W error::errortools.ErrortoolsDeprecationWarning -c "from errortools import <OldName>"

# Structured fields reach the warning instance
python -c "
import warnings, errortools
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    errortools.<OldName>  # noqa: B018
inst = caught[-1].message
assert inst.removed_version == '5.0'
assert inst.deprecated_version == '3.6.2'
"

# Returned object IS the canonical replacement (not None!)
python -c "
import errortools
assert errortools.<OldName> is errortools.<NewName>  # noqa: B018
"

# The name is still in __all__ and __dir__()
python -c "
import errortools
assert '<OldName>' in errortools.__all__
assert '<OldName>' in dir(errortools)
"

# Catalogue invariant — all three tables have the same key set
python -m pytest testing/test_init.py::TestDeprecationCatalogue -v

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
  Use the `ErrortoolsDeprecationWarning.emit(...)` classmethod when
  you have structured metadata — never `warnings.warn(...)` directly
  inside the dispatcher path.
- ❌ **Forgetting the `.. remove::` version.** Without it, the next
  agent has no signal for when the hard delete is allowed.
- ❌ **Documenting the replacement in code but not in docs.** Both the
  docstring *and* `docs/` must point at the new name; users find it
  via the docs first.
- ❌ **Adding only to `_DEPRECATED_NAMES`.** This re-introduces the
  silent-`None` bug: accessing `errortools.<OldName>` will warn *and*
  return `None` instead of the canonical replacement, so
  `isinstance(x, errortools.<OldName>)` will crash. Always populate
  all three tables atomically; `TestDeprecationCatalogue` enforces
  the key-set invariant.

## Related skills

- [`add-public-api.md`](add-public-api.md) — for the replacement.
- [`update-changelog.md`](update-changelog.md) — required.
- [`update-docs.md`](update-docs.md) — required.
- [`write-tests.md`](write-tests.md) — required.
