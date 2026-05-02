# Quick Start

## Basic Exception Handling

### Suppress exceptions with metadata

```python
from errortools import ignore

with ignore(KeyError) as err:
    _ = {}["missing"]

if err.be_ignore:
    print(f"Suppressed {err.name}: {err.exception}")
    print(f"Traceback: {err.traceback}")
```

### Fast suppression (no metadata)

```python
from errortools import fast_ignore

with fast_ignore(KeyError, IndexError):
    _ = [][0]  # suppressed, minimal overhead
```

## Retry and Timeout

### Automatic retry

```python
from errortools import retry

@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str):
    # Will retry up to 3 times on ConnectionError
    ...
```

### Async timeout

```python
from errortools import timeout

@timeout(5.0)
async def fetch_data(url: str):
    # Raises asyncio.TimeoutError after 5 seconds
    ...
```

## Custom Exceptions

### Simple error codes

```python
from errortools import PureBaseException

class AppError(PureBaseException):
    code = 9000
    default_detail = "Application error"

raise AppError()  # [9000] Application error
```

### Built-in error codes

```python
from errortools import BaseErrorCodes

raise BaseErrorCodes.not_found("user #42")
raise BaseErrorCodes.invalid_input("username too short")
raise BaseErrorCodes.access_denied()
```

## Logging

```python
from errortools.logging import logger

logger.info("Server started on port {}", 8080)
logger.warning("Disk at {pct:.1f}%", pct=92.5)
logger.success("All systems operational")

# Add file sink
logger.add("app.log", rotation=10_000_000, retention=5)

# Bind context
req_log = logger.bind(request_id="abc-123")
req_log.info("Request received")
```

## Next Steps

- Explore [Core Features](core-features.md) for detailed documentation
- Check [Examples](examples.md) for real-world use cases
- Review [API Reference](api-reference.md) for complete API documentation
