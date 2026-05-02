# API Reference

Complete API documentation for errortools.

## Exception Handling

### ignore()

```python
ignore(*exceptions: type[Exception]) -> IgnoreContext
```

Context manager and decorator for suppressing exceptions with metadata.

**Parameters:**
- `*exceptions`: Exception types to suppress

**Returns:** `IgnoreContext` with attributes:
- `be_ignore: bool` - Whether an exception was suppressed
- `name: str | None` - Exception class name
- `count: int` - Number of suppressed exceptions
- `exception: Exception | None` - The exception instance
- `traceback: str | None` - Formatted traceback

### fast_ignore()

```python
fast_ignore(*exceptions: type[Exception]) -> contextlib.suppress
```

Lightweight exception suppression without metadata.

### ignore_subclass()

```python
ignore_subclass(base: type[Exception]) -> IgnoreContext
```

Suppress any subclass of a base exception type.

### ignore_warns()

```python
ignore_warns(*categories: type[Warning]) -> warnings.catch_warnings
```

Suppress warnings by category.

## Raising Exceptions

### raises()

```python
raises(
    exceptions: list[type[Exception]],
    messages: list[str]
) -> None
```

Raise exceptions from lists (raises first exception).

### raises_all()

```python
raises_all(
    exceptions: list[type[Exception]],
    messages: list[str]
) -> None
```

Batch raise multiple exceptions as ExceptionGroup.

### reraise()

```python
reraise(
    from_exc: type[Exception] | tuple[type[Exception], ...],
    to_exc: type[Exception]
) -> contextlib.AbstractContextManager
```

Convert exception types on the fly.

### assert_raises()

```python
assert_raises(
    callable: Callable,
    exceptions: list[type[Exception]],
    *args,
    **kwargs
) -> Exception
```

Assert a callable raises specific exceptions.

## Decorators

### @retry()

```python
retry(
    times: int,
    on: type[Exception] | tuple[type[Exception], ...],
    delay: float = 0.0
) -> Callable
```

Automatically retry on failure.

### @timeout()

```python
timeout(seconds: float) -> Callable
```

Cancel async functions after timeout.

### @error_cache()

```python
error_cache(maxsize: int | None = 128) -> Callable
```

Cache exceptions by function arguments.

### @deprecated()

```python
deprecated(message: str) -> Callable
```

Mark functions as deprecated.

### @experimental()

```python
experimental(message: str) -> Callable
```

Mark functions as experimental.

## Custom Exceptions

### PureBaseException

```python
class PureBaseException(Exception):
    code: int
    default_detail: str
    detail: str
```

Base exception with error codes.

### ContextException

```python
class ContextException(PureBaseException):
    trace_id: str
    context: dict
    chain: list[dict]
    traceback: str
    
    def with_context(self, **kwargs) -> Self
    def with_cause(self, cause: Exception) -> Self
```

Exception with trace IDs and context.

### BaseErrorCodes

Factory class for predefined error codes:

```python
class BaseErrorCodes:
    @staticmethod
    def invalid_input(detail: str = "") -> InvalidInputError
    
    @staticmethod
    def access_denied(detail: str = "") -> AccessDeniedError
    
    @staticmethod
    def not_found(detail: str = "") -> NotFoundError
    
    @staticmethod
    def runtime_failure(detail: str = "") -> RuntimeFailure
    
    @staticmethod
    def timeout_failure(detail: str = "") -> TimeoutFailure
    
    @staticmethod
    def configuration_error(detail: str = "") -> ConfigurationError
```

## Warnings

### BaseWarning

```python
class BaseWarning(UserWarning):
    default_detail: str
    
    @classmethod
    def emit(cls, detail: str = "") -> None
    
    @staticmethod
    def deprecated(detail: str) -> DeprecatedWarning
    
    @staticmethod
    def performance(detail: str) -> PerformanceWarning
    
    @staticmethod
    def resource(detail: str) -> ResourceUsageWarning
    
    @staticmethod
    def runtime_behaviour(detail: str) -> RuntimeBehaviourWarning
    
    @staticmethod
    def configuration(detail: str) -> ConfigurationWarning
```

## Future Module

### super_fast_ignore()

```python
super_fast_ignore(*exceptions: type[Exception]) -> contextlib.suppress
```

Minimal overhead exception suppression.

### super_fast_catch()

```python
super_fast_catch(exception: type[Exception]) -> CatchContext
```

Lightweight exception capture.

**Returns:** `CatchContext` with attribute:
- `exception: Exception | None`

### super_fast_reraise()

```python
super_fast_reraise(
    from_exc: type[Exception] | tuple[type[Exception], ...],
    to_exc: type[Exception]
) -> contextlib.AbstractContextManager
```

Lightweight exception type conversion.

### ExceptionCollector

```python
class ExceptionCollector:
    has_errors: bool
    count: int
    exceptions: list[Exception]
    
    def catch(self, callable: Callable, *args, **kwargs) -> None
    def raise_all(self, message: str) -> None
```

Batch exception collector.

## Logging

### logger

```python
logger.trace(message: str, *args, **kwargs) -> None
logger.debug(message: str, *args, **kwargs) -> None
logger.info(message: str, *args, **kwargs) -> None
logger.success(message: str, *args, **kwargs) -> None
logger.warning(message: str, *args, **kwargs) -> None
logger.error(message: str, *args, **kwargs) -> None
logger.critical(message: str, *args, **kwargs) -> None

logger.add(
    sink: str | IO | Callable,
    level: str | int = "DEBUG",
    rotation: int | None = None,
    retention: int | None = None
) -> int

logger.remove(sink_id: int | None = None) -> None
logger.set_level(level: str | int) -> None
logger.bind(**kwargs) -> BaseLogger
logger.exception(message: str) -> None
logger.opt(exception: bool = False) -> BaseLogger
logger.catch(
    *exceptions: type[Exception],
    reraise: bool = False
) -> contextlib.AbstractContextManager
```

### Level

```python
class Level(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
```

## Type Aliases

```python
ExceptionType = type[Exception]
WarningType = type[Warning]
AnyErrorCode = int | str
BaseErrorCodesType = type[BaseErrorCodes]
PureBaseExceptionType = type[PureBaseException]
ContextExceptionType = type[ContextException]
TracebackType = types.TracebackType
FrameType = types.FrameType
```
