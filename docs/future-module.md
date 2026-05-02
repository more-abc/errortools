# Future Module

The `errortools.future` module provides zero-overhead exception handling utilities for performance-critical code paths.

## super_fast_ignore()

Absolute minimal overhead exception suppression.

```python
from errortools.future import super_fast_ignore

with super_fast_ignore(KeyError):
    _ = {}["x"]  # Suppressed with minimal overhead
```

### Performance comparison

| Function | Overhead | Metadata | Use case |
|----------|----------|----------|----------|
| `ignore()` | Medium | Full | Development, debugging |
| `fast_ignore()` | Low | None | Production hot paths |
| `super_fast_ignore()` | Minimal | None | Critical performance paths |

## super_fast_catch()

Lightweight exception capture without metadata collection.

```python
from errortools.future import super_fast_catch

with super_fast_catch(ValueError) as ctx:
    raise ValueError("oops")

if ctx.exception is not None:
    print(ctx.exception)  # ValueError('oops')
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `exception` | `Exception \| None` | The caught exception instance |

## super_fast_reraise()

Lightweight exception type conversion.

```python
from errortools.future import super_fast_reraise

with super_fast_reraise(KeyError, ValueError):
    raise KeyError("missing")
# Raises: ValueError: 'missing'
```

### Multiple type conversion

```python
with super_fast_reraise((KeyError, IndexError), RuntimeError):
    _ = [][99]
# Raises: RuntimeError: list index out of range
```

## ExceptionCollector

Batch collect exceptions for later processing.

```python
from errortools.future import ExceptionCollector

collector = ExceptionCollector()

# Collect exceptions
collector.catch(int, "bad1")
collector.catch(int, "bad2")
collector.catch(float, "bad3")

# Check if any errors occurred
if collector.has_errors:
    print(f"Collected {collector.count} errors")
    
    # Raise all as ExceptionGroup
    collector.raise_all("batch operation failed")
```

### Methods

#### catch()

Attempt to call a function and collect any exceptions:

```python
collector.catch(callable, *args, **kwargs)
```

#### raise_all()

Raise all collected exceptions as an `ExceptionGroup`:

```python
collector.raise_all(message="Operation failed")
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `has_errors` | `bool` | `True` if any exceptions were collected |
| `count` | `int` | Number of collected exceptions |
| `exceptions` | `list[Exception]` | List of collected exception instances |

## Use cases

### Hot path optimization

Use `super_fast_ignore()` in tight loops where exception handling overhead matters:

```python
from errortools.future import super_fast_ignore

for item in large_dataset:
    with super_fast_ignore(KeyError):
        process(item["optional_field"])
```

### Batch processing

Use `ExceptionCollector` to continue processing despite errors:

```python
from errortools.future import ExceptionCollector

collector = ExceptionCollector()

for user_id in user_ids:
    collector.catch(process_user, user_id)

if collector.has_errors:
    logger.error(f"Failed to process {collector.count} users")
    collector.raise_all("Batch processing failed")
```
