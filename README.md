# errortools

A lightweight Python exception handling utility library.

[![Code Style: Google](https://img.shields.io/badge/style-google-3666d6.svg)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings)
[![PyPI Version](https://img.shields.io/pypi/v/errortools)](https://pypi.org/project/errortools/)
[![Python Versions](https://img.shields.io/pypi/pyversions/errortools)](https://pypi.org/project/errortools/)
![This week commits](https://img.shields.io/github/commit-activity/w/more-abc/errortools)
![This month commits](https://img.shields.io/github/commit-activity/m/more-abc/errortools)
![Past year commits](https://img.shields.io/github/commit-activity/y/more-abc/errortools)
![Total commits badge](https://img.shields.io/github/commit-activity/t/more-abc/errortools)
![OS support](https://img.shields.io/badge/OS-macOS%20Linux%20Windows-red)

## Installation

```bash
pip install errortools
```

## Features

- **Suppress**: `ignore()`, `super_fast_ignore()`, `@suppress()` — silence exceptions gracefully
- **Retry & Timeout**: `@retry()`, `@timeout()` — auto retry with delay, async timeout
- **Raise & Convert**: `raises()`, `reraise()`, `@convert()` — batch raise, type conversion
- **Catch & Collect**: `super_fast_catch()`, `ExceptionCollector` — inspect or batch exceptions
- **Caching**: `@error_cache` — LRU exception cache, like `functools.lru_cache`
- **Custom Exceptions**: `PureBaseException`, `ContextException`, `BaseErrorCodes`
- **Logging**: structured logger with sinks, context binding, and exception capture

## Quick Start

```python
from errortools import ignore, retry, reraise, error_cache, suppress, convert
from errortools.future import super_fast_ignore, super_fast_catch, ExceptionCollector

# ── Suppress ─────────────────────────────────────────────────
with ignore(KeyError) as err:               # full metadata
    _ = {}["missing"]
# err.be_ignore=True, err.name='KeyError', err.traceback=...

with super_fast_ignore(ValueError):         # zero-overhead
    int("bad")

@suppress(ZeroDivisionError, default=0)     # decorator form
def divide(a, b): return a / b

# ── Retry ────────────────────────────────────────────────────
@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str): ...

# ── Convert ──────────────────────────────────────────────────
@convert(KeyError, ValueError)              # decorator
def lookup(d, key): return d[key]

with reraise(KeyError, ValueError):         # context manager
    raise KeyError("x")                     # → ValueError

# ── Catch & Collect ──────────────────────────────────────────
with super_fast_catch(ValueError) as ctx:
    raise ValueError("oops")
# ctx.exception → ValueError('oops')

collector = ExceptionCollector()
collector.catch(int, "bad1")
collector.catch(int, "bad2")
collector.raise_all()                       # → ExceptionGroup

# ── Cache ────────────────────────────────────────────────────
@error_cache(maxsize=64)
def load(uid: int):
    if uid < 0: raise ValueError(f"invalid: {uid}")
    return {"id": uid}
```

## Custom Exceptions

```python
from errortools import PureBaseException, ContextException, BaseErrorCodes

class AppError(PureBaseException):
    code = 9000
    default_detail = "Application error."

err = ContextException("failed").with_context(service="db")
raise BaseErrorCodes.not_found("user #42")  # NotFoundError [3001]
```

## Logging

```python
from errortools.logging import logger

logger.info("Server started on port {}", 8080)
logger.add("app.log", rotation=10_485_760, retention=5)
with logger.catch():
    int("not a number")                     # logged + suppressed
```

## Documentation

Full docs: [docs](https://errortools.readthedocs.io) | License: [LICENSE](LICENSE.txt)
