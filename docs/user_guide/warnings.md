# Warnings

errortools provides structured warning classes with factory methods for common warning types.

## BaseWarning

Base class for all structured warnings.

```python
from errortools import BaseWarning

class ExperimentalWarning(BaseWarning):
    default_detail = "This feature is experimental"

# Emit with default message
ExperimentalWarning.emit()

# Emit with custom message
ExperimentalWarning.emit("use at your own risk")
```

### Factory methods

BaseWarning provides factory methods for common warning types:

```python
from errortools import BaseWarning

# Deprecation warning
BaseWarning.deprecated("use new_api() instead").emit()

# Performance warning
BaseWarning.performance("O(n²) detected").emit()

# Resource usage warning
BaseWarning.resource("file handle leak").emit()

# Runtime behaviour warning
BaseWarning.runtime_behaviour("unexpected state").emit()

# Configuration warning
BaseWarning.configuration("missing optional key").emit()
```

## Predefined warning classes

### DeprecatedWarning

For deprecated features:

```python
from errortools import DeprecatedWarning

DeprecatedWarning.emit("old_function() is deprecated, use new_function()")
```

### PerformanceWarning

For performance concerns:

```python
from errortools import PerformanceWarning

PerformanceWarning.emit("Large dataset detected, consider pagination")
```

### ResourceUsageWarning

For resource usage issues:

```python
from errortools import ResourceUsageWarning

ResourceUsageWarning.emit("Memory usage exceeds 80%")
```

### RuntimeBehaviourWarning

For unexpected runtime behaviour:

```python
from errortools import RuntimeBehaviourWarning

RuntimeBehaviourWarning.emit("Fallback to default configuration")
```

### ConfigurationWarning

For configuration issues:

```python
from errortools import ConfigurationWarning

ConfigurationWarning.emit("Optional setting 'debug' not found")
```

## Suppressing warnings

Use `ignore_warns()` to suppress warnings:

```python
from errortools import ignore_warns, DeprecatedWarning

with ignore_warns(DeprecatedWarning):
    DeprecatedWarning.emit("old api")  # Suppressed

with ignore_warns():  # Suppress all warnings
    DeprecatedWarning.emit("anything")
```

## Integration with @deprecated and @experimental

The warning classes integrate with the decorator utilities:

```python
from errortools import deprecated, experimental

@deprecated("Use new_function() instead")
def old_function():
    pass  # Emits DeprecatedWarning when called

@experimental("This API may change")
def new_feature():
    pass  # Emits ExperimentalWarning when called
```
