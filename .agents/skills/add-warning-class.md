---
name: add-warning-class
description: Add a new predefined warning class under BaseWarning.
when_to_use:
  - "add a new warning type"
  - "subclass BaseWarning"
  - "add DeprecationWarning-style helper"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Add a new predefined `Warning` subclass to the `BaseWarning` family so
that users can either raise it directly or use the matching
`BaseWarning.<name>()` factory.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §3.4.
- [ ] Read `_errortools/classes/warn.py` to see the existing
  `BaseWarning` family and factory methods.
- [ ] Confirm the new class is not redundant with the existing
  `DeprecatedWarning`, `PerformanceWarning`,
  `ResourceUsageWarning`, `RuntimeBehaviourWarning`,
  `ConfigurationWarning`.

## Procedure

1. **Add a new class in `_errortools/classes/warn.py`.** Use the
   existing template:

   ```python
   class <Name>Warning(BaseWarning):
       """One-line description of when to emit this warning."""

       default_detail = "<human-readable default message>."
   ```

2. **Add a factory classmethod on `BaseWarning`** alongside the existing
   ones (`deprecated`, `performance`, `resource`, `runtime`,
   `configuration`):

   ```python
   @classmethod
   def <name>(cls, detail: Union[str, None] = None) -> <Name>Warning:
       """Return a `<Name>Warning` instance."""
       return <Name>Warning(detail)
   ```

3. **Re-export from `errortools/__init__.py`** in the `# classes` bucket
   of `__all__` (alphabetical order). The factory classmethod is
   reachable via `BaseWarning`, which is already in `__all__`.

4. **Write tests** in `testing/classes/test_warnings.py`:
   - the class can be constructed with and without a `detail`,
   - `emit()` actually issues a warning of the right subclass,
   - `default_detail` is used when no `detail` is supplied,
   - the factory classmethod returns the right subclass.

5. **Document it** in `docs/user_guide/warnings.md` (the table of
   available warning types) and `docs/api_reference/`.

6. **Add a ChangeLog entry** under `## [Unreleased]`.

## Examples

### Real example — `PerformanceWarning`

```python
class PerformanceWarning(BaseWarning):
    """An operation may cause significant performance degradation."""

    default_detail = "This operation may be slow."
```

```python
@classmethod
def performance(cls, detail: Union[str, None] = None) -> PerformanceWarning:
    """Return a `PerformanceWarning` instance."""
    return PerformanceWarning(detail)
```

### Adding a new warning, e.g. `APIDeprecationWarning`

```python
class APIDeprecationWarning(BaseWarning):
    """An API is scheduled for removal in a future version."""

    default_detail = "This API is deprecated and will be removed."
```

```python
@classmethod
def api_deprecated(cls, detail: Union[str, None] = None) -> APIDeprecationWarning:
    """Return an `APIDeprecationWarning` instance."""
    return APIDeprecationWarning(detail)
```

## Verification

```bash
python -c "
import warnings
from errortools import BaseWarning, <Name>Warning
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    BaseWarning.<name>().emit('boom')
    assert any(issubclass(w.category, <Name>Warning) for w in caught)
"

black .
flake8
mypy _errortools/
pytest testing/classes/test_warnings.py
```

## Common pitfalls

- ❌ **Inheriting from `Warning` directly** instead of `BaseWarning`. The
  `default_detail`, `__str__`/`__repr__`, and `emit` machinery is
  centralized on `BaseWarning`; bypass it and you break the
  `BaseWarning.<name>()` factory.
- ❌ **Mismatching the factory name and class name.** The factory method
  on `BaseWarning` must be lowercase snake_case that matches the
  warning's intent (`api_deprecated` ↔ `APIDeprecationWarning`).
- ❌ **Forgetting to suppress the global `DeprecationWarning` filter.**
  `pyproject.toml [tool.pytest.ini_options]` sets
  `filterwarnings = ["ignore::DeprecationWarning"]`; do **not** rely on
  that — emit a specific subclass and assert against it instead.
- ❌ **Failing to update the docs table.** Users find these classes via
  `docs/user_guide/warnings.md`, not via the API reference.

## Related skills

- [`add-exception-class.md`](add-exception-class.md) — for `Exception`
  subclasses (not `Warning`).
- [`add-public-api.md`](add-public-api.md) — for the re-export step.
- [`write-tests.md`](write-tests.md) — required.
- [`update-docs.md`](update-docs.md) — required.
- [`update-changelog.md`](update-changelog.md) — required.
