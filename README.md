# errortools
A lightweight Python exception handling utility library.

## Features
- **Raise Exceptions**: `raises()`, `raises_all()`, `reraise()` support batch raising and exception conversion
- **Catch & Suppress**: `ignore()`, `ignore_subclass()`, `ignore_warns()` enable graceful suppression of exceptions and warnings
- **Exception Caching**: `error_cache` caches exceptions thrown by functions (similar to `lru_cache`)
- **Custom Exceptions**: `BaseErrorCodes` supports structured exception classes with error codes
- **Attribute Error Mixin**: Customize error behavior for attribute access, assignment, and deletion

## Installation
```bash
pip install errortools
``` 

## Quick Examples
```python
from errortools import ignore, reraise

# Silently ignore KeyError
with ignore(KeyError):
    {}["missing"]  # No error raised

# Reraise KeyError as ValueError
with reraise(KeyError, ValueError):
    raise KeyError("x")  # Raises ValueError instead
```

- **Go explore more great stuff in code!** 

***NOTES***: explore many many new things!