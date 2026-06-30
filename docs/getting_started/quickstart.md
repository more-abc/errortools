# Quick Start

This page walks through the most common errortools idioms end-to-end.
Every example is runnable as-is — copy the snippets into a Python file
or a REPL and they will work without further setup.

```{seealso}
* {doc}`installation` — install errortools in your environment.
* {doc}`core-features` — a deeper tour of every feature shown here.
* {doc}`../api_reference/index` — complete API reference.
```

## A 30-second tour

```python
from errortools import ignore, retry
from errortools.classes import BaseErrorCodes
from errortools.logging import logger

# 1. Suppress an exception, then introspect it
with ignore(KeyError) as err:
    _ = {}["missing"]
print(err.exception)        # KeyError('missing')

# 2. Retry a flaky operation
@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str): ...

# 3. Raise a structured exception
raise BaseErrorCodes.not_found("user #42")   # NotFoundError [3001]

# 4. Structured logging
logger.info("Server started on port {}", 8080)
```

## Suppressing exceptions

### With metadata — {func}`~errortools.ignore`

{func}`~errortools.ignore` is a context manager that swallows
the exceptions you list while keeping a full record of what happened.
Bind the result to a name with `as` to read the metadata after the
block exits.

```python
from errortools import ignore

with ignore(KeyError) as err:
    _ = {}["missing"]

if err.be_ignore:
    print(f"Suppressed {err.name}: {err.exception}")
    print(f"Traceback:\n{err.traceback}")
```

```{list-table} Attributes on the bound object
:header-rows: 1
:widths: 20 80

* - Attribute
  - Description
* - ``be_ignore``
  - ``True`` if an exception was suppressed.
* - ``name``
  - Class name of the suppressed exception (``"KeyError"``).
* - ``count``
  - Number of exceptions suppressed in the block.
* - ``exception``
  - The original exception instance, or ``None``.
* - ``traceback``
  - Pre-formatted traceback string, or ``None``.
```

### Without metadata — {func}`~errortools.fast_ignore`

When you don't need any of the above metadata, use
{func}`~errortools.fast_ignore`.  It's a thin wrapper around
{func}`contextlib.suppress` and adds essentially no overhead.

```python
from errortools import fast_ignore

with fast_ignore(KeyError, IndexError):
    _ = [][0]      # suppressed, minimal overhead
```

### By base class — {func}`~errortools.ignore_subclass`

{func}`~errortools.ignore_subclass` matches every subclass of
the type you pass.  This is the most expressive form: "ignore anything
that derives from ``X``".

```python
from errortools import ignore_subclass

with ignore_subclass(LookupError):
    raise IndexError("out of range")     # IndexError ⊆ LookupError
    # IndexError is caught and discarded
```

### Warnings — {func}`~errortools.ignore_warns`

{func}`~errortools.ignore_warns` mirrors
{func}`warnings.catch_warnings` for the common case of suppressing
specific categories.

```python
from errortools import ignore_warns

with ignore_warns(DeprecationWarning):
    # Deprecated API call that would otherwise warn
    legacy_api()
```

```{seealso}
See {doc}`../user_guide/exception_handling` for the full guide,
including the "subclass vs. tuple" rule and the
{mod}`errortools.future` zero-overhead variants.
```

## Retrying and timing out

### Automatic retry — {func}`~errortoolsretry`

{func}`~errortools.retry` retries a callable on the
configured exception, with an optional delay between attempts.

```python
from errortools import retry

@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str):
    # Will retry up to 3 times on ConnectionError
    ...
```

### Async timeout — {func}`~errortools.timeout`

{func}`~errortools.timeout` cancels a coroutine
after the given deadline.  It requires an active event loop.

```python
from errortools import timeout

@timeout(5.0)
async def fetch_data(url: str):
    # Raises asyncio.TimeoutError after 5 seconds
    ...
```

## Defining custom exceptions

### With error codes — {class}`~errortools.PureBaseException`

Subclass {class}`~errortools.PureBaseException` to attach a
numeric error code and a default message.  The code is rendered in
the exception's ``__str__`` for easy log greppability.

```python
from errortools import PureBaseException

class AppError(PureBaseException):
    code = 9000
    default_detail = "Application error"

raise AppError()                 # [9000] Application error
raise AppError("disk full")      # [9000] disk full
```

### With rich context — {class}`~errortools.ContextException`

{class}`~errortools.ContextException` adds a trace ID, a free
form context dict, and a chain of contextual events.

```python
from errortools import ContextException

raise (
    ContextException("user not found")
    .with_context(request_id="abc-123", user_id=42)
    .with_cause(KeyError("user"))
)
```

### Predefined codes — {class}`~errortools.BaseErrorCodes`

For the most common cases, {class}`~errortools.BaseErrorCodes`
ships ready-made factories so you don't have to subclass anything.

```python
from errortools import BaseErrorCodes

raise BaseErrorCodes.not_found("user #42")         # [3001] user #42
raise BaseErrorCodes.invalid_input("username too short")
raise BaseErrorCodes.access_denied()
```

```{seealso}
See {doc}`../user_guide/custom_exceptions` for the complete taxonomy
of codes, the error-class hierarchy, and chaining examples.
```

## Structured logging

{mod}`errortools.logging` is a Loguru-inspired logger that ships with
the package — no extra install required.

```python
from errortools.logging import logger

logger.info("Server started on port {}", 8080)
logger.warning("Disk at {pct:.1f}%", pct=92.5)
logger.success("All systems operational")

# Add a rotating file sink
logger.add("app.log", rotation=10_000_000, retention=5)

# Bind a context that propagates to every log call
req_log = logger.bind(request_id="abc-123")
req_log.info("Request received")
```

```{seealso}
See {doc}`../user_guide/logging` for sinks, levels, formatting, and
the integration with the standard-library {mod}`logging` module.
```

## Where to go next

- {doc}`core-features` — detailed tour of every feature above.
- {doc}`../examples/index` — runnable, end-to-end examples.
- {doc}`../api_reference/index` — the complete API reference.
