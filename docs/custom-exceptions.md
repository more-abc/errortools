# Custom Exceptions

errortools provides three layers of custom exception classes, each building on the previous one.

## Layer 1: PureBaseException

Base exception class with error codes and default messages.

```python
from errortools import PureBaseException

class AppError(PureBaseException):
    code = 9000
    default_detail = "Application error occurred"

raise AppError()
# Output: [9000] Application error occurred

raise AppError("Custom message")
# Output: [9000] Custom message
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | `int` | Error code (class attribute) |
| `default_detail` | `str` | Default error message (class attribute) |
| `detail` | `str` | Actual error message (instance attribute) |

### String representation

```python
err = AppError("Something went wrong")
print(err)         # [9000] Something went wrong
print(repr(err))   # AppError(detail='Something went wrong', code=9000)
```

## Layer 2: ContextException

Extends `PureBaseException` with trace IDs, context dictionaries, and exception chaining.

```python
from errortools import ContextException

class ServiceError(ContextException):
    code = 9001
    default_detail = "Service unavailable"

try:
    raise ConnectionError("db timeout")
except ConnectionError as cause:
    err = (
        ServiceError("downstream failed")
        .with_context(service="postgres", retries=3)
        .with_cause(cause)
    )
    raise err
```

### Additional attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `trace_id` | `str` | Unique identifier per instance |
| `context` | `dict` | Additional context data |
| `chain` | `list[dict]` | Exception chain information |
| `traceback` | `str` | Compact stack trace |

### Methods

#### with_context()

Add context data to the exception:

```python
err = ServiceError("failed").with_context(
    service="api",
    endpoint="/users",
    status_code=500
)
print(err.context)
# {'service': 'api', 'endpoint': '/users', 'status_code': 500}
```

#### with_cause()

Chain exceptions together:

```python
try:
    raise ValueError("original error")
except ValueError as cause:
    err = ServiceError("wrapped").with_cause(cause)
    print(err.chain)
    # [{'type': 'ServiceError', 'code': 9001, ...}]
```

## Layer 3: BaseErrorCodes

Predefined exception factory with common error codes.

```python
from errortools import BaseErrorCodes

# Invalid input [1001]
raise BaseErrorCodes.invalid_input("username too short")

# Access denied [2001]
raise BaseErrorCodes.access_denied()

# Not found [3001]
raise BaseErrorCodes.not_found("user #42")

# Runtime failure [4001]
raise BaseErrorCodes.runtime_failure("crash")

# Timeout failure [4002]
raise BaseErrorCodes.timeout_failure()

# Configuration error [5001]
raise BaseErrorCodes.configuration_error("missing key")
```

### Predefined error codes

| Factory Method | Exception Class | Code | Description |
|----------------|-----------------|------|-------------|
| `invalid_input()` | `InvalidInputError` | 1001 | Invalid input data |
| `access_denied()` | `AccessDeniedError` | 2001 | Access denied |
| `not_found()` | `NotFoundError` | 3001 | Resource not found |
| `runtime_failure()` | `RuntimeFailure` | 4001 | Runtime failure |
| `timeout_failure()` | `TimeoutFailure` | 4002 | Timeout failure |
| `configuration_error()` | `ConfigurationError` | 5001 | Configuration error |

### Direct usage

You can also use the exception classes directly:

```python
from errortools import NotFoundError, InvalidInputError

raise NotFoundError("user not found")
raise InvalidInputError("invalid email format")
```
