# Frequently Asked Questions (FAQ)

This page collects common questions and their answers about errortools. If you cannot find what you are looking for, feel free to [open an issue](https://github.com/more-abc/errortools/issues).

## General

### What Python versions are supported?

errortools supports **Python 3.8 and higher**. The core package has **zero external dependencies**.

### Is errortools production-ready?

Yes. The library follows [semantic versioning](https://semver.org/) and has a comprehensive test suite. APIs marked as `provisional` or experimental may change in minor releases; stable APIs will not break within a major version.

### How does errortools relate to the standard library?

errortools is **not** a replacement for the standard library. It complements `contextlib.suppress`, `warnings`, and `logging` with convenience wrappers, structured exceptions, and loguru-inspired logging. You can mix and match freely with standard library tools.

## Exception Handling

### What is the difference between `ignore()` and `fast_ignore()`?

| Feature | `ignore()` | `fast_ignore()` |
|---------|-----------|-----------------|
| Returns metadata | Yes (`be_ignore`, `name`, `count`, `exception`, `traceback`) | No |
| Can be used as a decorator | Yes | Yes |
| Overhead | Medium | Low |
| Best for | Development, debugging | Production hot paths |

For absolute minimal overhead in tight loops, consider `super_fast_ignore()` from the [`future` module](../user_guide/future_module.md).

### Can I suppress multiple exception types at once?

Yes. Both `ignore()` and `fast_ignore()` accept multiple exception types:

```python
from errortools import ignore

with ignore(ValueError, TypeError, AttributeError) as err:
    some_risky_operation()
```

### How do I access the suppressed exception instance?

```python
from errortools import ignore

with ignore(ValueError) as err:
    int("not a number")

if err.be_ignore:
    print(err.exception)   # ValueError('invalid literal for int() with base 10: \'not a number\'')
    print(err.traceback)   # Full traceback string
```

## Logging

### How is this different from the standard `logging` module?

errortools.logging is inspired by [loguru](https://github.com/Delgan/loguru) and offers:

- **Simpler API** — `logger.info("Hello, {}!", name)` instead of `%`-style formatting or `extra=` dicts.
- **Runtime sink management** — add and remove file/stdout/callable sinks without touching configuration files.
- **Automatic colourisation** — coloured output in TTY terminals without extra configuration.
- **Context binding** — create child loggers with extra fields via `bind()`.
- **Zero dependencies** — unlike loguru, errortools carries no external packages.

### Can I use `str.format` style in log messages?

Yes. errortools uses Python's `{ }` format syntax (like loguru), not `%-formatting`:

```python
logger.info("User {} logged in at {}", user_id, timestamp)
logger.info("Disk at {pct:.1f}%", pct=92.5)
```

### How do I rotate and retain log files?

Use the `rotation` (bytes) and `retention` (number of old files) parameters:

```python
logger.add(
    "app.log",
    rotation=10_000_000,  # Rotate when file reaches 10 MB
    retention=5            # Keep 5 rotated files
)
```

### Can I send logs to multiple destinations?

Yes. `add()` returns a sink ID that you can use to manage each destination independently:

```python
import sys

console = logger.add(sys.stderr, level="WARNING")
debug_file = logger.add("debug.log", level="DEBUG")

# Remove only the console sink
logger.remove(console)
```

### How do I capture exceptions automatically?

Use `logger.exception()` inside an `except` block, or `logger.catch()` as a context manager / decorator:

```python
# Inside except block
logger.exception("Something went wrong")

# Context manager
with logger.catch():
    risky_call()

# Decorator — suppress and log
@logger.catch(ValueError)
def parse_int(s: str) -> int:
    return int(s)
```

## Custom Exceptions

### Should I subclass `PureBaseException` or `ContextException`?

| Base class | Use when... |
|------------|-------------|
| `PureBaseException` | You need simple error codes and messages. |
| `ContextException` | You also need trace IDs, extra context dicts, or exception chaining. |

Both classes are lightweight and fully typed.

### How do error codes show up in string output?

```python
from errortools import PureBaseException

class MyError(PureBaseException):
    code = 9000
    default_detail = "Something failed"

err = MyError("custom message")
print(str(err))    # [9000] custom message
print(repr(err))   # MyError(detail='custom message', code=9000)
```

### Can I chain exceptions?

Yes — use `ContextException.with_cause()` to preserve the original traceback:

```python
from errortools import ContextException

class ServiceError(ContextException):
    code = 5001
    default_detail = "Service call failed"

try:
    raise ConnectionError("timed out")
except ConnectionError as exc:
    raise (
        ServiceError("Database unreachable")
        .with_context(endpoint="/api/users")
        .with_cause(exc)
    )
```

## Decorators

### Does `@retry()` work with async functions?

Yes. `retry()` is fully compatible with `async def` and will await the retry delays correctly:

```python
from errortools import retry

@retry(times=3, on=TimeoutError, delay=1.0)
async def fetch_data(url: str) -> bytes:
    ...
```

### How does `@error_cache()` differ from `functools.lru_cache`?

`error_cache()` caches **exceptions** by arguments, returning the same exception instance on subsequent calls. This is useful when validation failure is deterministic and expensive (e.g. database or API checks):

```python
from errortools import error_cache

@error_cache(maxsize=128)
def validate_token(token: str) -> dict:
    if not is_valid_format(token):
        raise ValueError("bad token")
    return lookup(token)
```

## Warnings

### How do I suppress errortools warnings?

Use `ignore_warns()` the same way you would suppress standard-library warnings:

```python
from errortools import ignore_warns

with ignore_warns(DeprecationWarning):
    legacy_function()
```

To suppress **all** warnings, call `ignore_warns()` without arguments.

## Contributing

### How can I report a bug or request a feature?

Open an issue on [GitHub](https://github.com/more-abc/errortools/issues). Please include:

- errortools version (`python -m errortools -v`)
- Python version
- A minimal code snippet that reproduces the problem

## See also

- [Erron the mascot](mascot.md) — Meet our friendly mascot 🦎
- [EMEP Index](../emeps/index.md) — Proposals for future enhancements
