# errortools

<p align="center">
  <img src="_static/img/main.png" alt="errortools logo" width="220">
</p>

A lightweight Python exception handling utility library.

## Overview

**errortools** provides a comprehensive toolkit for working with Python exceptions, warnings, and logging. It offers both high-level convenience functions and low-overhead utilities for performance-critical code.

## Key Features

- **Exception Handling**: Context managers and decorators for graceful error suppression
- **Batch Operations**: Raise multiple exceptions at once with `raises_all()` and `ExceptionGroup`
- **Retry & Timeout**: Automatic retry logic and async timeout decorators
- **Custom Exceptions**: Structured exception classes with error codes, trace IDs, and context
- **Future Module**: Zero-overhead exception handling for hot paths
- **Logging**: Loguru-inspired structured logger with no external dependencies
- **Type Safety**: Full type hints and type aliases for better IDE support

## Quick Example

```python
from errortools import ignore, retry, BaseErrorCodes
from errortools.logging import logger

# Suppress exceptions with metadata
with ignore(KeyError) as err:
    _ = {}["missing"]
    
print(err.be_ignore)  # True
print(err.exception)  # KeyError('missing')

# Automatic retry on failure
@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str):
    ...

# Structured exceptions with error codes
raise BaseErrorCodes.not_found("user #42")  # NotFoundError [3001]

# Structured logging
logger.info("Server started on port {}", 8080)
```

## Installation

```bash
pip install errortools
```

## Documentation Structure

```{toctree}
---
maxdepth: 2
caption: Contents
---
installation
quickstart
core-features
exception-handling
raising-exceptions
decorators
custom-exceptions
warnings
future-module
logging
api-reference
examples
mascot
```
