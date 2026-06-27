---
name: add-exception-class
description: Add a new predefined error code under BaseErrorCodes.
when_to_use:
  - "add a new error code"
  - "subclass BaseErrorCodes"
  - "add InvalidInputError-style helper"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Add a new predefined exception class to the
`BaseErrorCodes` family so that users can write
`raise BaseErrorCodes.<name>("…")` (factory) or
`raise <Name>Error("…")` (direct).

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §3.4.
- [ ] Read `_errortools/classes/errorcodes.py` to see the existing
  layering (`PureBaseException` → `ContextException` → `BaseErrorCodes`).
- [ ] Pick a **unique** numeric `code` from a sensible block (existing
  range: 1xxx / 2xxx / 3xxx / 4xxx / 5xxx).

## Procedure

1. **Pick the right layer.** Choose the lowest layer that fits:
   - `PureBaseException` — just `code` + `default_detail` + a string
     representation. No context, no chain.
   - `ContextException` — adds `trace_id`, `context`, `with_context`,
     `with_cause`, `chain`, `traceback`. Use this when the error needs
     structured context.
   - `BaseErrorCodes` — adds factory classmethods. Use this for
     user-facing predefined codes.

2. **Add a new class in `_errortools/classes/errorcodes.py`.** Stick to
   the existing template:

   ```python
   class <Name>Error(BaseErrorCodes):
       """<One-line description> (<code>): <semantics>."""

       code = <unique-int>
       default_detail = "<human readable message>."
   ```

3. **Add a factory classmethod on `BaseErrorCodes`** next to
   `invalid_input`, `not_found`, `access_denied`, etc.:

   ```python
   @classmethod
   def <name>(cls, detail: Union[str, None] = None) -> "<Name>Error":
       """<Description> (Error Code: <code>)."""
       return <Name>Error(detail)
   ```

4. **Update the exports in `_errortools/typing.py`** if a new alias is
   appropriate. The existing union alias `AnyErrorCode` may need to
   include the new type.

5. **Re-export from `errortools/__init__.py`** in this exact order:
   - import the new class next to its siblings,
   - add the class to the `# classes` bucket of `__all__`,
   - add the factory classmethod to nothing — it lives on
     `BaseErrorCodes` which is already in `__all__`.

6. **Write tests** in `testing/classes/test_errorcodes.py`:
   - the class raises with the right `code`, `detail`, `__str__`,
   - the factory returns the same class,
   - the chain/context/cause helpers behave as documented
     (if it extends `ContextException`).

7. **Document it** in `docs/user_guide/custom_exceptions.md` (the
   "Predefined error codes" table) and in
   `docs/api_reference/`.

8. **Add a ChangeLog entry** under `## [Unreleased]`.

## Examples

### Real example — `InvalidInputError`

```python
class InvalidInputError(BaseErrorCodes):
    """Input Validation Error (1001): Used for scenarios where parameter or input format validation fails."""

    code = 1001
    default_detail = "Invalid input."
```

```python
@classmethod
def invalid_input(cls, detail: Union[str, None] = None) -> "InvalidInputError":
    """Input Validation Error (Error Code: 1001)."""
    return InvalidInputError(detail)
```

### Adding a new code, e.g. `QuotaExceededError [6001]`

```python
class QuotaExceededError(BaseErrorCodes):
    """Quota Exceeded Error (6001): A usage or rate quota has been exceeded."""

    code = 6001
    default_detail = "Quota exceeded."
```

```python
@classmethod
def quota_exceeded(cls, detail: Union[str, None] = None) -> "QuotaExceededError":
    """Quota Exceeded Error (Error Code: 6001)."""
    return QuotaExceededError(detail)
```

Then add `QuotaExceededError` to `errortools/__all__` and to
`AnyErrorCode` in `_errortools/typing.py`.

## Verification

```bash
python -c "from errortools import BaseErrorCodes, <Name>Error; \
    e = BaseErrorCodes.<name>('boom'); assert isinstance(e, <Name>Error); \
    assert e.code == <unique-int>"

black .
flake8
mypy _errortools/
pytest testing/classes/test_errorcodes.py
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Re-using a `code` value.** Each numeric code must be unique within
  the `BaseErrorCodes` family; collisions break consumers that switch on
  `code`.
- ❌ **Editing `AnyErrorCode` to exclude a deprecated code.** The whole
  point of the union is to keep consumers exhaustive; the right move is
  `.. deprecated::` documentation, not removal.
- ❌ **Returning a different class from the factory.** The factory must
  return the matching subclass.
- ❌ **Forgetting `with_context` / `with_cause` tests.** If the new class
  inherits from `ContextException`, the chain helpers must keep working
  for the whole family.

## Related skills

- [`add-warning-class.md`](add-warning-class.md) — for `Warning`
  subclasses (not `Exception` subclasses).
- [`add-public-api.md`](add-public-api.md) — for the re-export step.
- [`write-tests.md`](write-tests.md) — required.
- [`update-docs.md`](update-docs.md) — required.
- [`update-changelog.md`](update-changelog.md) — required.
