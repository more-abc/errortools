# Decorators

## @retry()

Automatically retry a function on failure.

### Basic usage

```python
from errortools import retry

@retry(times=3, on=ConnectionError, delay=1.0)
def connect(host: str):
    # Will retry up to 3 times on ConnectionError
    # with 1 second delay between attempts
    ...
```

### Multiple exception types

```python
@retry(times=5, on=(ValueError, KeyError), delay=0.5)
def parse(data: dict) -> str:
    return data["key"]
```

### Async functions

```python
@retry(times=5, on=TimeoutError, delay=0.5)
async def fetch(url: str) -> bytes:
    ...
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `times` | `int` | Maximum number of retry attempts |
| `on` | `type \| tuple[type, ...]` | Exception type(s) to retry on |
| `delay` | `float` | Delay in seconds between retries |

## @timeout()

Cancel async functions that take too long.

```python
from errortools import timeout

@timeout(5.0)
async def fetch_data(url: str) -> bytes:
    # Raises asyncio.TimeoutError after 5 seconds
    ...
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `seconds` | `float` | Timeout duration in seconds |

## @error_cache()

Cache exceptions raised by functions, similar to `functools.lru_cache`.

```python
from errortools import error_cache, ignore

@error_cache(maxsize=64)
def load(user_id: int) -> dict:
    if user_id < 0:
        raise ValueError(f"invalid id: {user_id}")
    return {"id": user_id}

# First call raises and caches the exception
with ignore(ValueError):
    load(-1)

# Second call returns cached exception immediately
with ignore(ValueError):
    load(-1)

print(load.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=64, currsize=1)

load.clear_cache()
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `maxsize` | `int \| None` | Maximum cache size (None = unlimited) |

## @deprecated()

Mark functions as deprecated with automatic warnings.

```python
from errortools import deprecated

@deprecated("Use new_function() instead")
def old_function():
    ...

old_function()  # Emits DeprecationWarning
```

## @experimental()

Mark functions as experimental with automatic warnings.

```python
from errortools import experimental

@experimental("This API may change in future versions")
def new_feature():
    ...

new_feature()  # Emits ExperimentalWarning
```

## @suppress()

Decorator that suppresses specified exceptions and returns a default value.

```{versionadded} 3.1
```

### Basic usage

```python
from errortools import suppress

@suppress(ZeroDivisionError, default=0)
def divide(a, b):
    return a / b

divide(10, 2)  # 5.0
divide(1, 0)   # 0
```

### Multiple exception types

```python
@suppress(ValueError, KeyError, default="N/A")
def get_value(data, key):
    return data[key]

get_value({}, "missing")  # "N/A"
```

### Default is None

```python
@suppress(FileNotFoundError)
def read_config(path):
    with open(path) as f:
        return f.read()

read_config("missing.txt")  # None
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `*exceptions` | `type[BaseException]` | Exception type(s) to suppress |
| `default` | `Any` | Value to return when suppressed (default: `None`) |

## @convert()

Decorator that converts one exception type to another, preserving the exception chain.

```{versionadded} 3.1
```

### Basic usage

```python
from errortools import convert

@convert(KeyError, ValueError)
def lookup(data, key):
    return data[key]

lookup({}, "x")
# Raises: ValueError("'x'") with __cause__ = KeyError("'x'")
```

### Custom message

```python
@convert(KeyError, RuntimeError, message="configuration key not found")
def get_config(config, key):
    return config[key]

get_config({}, "db_host")
# Raises: RuntimeError("configuration key not found")
```

### Multiple source types

```python
@convert((KeyError, IndexError), ValueError)
def access(data, index):
    return data[index]

access({}, "x")    # Raises ValueError
access([], 99)     # Raises ValueError
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `type \| tuple[type, ...]` | Exception type(s) to catch |
| `target` | `type` | Exception type to raise instead |
| `message` | `str \| None` | Custom message (default: original message) |
