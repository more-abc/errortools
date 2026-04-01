"""Tests for _errortools/cached — error_cache decorator and ErrorCacheWrapper."""

import pytest

from _errortools.cached.cache import error_cache

# =============================================================================
# Helpers
# =============================================================================


def _make_counter_func(raise_on=None):
    """Return a function that counts calls and optionally raises."""
    call_count = [0]

    def f(x):
        call_count[0] += 1
        if raise_on is not None and x == raise_on:
            raise ValueError(f"bad value: {x}")
        return x * 2

    f.call_count = call_count  # type: ignore
    return f


# =============================================================================
# error_cache — basic decoration patterns
# =============================================================================


class TestErrorCacheDecorator:
    def test_bare_decorator(self):
        @error_cache
        def f(x):
            return x

        assert f(3) == 6 or f(3) == 3  # just test it's callable and returns

    def test_decorator_with_parens(self):
        @error_cache()
        def f(x):
            return x * 2

        assert f(5) == 10

    def test_decorator_with_maxsize(self):
        @error_cache(maxsize=5)
        def f(x):
            if x < 0:
                raise ValueError("negative")
            return x

        assert f(1) == 1

    def test_wrapper_has_correct_name(self):
        @error_cache
        def my_func(x):
            return x

        assert my_func.__name__ == "my_func"  # type: ignore

    def test_wrapped_attribute(self):
        def inner(x):
            return x

        wrapped = error_cache(inner)
        assert wrapped.__wrapped__ is inner


# =============================================================================
# error_cache — caching on exception
# =============================================================================


class TestErrorCacheCaching:
    def test_exception_is_cached(self):
        @error_cache
        def f(x):
            if x == 0:
                raise ZeroDivisionError("zero")
            return x

        with pytest.raises(ZeroDivisionError):
            f(0)

        # Now retrieve from cache
        cached = f.get_cached_error(0)
        assert isinstance(cached, ZeroDivisionError)

    def test_miss_increments_stat(self):
        @error_cache
        def f(x):
            raise RuntimeError("always fails")

        with pytest.raises(RuntimeError):
            f(42)

        info = f.cache_info()
        assert "misses=1" in info

    def test_hit_increments_stat(self):
        @error_cache
        def f(x):
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            f(99)

        f.get_cached_error(99)  # counts as a hit
        info = f.cache_info()
        assert "hits=1" in info

    def test_successful_call_clears_cached_error(self):
        call_no = [0]

        @error_cache
        def f(x):
            call_no[0] += 1
            if call_no[0] == 1:
                raise ValueError("first call fails")
            return x * 2

        with pytest.raises(ValueError):
            f(7)

        assert f.get_cached_error(7) is not None  # cached

        result = f(7)  # second call succeeds → cache entry removed
        assert result == 14
        assert f.get_cached_error(7) is None

    def test_different_args_cached_separately(self):
        @error_cache
        def f(x):
            raise RuntimeError(f"fail:{x}")

        with pytest.raises(RuntimeError):
            f(1)
        with pytest.raises(RuntimeError):
            f(2)

        assert f.get_cached_error(1) is not None
        assert f.get_cached_error(2) is not None

    def test_get_cached_error_none_for_no_error(self):
        @error_cache
        def f(x):
            return x

        f(10)
        assert f.get_cached_error(10) is None

    def test_clear_cache_resets_stats(self):
        @error_cache
        def f(x):
            raise ValueError("fail")

        with pytest.raises(ValueError):
            f(1)

        f.clear_cache()
        info = f.cache_info()
        assert "hits=0" in info
        assert "misses=0" in info
        assert "currsize=0" in info

    def test_clear_cache_removes_entries(self):
        @error_cache
        def f(x):
            raise ValueError("fail")

        with pytest.raises(ValueError):
            f(1)

        f.clear_cache()
        assert f.get_cached_error(1) is None


# =============================================================================
# error_cache — LRU eviction
# =============================================================================


class TestErrorCacheLRU:
    def test_lru_eviction_respects_maxsize(self):
        @error_cache(maxsize=2)
        def f(x):
            raise ValueError(f"fail:{x}")

        for i in range(3):
            with pytest.raises(ValueError):
                f(i)

        info = f.cache_info()
        assert "currsize=2" in info  # LRU evicted one entry

    def test_unlimited_cache(self):
        @error_cache(maxsize=None)
        def f(x):
            raise ValueError(f"fail:{x}")

        for i in range(10):
            with pytest.raises(ValueError):
                f(i)

        info = f.cache_info()
        assert "currsize=10" in info
        assert "maxsize=None" in info


# =============================================================================
# error_cache — cache_info() format
# =============================================================================


class TestCacheInfo:
    def test_cache_info_format(self):
        @error_cache(maxsize=64)
        def f(x):
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            f(1)

        info = f.cache_info()
        assert "ErrorCacheInfo" in info
        assert "hits=0" in info
        assert "misses=1" in info
        assert "maxsize=64" in info
        assert "currsize=1" in info
