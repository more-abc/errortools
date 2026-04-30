# errortools
A lightweight Python exception handling utility library.

[![Code Style: Google](https://img.shields.io/badge/style-google-3666d6.svg)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings)
[![PyPI Version](https://img.shields.io/pypi/v/errortools)](https://pypi.org/project/errortools/)
[![Python Versions](https://img.shields.io/pypi/pyversions/errortools)](https://pypi.org/project/errortools/)
![This week commits](https://img.shields.io/github/commit-activity/w/more-abc/errortools)
![This month commits](https://img.shields.io/github/commit-activity/m/more-abc/errortools)
![Past year commits](https://img.shields.io/github/commit-activity/y/more-abc/errortools)
![Total commits badge](https://img.shields.io/github/commit-activity/t/more-abc/errortools)

## Features
- **Raise Exceptions**: `raises()`, `raises_all()`, `reraise()` — batch raising and exception conversion
- **Catch & Suppress**: `ignore()`, `ignore_subclass()`, `ignore_warns()`, `fast_ignore()`, `super_fast_ignore()`, `timeout()`, `retry()` — graceful suppression of exceptions and warnings, with automatic retry
- **Future Utilities**: `super_fast_catch()`, `super_fast_reraise()`, `ExceptionCollector` — lightweight exception handling for high-performance scenarios
- **Exception Caching**: `error_cache` — cache exceptions raised by functions (similar to `lru_cache`)
- **Custom Exceptions**: `PureBaseException`, `ContextException`, `BaseErrorCodes`, `BaseWarning` — structured exception classes with error codes, trace IDs, and context
- **Attribute Error Mixin**: Customize error behavior for attribute access, assignment, and deletion
- **Type Aliases**: `ExceptionType`, `AnyErrorCode`, `BaseErrorCodesType`, and more
- **Logging**: `logger` — loguru-inspired structured logger with leveled output, multiple sinks, context binding, and exception capture

## Installation
```bash
pip install errortools
```

---

## Examples

```python
import warnings
from errortools import (
    ignore, fast_ignore, ignore_subclass, ignore_warns, timeout, retry,
    reraise, raises, raises_all, assert_raises,
    error_cache,
    PureBaseException, ContextException, BaseErrorCodes, BaseWarning,
)
from errortools.future import super_fast_ignore, super_fast_catch, super_fast_reraise, ExceptionCollector

# ── 1. ignore ── context manager with full metadata ──────────────────────────
with ignore(KeyError) as err:
    _ = {}["missing"]

assert err.be_ignore          # True  — was suppressed
assert err.name == "KeyError" # exception class name
assert err.count == 1         # how many times suppressed
assert err.exception          # the original KeyError instance
assert err.traceback          # full formatted traceback string
```

**Attributes on the returned object:**

| Attribute | Type | Description |
|---|---|---|
| `be_ignore` | `bool` | `True` if an exception was suppressed |
| `name` | `str \| None` | Class name of the suppressed exception |
| `count` | `int` | Number of suppressed exceptions |
| `exception` | `Exception \| None` | The original exception instance |
| `traceback` | `str \| None` | Formatted traceback string for debugging |

## Examples

```python
# ── ignore as a decorator ──
@ignore(ValueError, TypeError)
def parse(x: str) -> int:
    return int(x)

parse("bad")  # suppressed → returns None

# ── 2. fast_ignore / super_fast_ignore ── zero-overhead hot-path suppression ─
with fast_ignore(KeyError, IndexError):
    _ = [][0]                 # suppressed, no metadata collected

with super_fast_ignore(KeyError):
    _ = {}["x"]              # absolute minimal overhead

# ── 3. ignore_subclass ── suppress any subclass of a base ────────────────────
with ignore_subclass(LookupError):
    raise IndexError("out of range")   # IndexError ⊆ LookupError — suppressed

# ── 4. ignore_warns ── silence warnings ──────────────────────────────────────
with ignore_warns(DeprecationWarning):
    warnings.warn("old api", DeprecationWarning)   # no output

with ignore_warns():           # suppress everything
    warnings.warn("anything")

# ── 5. timeout ── cancel async functions that take too long ──────────────────
@timeout(5.0)
async def fetch_data(url: str) -> bytes:
    ...                               # any async operation

# asyncio.TimeoutError raised automatically if it exceeds 5 s

# ── 6. retry ── automatically retry on failure ───────────────────────────────
@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str) -> None:
    ...                               # retried up to 3 times on ConnectionError

# works with async functions too
@retry(times=5, on=TimeoutError, delay=0.5)
async def fetch(url: str) -> bytes:
    ...

# multiple exception types
@retry(times=2, on=(ValueError, KeyError))
def parse(data: dict) -> str:
    return data["key"]

# ── 7. reraise ── convert exception types on the fly ─────────────────────────
with reraise(KeyError, ValueError):
    raise KeyError("missing key")      # → ValueError: 'missing key'

with reraise((KeyError, IndexError), RuntimeError):
    _ = [][99]                         # → RuntimeError: list index out of range

# ── 8. raises / raises_all ── batch raise ────────────────────────────────────
raises([ValueError], ["bad input"])    # → ValueError: bad input

raises_all(
    [ValueError, TypeError],
    ["bad input"],
)                                      # → ExceptionGroup (2 sub-exceptions)

# ── 9. assert_raises ── assert a callable raises ─────────────────────────────
exc = assert_raises(int, [ValueError], "not-a-number")
print(exc)   # invalid literal for int() with base 10: 'not-a-number'

# ── 10. super_fast_catch ── lightweight exception capture ──────────────────────
with super_fast_catch(ValueError) as ctx:
    raise ValueError("oops")
    
assert ctx.exception is not None
print(ctx.exception)  # ValueError('oops')

# ── 11. super_fast_reraise ── lightweight exception type conversion ────────────
with super_fast_reraise(KeyError, ValueError):
    raise KeyError("missing")           # → ValueError: 'missing'

# ── 12. ExceptionCollector ── batch collect exceptions ───────────────────────────
collector = ExceptionCollector()
collector.catch(int, "bad1")
collector.catch(int, "bad2")

if collector.has_errors:
    print(f"Collected {collector.count} errors")
    collector.raise_all("batch operation failed")  # → ExceptionGroup (2 sub-exceptions)

# ── 13. error_cache ── cache exceptions by call arguments ─────────────────────
@error_cache(maxsize=64)
def load(user_id: int) -> dict:
    if user_id < 0:
        raise ValueError(f"invalid id: {user_id}")
    return {"id": user_id}

with ignore(ValueError):
    load(-1)              # raises, exception cached for args (-1,)

print(load.cache_info())  # CacheInfo(hits=0, misses=1, maxsize=64, currsize=1)
load.clear_cache()

# ── 14. Custom exceptions — three layers ──────────────────────────────────────

# Layer 1: PureBaseException — code + detail only
class AppError(PureBaseException):
    code = 9000
    default_detail = "Application error."

print(AppError())         # [9000] Application error.
print(repr(AppError()))   # AppError(detail='Application error.', code=9000)

# Layer 2: ContextException — adds trace_id, context dict, exception chaining
class ServiceError(ContextException):
    code = 9001
    default_detail = "Service unavailable."

try:
    raise ConnectionError("db timeout")
except ConnectionError as cause:
    err = (
        ServiceError("downstream failed")
        .with_context(service="postgres", retries=3)
        .with_cause(cause)
    )
    print(err.trace_id)    # 'a3f1c8...' — unique per instance
    print(err.context)     # {'service': 'postgres', 'retries': 3}
    print(err.chain)       # [{'type': 'ServiceError', 'code': 9001, ...}]
    print(err.traceback)   # compact stack trace joined by |

# Layer 3: BaseErrorCodes — predefined factory methods
raise BaseErrorCodes.invalid_input("username too short")  # InvalidInputError  [1001]
raise BaseErrorCodes.access_denied()                      # AccessDeniedError  [2001]
raise BaseErrorCodes.not_found("user #42")                # NotFoundError      [3001]
raise BaseErrorCodes.runtime_failure("crash")             # RuntimeFailure     [4001]
raise BaseErrorCodes.timeout_failure()                    # TimeoutFailure     [4002]
raise BaseErrorCodes.configuration_error("missing key")   # ConfigurationError [5001]

# ── 15. BaseWarning ── structured warnings with factory methods ───────────────
class ExperimentalWarning(BaseWarning):
    default_detail = "This feature is experimental."

ExperimentalWarning.emit()                          # uses default_detail
ExperimentalWarning.emit("use at your own risk")    # custom message

BaseWarning.deprecated("use new_api() instead").emit()   # DeprecatedWarning
BaseWarning.performance("O(n²) detected").emit()         # PerformanceWarning
BaseWarning.resource("file handle leak").emit()          # ResourceUsageWarning
```

---

## Logging

`errortools.logging` is a loguru-inspired structured logger with no external dependencies.

### Quick start

```python
from errortools.logging import logger

logger.info("Server started on port {}", 8080)
logger.warning("Disk at {pct:.1f}%", pct=92.5)
logger.success("All systems operational")
```

Output (colourised in a terminal):

```
2026-04-30 08:34:21.850 | ℹ INFO     | <string>:<module>:3 - Server started on port 8080
2026-04-30 08:34:21.851 | ⚠ WARNING  | <string>:<module>:4 - Disk at 92.5%
2026-04-30 08:34:21.851 | ✔ SUCCESS  | <string>:<module>:5 - All systems operational
```

### Log levels

| Method | Level | No |
|---|---|---|
| `logger.trace()` | TRACE | 5 |
| `logger.debug()` | DEBUG | 10 |
| `logger.info()` | INFO | 20 |
| `logger.success()` | SUCCESS | 25 |
| `logger.warning()` | WARNING | 30 |
| `logger.error()` | ERROR | 40 |
| `logger.critical()` | CRITICAL | 50 |

### Sinks

Add and remove destinations at runtime. Each sink has its own level filter.

```python
from errortools.logging import logger, Level

# stream (stderr by default, auto-detects TTY colour)
logger.add(sys.stdout, level="WARNING")

# file with rotation (bytes) and retention (number of old files to keep)
sid = logger.add("logs/app.log", rotation=10_485_760, retention=5)

# any callable
logger.add(print)

# remove by id, or pass no argument to remove all
logger.remove(sid)
logger.remove()
```

### Level filtering

```python
logger.set_level("WARNING")   # or Level.WARNING or numeric 30
logger.debug("dropped")       # below threshold — not emitted
logger.warning("kept")        # at threshold — emitted
```

### Context binding

`bind()` returns a **new** logger that carries extra fields in every record. The original logger is unmodified.

```python
req_log = logger.bind(request_id="abc-123", user="alice")
req_log.info("Request received")   # record.extra contains request_id and user

# Stacking
db_log = req_log.bind(db="postgres")
db_log.debug("Query OK")           # extra: request_id, user, db
```

### Exception capture

```python
# Attach the current traceback to any log call
try:
    connect()
except ConnectionError:
    logger.exception("DB connection failed")       # logs at ERROR + traceback

# Equivalent long-hand
logger.opt(exception=True).error("DB connection failed")
```

### catch() — auto-log and suppress

```python
# As a context manager
with logger.catch():
    int("not a number")   # logged at ERROR, then suppressed

# Re-raise after logging
with logger.catch(ConnectionError, reraise=True):
    connect()

# As a decorator
@logger.catch(ValueError)
def parse(s: str) -> int:
    return int(s)
```

### Custom format string

```python
logger.add(
    "debug.log",
    fmt="{time} | {level} | {name}:{function}:{line} - {message}",
)
```

Available placeholders: `{time}`, `{level}`, `{name}`, `{file}`, `{line}`, `{function}`, `{message}`.