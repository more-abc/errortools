# errortools
A lightweight Python exception handling utility library.

## Features
- **Raise Exceptions**: `raises()`, `raises_all()`, `reraise()` — batch raising and exception conversion
- **Catch & Suppress**: `ignore()`, `ignore_subclass()`, `ignore_warns()`, `fast_ignore()`, `super_fast_ignore()`, `timeout()` — graceful suppression of exceptions and warnings
- **Exception Caching**: `error_cache` — cache exceptions raised by functions (similar to `lru_cache`)
- **Custom Exceptions**: `PureBaseException`, `ContextException`, `BaseErrorCodes`, `BaseWarning` — structured exception classes with error codes, trace IDs, and context
- **Attribute Error Mixin**: Customize error behavior for attribute access, assignment, and deletion
- **Type Aliases**: `ExceptionType`, `AnyErrorCode`, `BaseErrorCodesType`, and more

## Installation
```bash
pip install errortools
```

---

## Example

```python
import warnings
from errortools import (
    ignore, fast_ignore, ignore_subclass, ignore_warns, timeout,
    reraise, raises, raises_all, assert_raises,
    error_cache,
    PureBaseException, ContextException, BaseErrorCodes, BaseWarning,
)
from errortools.future import super_fast_ignore

# ── 1. ignore ── context manager with full metadata ──────────────────────────
with ignore(KeyError) as err:
    _ = {}["missing"]

assert err.be_ignore          # True  — was suppressed
assert err.name == "KeyError" # exception class name
assert err.count == 1         # how many times suppressed
assert err.exception          # the original KeyError instance
assert err.traceback          # full formatted traceback string

# ignore as a decorator
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

# ── 6. reraise ── convert exception types on the fly ─────────────────────────
with reraise(KeyError, ValueError):
    raise KeyError("missing key")      # → ValueError: 'missing key'

with reraise((KeyError, IndexError), RuntimeError):
    _ = [][99]                         # → RuntimeError: list index out of range

# ── 7. raises / raises_all ── batch raise ────────────────────────────────────
raises([ValueError], ["bad input"])    # → ValueError: bad input

raises_all(
    [ValueError, TypeError],
    ["bad input"],
)                                      # → ExceptionGroup (2 sub-exceptions)

# ── 8. assert_raises ── assert a callable raises ─────────────────────────────
exc = assert_raises(int, [ValueError], "not-a-number")
print(exc)   # invalid literal for int() with base 10: 'not-a-number'

# ── 9. error_cache ── cache exceptions by call arguments ─────────────────────
@error_cache(maxsize=64)
def load(user_id: int) -> dict:
    if user_id < 0:
        raise ValueError(f"invalid id: {user_id}")
    return {"id": user_id}

with ignore(ValueError):
    load(-1)              # raises, exception cached for args (-1,)

print(load.cache_info())  # CacheInfo(hits=0, misses=1, maxsize=64, currsize=1)
load.clear_cache()

# ── 10. Custom exceptions — three layers ──────────────────────────────────────

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

# ── 11. BaseWarning ── structured warnings with factory methods ───────────────
class ExperimentalWarning(BaseWarning):
    default_detail = "This feature is experimental."

ExperimentalWarning.emit()                          # uses default_detail
ExperimentalWarning.emit("use at your own risk")    # custom message

BaseWarning.deprecated("use new_api() instead").emit()   # DeprecatedWarning
BaseWarning.performance("O(n²) detected").emit()         # PerformanceWarning
BaseWarning.resource("file handle leak").emit()          # ResourceUsageWarning
```