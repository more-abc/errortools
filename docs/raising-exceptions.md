# Raising Exceptions

## raises()

Raise exceptions from lists of exception types and messages.

```python
from errortools import raises

# Single exception
raises([ValueError], ["Invalid input"])
# Raises: ValueError: Invalid input

# Multiple exceptions (raises first)
raises([ValueError, TypeError], ["bad value", "bad type"])
# Raises: ValueError: bad value
```

## raises_all()

Batch raise multiple exceptions as an `ExceptionGroup`.

```python
from errortools import raises_all

raises_all(
    [ValueError, TypeError],
    ["Invalid input", "Wrong type"],
)
# Raises: ExceptionGroup (2 sub-exceptions)
#   ValueError: Invalid input
#   TypeError: Wrong type
```

## reraise()

Convert exception types on the fly.

### Single type conversion

```python
from errortools import reraise

with reraise(KeyError, ValueError):
    raise KeyError("missing key")
# Raises: ValueError: 'missing key'
```

### Multiple type conversion

```python
with reraise((KeyError, IndexError), RuntimeError):
    _ = [][99]
# Raises: RuntimeError: list index out of range
```

### Preserving original traceback

The original exception is preserved in the `__cause__` attribute:

```python
try:
    with reraise(KeyError, ValueError):
        raise KeyError("missing")
except ValueError as e:
    print(e.__cause__)  # KeyError('missing')
```

## assert_raises()

Assert that a callable raises specific exceptions. Useful for testing.

```python
from errortools import assert_raises

# Assert int() raises ValueError
exc = assert_raises(int, [ValueError], "not-a-number")
print(exc)  # invalid literal for int() with base 10: 'not-a-number'

# With multiple arguments
exc = assert_raises(lambda: [][0], [IndexError])
print(exc)  # list index out of range
```

### Return value

Returns the caught exception instance, or raises `AssertionError` if the expected exception was not raised.
