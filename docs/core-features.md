# Core Features

errortools provides a comprehensive set of utilities for exception handling, organized into several categories:

## Exception Handling

Tools for catching and suppressing exceptions gracefully:

- **`ignore()`** - Context manager/decorator with full metadata tracking
- **`fast_ignore()`** - Lightweight suppression without metadata
- **`ignore_subclass()`** - Suppress any subclass of a base exception
- **`ignore_warns()`** - Suppress warnings

See [Exception Handling](exception-handling.md) for details.

## Raising Exceptions

Utilities for raising and converting exceptions:

- **`raises()`** - Raise exceptions from lists
- **`raises_all()`** - Batch raise multiple exceptions as ExceptionGroup
- **`reraise()`** - Convert exception types on the fly
- **`assert_raises()`** - Assert a callable raises specific exceptions

See [Raising Exceptions](raising-exceptions.md) for details.

## Decorators

Function decorators for common patterns:

- **`@retry()`** - Automatic retry on failure
- **`@timeout()`** - Async function timeout
- **`@error_cache()`** - Cache exceptions by arguments
- **`@deprecated()`** - Mark functions as deprecated
- **`@experimental()`** - Mark functions as experimental

See [Decorators](decorators.md) for details.

## Custom Exceptions

Structured exception classes with error codes and context:

- **`PureBaseException`** - Base class with error codes
- **`ContextException`** - Adds trace IDs and context dict
- **`BaseErrorCodes`** - Predefined error code factory

See [Custom Exceptions](custom-exceptions.md) for details.

## Warnings

Structured warning classes with factory methods:

- **`BaseWarning`** - Base warning class
- **`DeprecatedWarning`** - Deprecation warnings
- **`PerformanceWarning`** - Performance warnings
- **`ResourceUsageWarning`** - Resource usage warnings

See [Warnings](warnings.md) for details.
