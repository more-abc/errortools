"""
Decorator-based exception handling utilities.

.. versionadded:: 3.1
"""

from functools import wraps
from typing import Callable, TypeVar, Any, Union

_F = TypeVar("_F", bound=Callable[..., Any])
_ExcTypes = Union[type[BaseException], tuple[type[BaseException], ...]]


def suppress(
    *exceptions: type[BaseException],
    default: Any = None,
) -> Callable[[_F], _F]:
    """Decorator that suppresses specified exceptions and returns a default value.

    Complement to :func:`contextlib.suppress` and the ``ignore`` context
    manager — this variant wraps an entire function definition so every
    call site automatically gets the suppression behaviour.

    .. versionadded:: 3.1

    Args:
        *exceptions: Exception type(s) to suppress.
        default: Value to return when an exception is suppressed.

    Example:
        >>> @suppress(ZeroDivisionError, default=0)
        ... def divide(a, b):
        ...     return a / b
        >>> divide(1, 0)
        0
    """
    catch = exceptions if exceptions else (Exception,)

    def decorator(func: _F) -> _F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except catch:
                return default

        return wrapper  # type: ignore[return-value]

    return decorator


def convert(
    source: _ExcTypes,
    target: type[BaseException],
    message: Union[str, None] = None,
) -> Callable[[_F], _F]:
    """Decorator that converts one exception type to another.

    Decorator counterpart of the :func:`~_errortools.raises.reraise`
    context manager — useful when every call to a function should
    perform the same exception conversion.

    .. versionadded:: 3.1

    Args:
        source: Exception type(s) to catch.
        target: Exception type to raise instead.
        message: Optional message for the new exception.
            If ``None``, uses the original message.

    Example:
        >>> @convert(KeyError, ValueError)
        ... def lookup(d, key):
        ...     return d[key]
        >>> lookup({}, "x")  # doctest: +SKIP
        ValueError: 'x'
    """

    def decorator(func: _F) -> _F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except source as exc:
                msg = message if message is not None else str(exc)
                raise target(msg) from exc

        return wrapper  # type: ignore[return-value]

    return decorator
