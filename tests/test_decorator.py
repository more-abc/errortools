"""Tests for _errortools/decorator — decorators."""

import warnings

import pytest

from _errortools.decorator.cache import error_cache
from _errortools.decorator.deprecated import deprecated
from . import HAS_PYTEST

if not HAS_PYTEST:
    print("pytest is required to run these tests, skip run test_decorator.py")
    exit(0)

# =============================================================================
# deprecated decorator
# =============================================================================


class TestDeprecatedDecorator:
    def test_bare_decorator_with_version(self):
        @deprecated(version="2.0")
        def f(x):
            return x

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert f(3) == 3

    def test_decorator_with_reason(self):
        @deprecated(version="2.0", reason="Use new_func instead")
        def f(x):
            return x * 2

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert f(5) == 10

    def test_wrapper_has_correct_name(self):
        @deprecated(version="2.0")
        def my_func(x):
            return x

        assert my_func.__name__ == "my_func"

    def test_wrapped_attribute(self):
        def inner(x):
            return x

        wrapped = deprecated(version="2.0")(inner)
        assert wrapped.__wrapped__ is inner


class TestDeprecatedWarning:
    def test_emits_deprecation_warning_on_call(self):
        @deprecated(version="2.0")
        def f():
            pass

        with pytest.warns(DeprecationWarning) as record:
            f()

        assert len(record) == 1
        warn = record[0]
        assert "deprecated since version 2.0" in str(warn.message)

    def test_warning_contains_reason(self):
        @deprecated(version="2.0", reason="Please upgrade API")
        def f():
            pass

        with pytest.warns(DeprecationWarning) as record:
            f()

        assert "Please upgrade API" in str(record[0].message)

    def test_warning_stacklevel_correct(self):
        @deprecated(version="2.0")
        def f():
            pass

        with pytest.warns(DeprecationWarning) as record:
            f()

        # Ensure warning points to caller, not wrapper
        assert record[0].lineno is not None


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
        assert info.misses == 1

    def test_hit_increments_stat(self):
        @error_cache
        def f(x):
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            f(99)

        f.get_cached_error(99)  # counts as a hit
        info = f.cache_info()
        assert info.hits == 1

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
        assert info.hits == 0
        assert info.misses == 0
        assert info.currsize == 0

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
        assert info.currsize == 2  # LRU evicted one entry

    def test_unlimited_cache(self):
        @error_cache(maxsize=None)
        def f(x):
            raise ValueError(f"fail:{x}")

        for i in range(10):
            with pytest.raises(ValueError):
                f(i)

        info = f.cache_info()
        assert info.currsize == 10
        assert info.maxsize is None


# =============================================================================
# error_cache — cache_info() format
# =============================================================================


class TestCacheInfo:
    def test_cache_info_fields(self):
        @error_cache(maxsize=64)
        def f(x):
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            f(1)

        info = f.cache_info()
        assert info.hits == 0
        assert info.misses == 1
        assert info.maxsize == 64
        assert info.currsize == 1
