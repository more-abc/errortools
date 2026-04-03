from collections import OrderedDict
from collections.abc import Hashable, Callable
from typing import Any, Generic, TypeVar, Optional, TypeAlias

_T = TypeVar("_T", bound=Callable[..., Any])
_Key: TypeAlias = tuple[
    str, tuple[Hashable, ...], tuple[tuple[Hashable, Hashable], ...]
]


class ErrorCacheWrapper(Generic[_T]):
    """Wrapper class for error-cached functions."""

    def __init__(self, func: _T, maxsize: Optional[int] = 128) -> None:
        self.__wrapped__ = func  # Required for inspect module compatibility
        self._func_name = func.__name__

        # LRU cache with maxsize support (OrderedDict preserves access order)
        self._maxsize = maxsize if (maxsize is None or maxsize > 0) else None
        self._cache: OrderedDict[_Key, Exception] = OrderedDict()

        # Cache statistics
        self._hits = 0
        self._misses = 0

    def __call__(self, *args: Hashable, **kwargs: Hashable) -> Any:
        """Execute the wrapped function and cache exceptions if raised (with LRU)."""
        cache_key = self._make_key(args, kwargs)

        try:
            result = self.__wrapped__(*args, **kwargs)
        except Exception as exc:
            # Cache exception and enforce LRU eviction
            self._cache[cache_key] = exc
            self._misses += 1

            # Evict least recently used if maxsize is exceeded
            if self._maxsize is not None and len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)  # FIFO = LRU for insert order
            raise
        else:
            # Auto-clear cache for successful calls
            self._cache.pop(cache_key, None)
            return result

    def _make_key(
        self, args: tuple[Hashable, ...], kwargs: dict[str, Hashable]
    ) -> _Key:
        """Generate a unique hashable key."""
        sorted_kwargs = tuple(sorted(kwargs.items()))
        return (self._func_name, args, sorted_kwargs)

    # ---------------------- Cache control methods (like lru_cache) ----------------------
    def get_cached_error(
        self, *args: Hashable, **kwargs: Hashable
    ) -> Optional[Exception]:
        """Get the cached exception for the given arguments (if exists)."""
        cache_key = self._make_key(args, kwargs)
        if cache_key in self._cache:
            self._hits += 1
            self._cache.move_to_end(cache_key)  # Update LRU order (most recent)
            return self._cache[cache_key]
        return None

    def clear_cache(self) -> None:
        """Clear all cached exceptions and reset statistics."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def cache_info(self) -> str:
        """Return cache statistics."""
        return (
            f"ErrorCacheInfo(hits={self._hits}, misses={self._misses}, "
            f"maxsize={self._maxsize}, currsize={len(self._cache)})"
        )
