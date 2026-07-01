# errortools

<p align="center">
  <img src="_static/img/main.png" alt="errortools logo" width="220">
</p>

**errortools** is a lightweight Python toolkit for exception handling,
warnings, and structured logging.  It offers both high-level convenience
APIs and zero-overhead helpers for performance-critical code paths.

> Something need change or refactor? Contact email
> <errortools.docs@proton.me>

---

## At a glance

```python
from errortools import ignore, retry, BaseErrorCodes
from errortools.logging import logger

# Suppress exceptions with metadata
with ignore(KeyError) as err:
    _ = {}["missing"]
print(err.exception)        # KeyError('missing')

# Automatic retry on failure
@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str): ...

# Structured exceptions with error codes
raise BaseErrorCodes.not_found("user #42")   # NotFoundError [3001]

# Structured logging — no external dependencies
logger.info("Server started on port {}", 8080)
```

## Key features

- **Exception handling.** Context managers and decorators for graceful
  error suppression — see {doc}`user_guide/exception_handling`.
- **Batch raising.** Raise one or many exceptions at once with
  {func}`~errortools.raises` and
  {func}`~errortools.raises_all` — see
  {doc}`user_guide/raising_exceptions`.
- **Decorators.** Automatic retry (`@retry`), async timeout
  (`@timeout`), and error-caching (`@error_cache`) —
  see {doc}`user_guide/decorators`.
- **Custom exceptions.** Structured exception classes with error
  codes, trace IDs, and rich context — see
  {doc}`user_guide/custom_exceptions`.
- **Future module.** Zero-overhead exception handling for hot paths —
  see {doc}`user_guide/future_module`.
- **Logging.** A [Loguru](https://github.com/Delgan/loguru)-inspired
  structured logger with **no external dependencies** — see
  {doc}`user_guide/logging`.
- **Warnings.** A small library of `Warning` subclasses for common
  deprecation / performance scenarios — see
  {doc}`user_guide/warnings`.
- **Type safety.** Full type hints and `typing` aliases for
  IDE-friendly code — see {doc}`api_reference/index`.

## Why errortools?

| Concern | Standard library | errortools |
| --- | --- | --- |
| Suppress an exception with metadata | `try / except` boilerplate | `with ignore(KeyError) as err:` |
| Retry on failure | DIY loop | `@retry(times=3, on=ConnectionError)` |
| Structured error code | subclass `Exception` by hand | `BaseErrorCodes.not_found("user")` |
| Zero-overhead `suppress` | `contextlib.suppress` | `super_fast_ignore(ValueError)` |
| Structured logging | `logging` dictConfig | `logger.info("port {}", 8080)` |

## Installation

```bash
pip install errortools
```

For development installs and contributing see
{doc}`getting_started/installation`.

## Where to go next

```{toctree}
---
maxdepth: 2
caption: Contents
glob:
---

getting_started/index
user_guide/index
api_reference/index
cli_tools/index
examples/index
extending/index
faq/index
emeps/index
whatsnew/index
```

```{toctree}
---
hidden:
---

faq/mascot
```
