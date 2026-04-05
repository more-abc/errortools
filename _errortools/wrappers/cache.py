from collections import OrderedDict
from collections.abc import Hashable, Callable
from typing import Any, Generic, TypeVar, Optional, TypeAlias, NamedTuple

_T = TypeVar("_T", bound=Callable[..., Any])
_Key: TypeAlias = tuple[
    str, tuple[Hashable, ...], tuple[tuple[Hashable, Hashable], ...]
]


class CacheInfo(NamedTuple):
    """Cache statistics, compatible with functools.lru_cache CacheInfo."""

    hits: int
    misses: int
    maxsize: int | None
    currsize: int


class ErrorCacheWrapper(Generic[_T]):
    """Wrapper class for error-cached functions."""

    def __init__(self, func: _T, maxsize: int | None = 128) -> None:
        self.__wrapped__ = func  # Required for inspect module compatibility
        self._func_name = func.__name__

        # Validate maxsize
        if maxsize is not None and maxsize < 0:
            raise ValueError(
                f"maxsize must be None or a non-negative integer, got {maxsize!r}"
            )
        self._maxsize = maxsize
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
            if cache_key in self._cache:
                self._hits += 1
            else:
                self._misses += 1

            # Store in cache only if maxsize allows it (maxsize=0 means no caching)
            if self._maxsize != 0:
                self._cache[cache_key] = exc
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

    def cache_info(self) -> CacheInfo:
        """Return cache statistics as a named tuple (compatible with lru_cache)."""
        return CacheInfo(
            hits=self._hits,
            misses=self._misses,
            maxsize=self._maxsize,
            currsize=len(self._cache),
        )
