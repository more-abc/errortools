from functools import wraps
from typing import Callable
import warnings


def deprecated(
    version: str,
    reason: str = "This function is deprecated and will be removed in a future version.",
) -> Callable:
    """Decorator that marks a function as deprecated.

    Emits a DeprecationWarning when the decorated function is called.

    Args:
        version: The version in which the function is deprecated (e.g., "2.0").
        reason: Optional message explaining the deprecation and suggesting replacements.

    Example:
        >>> @deprecated(version="2.0", reason="Use new_func() instead.")
        ... def old_func():
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated since version {version}. {reason}"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def experimental(
    reason: str = "This function is experimental and may change in future versions.",
) -> Callable:
    """Decorator that marks a function as experimental.

    Emits a UserWarning when the decorated function is called.

    Args:
        reason: Optional message explaining the experimental status and any caveats.

    Example:
        >>> @experimental(reason="API may change without notice.")
        ... def new_feature():
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is experimental. {reason}"
            warnings.warn(msg, FutureWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
