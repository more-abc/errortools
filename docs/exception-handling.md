# Exception Handling

## ignore()

Context manager and decorator for suppressing exceptions with full metadata tracking.

### As a context manager

```python
from errortools import ignore

with ignore(KeyError) as err:
    _ = {}["missing"]

print(err.be_ignore)    # True
print(err.name)         # "KeyError"
print(err.count)        # 1
print(err.exception)    # KeyError('missing')
print(err.traceback)    # Full traceback string
```

### As a decorator

```python
@ignore(ValueError, TypeError)
def parse(x: str) -> int:
    return int(x)

result = parse("bad")  # Returns None instead of raising
```

### Metadata attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `be_ignore` | `bool` | `True` if an exception was suppressed |
| `name` | `str \| None` | Class name of the suppressed exception |
| `count` | `int` | Number of suppressed exceptions |
| `exception` | `Exception \| None` | The original exception instance |
| `traceback` | `str \| None` | Formatted traceback string |

## fast_ignore()

Lightweight suppression without metadata collection. Use for hot paths where you don't need debugging information.

```python
from errortools import fast_ignore

with fast_ignore(KeyError, IndexError):
    _ = [][0]  # Suppressed, minimal overhead
```

## ignore_subclass()

Suppress any subclass of a base exception type.

```python
from errortools import ignore_subclass

with ignore_subclass(LookupError):
    raise IndexError("out of range")  # IndexError ⊆ LookupError — suppressed
    raise KeyError("missing")         # KeyError ⊆ LookupError — suppressed
```

## ignore_warns()

Suppress warnings by category.

```python
from errortools import ignore_warns
import warnings

with ignore_warns(DeprecationWarning):
    warnings.warn("old api", DeprecationWarning)  # Suppressed

with ignore_warns():  # Suppress all warnings
    warnings.warn("anything")
```

## Performance comparison

| Function | Overhead | Metadata | Use case |
|----------|----------|----------|----------|
| `ignore()` | Medium | Full | Development, debugging |
| `fast_ignore()` | Low | None | Production hot paths |
| `super_fast_ignore()` | Minimal | None | Critical performance paths |

See [Future Module](future-module.md) for `super_fast_ignore()`.
