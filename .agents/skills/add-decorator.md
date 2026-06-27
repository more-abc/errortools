---
name: add-decorator
description: Add a new @decorator under _errortools/decorator/ and re-export it.
when_to_use:
  - "add a new decorator"
  - "wrap with @something"
  - "add @retry-style helper"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

Ship a new reusable decorator `@<name>` that:

- lives in `_errortools/decorator/<name>.py`,
- is registered in `_errortools/decorator/__init__.py` (which is empty by
  design — see source),
- is re-exported from `errortools/__init__.py` and listed in `__all__`,
- supports both sync and async callables if it is retry-style,
- preserves the wrapped function's signature via `functools.wraps`,
- is fully tested.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md) §3.3.
- [ ] Skim existing decorators for shape:
  `_errortools/decorator/{handlers,retry,timeout,cache,deprecated}.py`.

## Procedure

1. **Choose the file.** One decorator per file unless two are tightly
   coupled (e.g. `suppress` and `convert` in `handlers.py`).

2. **Write the decorator.** Use this skeleton:

   ```python
   """One-line summary of the decorator."""

   from __future__ import annotations
   from functools import wraps
   from typing import Any, Callable, TypeVar, Union

   _F = TypeVar("_F", bound=Callable[..., Any])
   _ExcTypes = Union[type[BaseException], tuple[type[BaseException], ...]]

   __all__ = ["<name>"]


   def <name>(
       *exceptions: type[BaseException],
       # … parameters …
   ) -> Callable[[_F], _F]:
       """Decorator docstring (Google style)."""
       def decorator(func: _F) -> _F:
           @wraps(func)
           def wrapper(*args: Any, **kwargs: Any) -> Any:
               # body
               return func(*args, **kwargs)
           return wrapper  # type: ignore[return-value]
       return decorator
   ```

3. **For retry-style decorators** (asynchronous or scheduled retries),
   detect coroutine functions with `inspect.iscoroutinefunction(func)` and
   return a separate `async_wrapper`. See `_errortools/decorator/retry.py`
   for the canonical pattern.

4. **Validate inputs eagerly.** Raise `TypeError` / `ValueError` at
   decorator-construction time, not at call time, so misconfiguration is
   loud.

5. **Preserve the original function** with `functools.wraps` and assign
   `__wrapped__` if the wrapper hides a stack frame. This is what makes
   the decorator transparent to introspection, `pytest`, and IDEs.

6. **Re-export from `errortools/__init__.py`** in the `# functions` bucket
   of `__all__`, alphabetically sorted. See
   [`add-public-api.md`](add-public-api.md#procedure).

7. **Write tests** in `testing/test_decorator.py` (or a new file under
   `testing/decorator/`). Cover:
   - happy path,
   - each documented exception type,
   - async/sync branching (if applicable),
   - the `functools.wraps` invariants (`__name__`, `__doc__`).

8. **Document it** in `docs/user_guide/decorators.md`. Add a small example
   to `docs/examples/` if the use case is non-obvious.

9. **Add a ChangeLog entry.** See [`update-changelog.md`](update-changelog.md).

## Examples

### Real example — `@deprecated`

`_errortools/decorator/deprecated.py` is the simplest decorator in the
project and a good template:

```python
def deprecated(
    version: str,
    reason: str = "This function is deprecated and will be removed in a future version.",
) -> Callable:
    """Decorator that marks a function as deprecated."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated since version {version}. {reason}"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Real example — async-aware `@retry`

`_errortools/decorator/retry.py` uses `inspect.iscoroutinefunction` to
branch into `_sync_retry` and `_async_retry`. Copy that structure for any
decorator that may wrap a coroutine.

## Verification

```bash
# Manual sanity check
python -c "from errortools import <name>; \
    @<name>(...) \
    def f(): ...; \
    print(f.__name__)"

# Format / lint / type / test
black .
flake8
mypy _errortools/
pytest testing/test_decorator.py
pytest --doctest-modules --no-cov
```

## Common pitfalls

- ❌ **Forgetting `functools.wraps`.** Without it, `func.__name__` and
  `func.__doc__` are lost; `pytest --doctest-modules` and IDE tooling
  break.
- ❌ **Detecting coroutine functions too late.** The detection has to
  happen in `__call__` of the decorator factory, not in the wrapper.
- ❌ **Adding new runtime dependencies.** The project is zero-deps at
  runtime; `from asyncio`, `from functools`, `from inspect` are fine.
- ❌ **Decorating with no `__all__`.** A missing `__all__` will fail
  `pyflakes` and `flake8-bugbear`.
- ❌ **Returning the original function unchanged.** Always return
  `wrapper`, even when the decorator is a no-op in the default config.

## Related skills

- [`add-public-api.md`](add-public-api.md) — for non-decorator public symbols.
- [`deprecate-public-name.md`](deprecate-public-name.md) — when the new
  decorator replaces an older one.
- [`write-tests.md`](write-tests.md) — required for every new decorator.
- [`update-docs.md`](update-docs.md) — `docs/user_guide/decorators.md`.
- [`update-changelog.md`](update-changelog.md) — required.
