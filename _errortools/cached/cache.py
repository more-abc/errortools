"""A helper tool for caching exceptions raised by functions, like lru_cache."""

import functools
from typing import (
    Callable,
    Any,
    Optional,
    TypeVar,
    overload,
)

from _errortools.cached.wrapper import ErrorCacheWrapper

_T = TypeVar("_T", bound=Callable[..., Any])

# fmt: off


@overload
def error_cache(func: _T) -> ErrorCacheWrapper[_T]:
    ...


@overload
def error_cache(maxsize: Optional[int] = 128) -> Callable[[_T], ErrorCacheWrapper[_T]]:
    ...
# fmt: on


def error_cache(  # type: ignore
    func: Optional[_T] = None, maxsize: Optional[int] = 128
) -> Any:
    """
    Decorator to cache exceptions raised by a function (like functools.lru_cache).

    This decorator automatically caches exceptions thrown by the wrapped function,
    keyed by the function's arguments. If the function succeeds, the cached exception
    (if any) for those arguments is removed.

    Key features (aligned with lru_cache):
    - maxsize: Maximum number of cached errors (None = unlimited, default=128)
    - LRU eviction: Evicts least recently used entries when maxsize is reached
    - cache_info(): Returns hits/misses/maxsize/currsize stats
    - clear_cache(): Clears cache and resets statistics

    Usage (same as lru_cache):

        @error_cache  # Default maxsize=128
        def risky_func(x: int) -> int: ...

        @error_cache(maxsize=32)  # Custom maxsize
        def risky_func(x: int) -> int: ...

        @error_cache(maxsize=None)  # Unlimited cache
        def risky_func(x: int) -> int: ...

        @error_cache()  # Explicit empty args (maxsize=128)
        def risky_func(x: int) -> int: ...

    Args:
        func: The function to wrap (auto-passed when using @error_cache without args).
        maxsize: Maximum number of cached errors (None = unlimited, default=128).

    Returns:
        Wrapped function with error caching functionality.

    Raises:
        TypeError: If non-hashable arguments are passed (same as lru_cache).
    """

    def decorator(f: _T) -> ErrorCacheWrapper[_T]:
        if not callable(f):
            raise TypeError(f"Expected a callable, got {type(f).__name__} instead")

        wrapper = ErrorCacheWrapper(f, maxsize=maxsize)
        functools.update_wrapper(wrapper, f)
        return wrapper

    # Handle both @error_cache and @error_cache(...) usage
    if func is None:
        return decorator
    return decorator(func)
