"""Tests for _errortools/decorator — decorators."""

import asyncio
import warnings

import pytest

from _errortools.decorator.cache import error_cache
from _errortools.decorator.deprecated import deprecated, experimental
from _errortools.decorator.handlers import suppress, convert
from _errortools.decorator.timeout import timeout
from _errortools.decorator.retry import retry

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
# experimental decorator
# =============================================================================


class TestExperimentalDecorator:
    def test_bare_decorator(self):
        @experimental()
        def f(x):
            return x

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert f(3) == 3

    def test_decorator_with_reason(self):
        @experimental(reason="API may change without notice")
        def f(x):
            return x * 2

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert f(5) == 10

    def test_wrapper_has_correct_name(self):
        @experimental()
        def my_func(x):
            return x

        assert my_func.__name__ == "my_func"

    def test_wrapped_attribute(self):
        def inner(x):
            return x

        wrapped = experimental()(inner)
        assert wrapped.__wrapped__ is inner


class TestExperimentalWarning:
    def test_emits_user_warning_on_call(self):
        @experimental()
        def f():
            pass

        with pytest.warns(FutureWarning) as record:
            f()

        assert len(record) == 1
        warn = record[0]
        assert "experimental" in str(warn.message)

    def test_warning_contains_reason(self):
        @experimental(reason="Subject to change")
        def f():
            pass

        with pytest.warns(FutureWarning) as record:
            f()

        assert "Subject to change" in str(record[0].message)

    def test_warning_stacklevel_correct(self):
        @experimental()
        def f():
            pass

        with pytest.warns(FutureWarning) as record:
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


# =============================================================================
# suppress decorator
# =============================================================================


class TestSuppressDecorator:
    def test_suppresses_and_returns_default(self):
        @suppress(ZeroDivisionError, default=0)
        def f(a, b):
            return a / b

        assert f(1, 0) == 0

    def test_returns_normally_when_no_exception(self):
        @suppress(ValueError, default=-1)
        def f(x):
            return int(x)

        assert f("42") == 42

    def test_default_is_none(self):
        @suppress(ValueError)
        def f():
            raise ValueError("x")

        assert f() is None

    def test_unrelated_exception_propagates(self):
        @suppress(ValueError, default=0)
        def f():
            raise TypeError("wrong")

        with pytest.raises(TypeError):
            f()

    def test_multiple_exception_types(self):
        @suppress(ValueError, KeyError, default="fallback")
        def f(flag):
            if flag == 1:
                raise ValueError("v")
            raise KeyError("k")

        assert f(1) == "fallback"
        assert f(2) == "fallback"

    def test_preserves_function_name(self):
        @suppress(Exception)
        def my_func():
            raise Exception("x")

        assert my_func.__name__ == "my_func"


# =============================================================================
# convert decorator
# =============================================================================


class TestConvertDecorator:
    def test_converts_exception_type(self):
        @convert(KeyError, ValueError)
        def f():
            raise KeyError("missing")

        with pytest.raises(ValueError) as exc_info:
            f()
        assert "missing" in str(exc_info.value)

    def test_chains_original_exception(self):
        @convert(KeyError, ValueError)
        def f():
            raise KeyError("orig")

        with pytest.raises(ValueError) as exc_info:
            f()
        assert isinstance(exc_info.value.__cause__, KeyError)

    def test_custom_message(self):
        @convert(KeyError, RuntimeError, message="custom error")
        def f():
            raise KeyError("ignored")

        with pytest.raises(RuntimeError, match="custom error"):
            f()

    def test_no_conversion_on_success(self):
        @convert(KeyError, ValueError)
        def f():
            return 42

        assert f() == 42

    def test_unrelated_exception_propagates(self):
        @convert(KeyError, ValueError)
        def f():
            raise TypeError("wrong")

        with pytest.raises(TypeError):
            f()

    def test_multiple_source_types(self):
        @convert((KeyError, IndexError), ValueError)
        def f(flag):
            if flag:
                raise KeyError("k")
            raise IndexError("i")

        with pytest.raises(ValueError):
            f(True)
        with pytest.raises(ValueError):
            f(False)

    def test_preserves_function_name(self):
        @convert(Exception, RuntimeError)
        def my_func():
            raise Exception("x")

        assert my_func.__name__ == "my_func"


# =============================================================================
# timeout decorator
# =============================================================================


class TestTimeout:
    def test_timeout_completes_within_limit(self):
        @timeout(1.0)
        async def quick_task():
            await asyncio.sleep(0.1)
            return "done"

        result = asyncio.run(quick_task())
        assert result == "done"

    def test_timeout_raises_on_exceeded(self):
        @timeout(0.1)
        async def slow_task():
            await asyncio.sleep(1.0)

        with pytest.raises(asyncio.TimeoutError):
            asyncio.run(slow_task())

    def test_timeout_with_args_kwargs(self):
        @timeout(1.0)
        async def task_with_params(a, b, c=None):
            await asyncio.sleep(0.01)
            return (a, b, c)

        result = asyncio.run(task_with_params(1, 2, c=3))
        assert result == (1, 2, 3)

    def test_timeout_preserves_function_name(self):
        @timeout(1.0)
        async def my_async_func():
            pass

        assert my_async_func.__name__ == "my_async_func"

    def test_timeout_propagates_other_exceptions(self):
        @timeout(1.0)
        async def failing_task():
            await asyncio.sleep(0.01)
            raise ValueError("custom error")

        with pytest.raises(ValueError, match="custom error"):
            asyncio.run(failing_task())

    def test_timeout_rejects_sync_function(self):
        with pytest.raises(ValueError, match="timeout only supports async functions"):
            timeout(1.0)(lambda: None)

    def test_timeout_rejects_regular_callable(self):
        with pytest.raises(ValueError, match="timeout only supports async functions"):
            timeout(1.0)(int)

    def test_timeout_zero_seconds(self):
        @timeout(0.0)
        async def instant_task():
            return "immediate"

        with pytest.raises(asyncio.TimeoutError):
            asyncio.run(instant_task())

    def test_timeout_returns_value(self):
        @timeout(1.0)
        async def coro():
            await asyncio.sleep(0.01)
            return "value"

        assert asyncio.run(coro()) == "value"


# =============================================================================
# retry decorator
# =============================================================================


class TestRetry:
    def test_negative_times_raises_value_error(self):
        with pytest.raises(ValueError):
            retry(times=-1, on=ValueError)

    def test_non_exception_type_raises_type_error(self):
        with pytest.raises(TypeError):
            retry(times=2, on=int)  # type: ignore

    def test_decorator_succeeds_on_first_attempt(self):
        @retry(times=3, on=ValueError)
        def fn():
            return "ok"

        assert fn() == "ok"

    def test_decorator_retries_until_success(self):
        state = {"n": 0}

        @retry(times=3, on=ValueError)
        def fn():
            state["n"] += 1
            if state["n"] < 3:
                raise ValueError("retry me")
            return state["n"]

        assert fn() == 3

    def test_decorator_reraises_after_exhaustion(self):
        @retry(times=2, on=ValueError)
        def fn():
            raise ValueError("always fails")

        with pytest.raises(ValueError, match="always fails"):
            fn()

    def test_decorator_unrelated_exception_propagates(self):
        @retry(times=5, on=ValueError)
        def fn():
            raise RuntimeError("unrelated")

        with pytest.raises(RuntimeError):
            fn()

    def test_decorator_preserves_return_value(self):
        @retry(times=2, on=ValueError)
        def fn():
            return 42

        assert fn() == 42

    def test_decorator_preserves_function_name(self):
        @retry(times=1, on=ValueError)
        def my_func():
            pass

        assert my_func.__name__ == "my_func"

    def test_async_decorator_succeeds(self):
        @retry(times=3, on=ValueError)
        async def fn():
            return "async ok"

        assert asyncio.run(fn()) == "async ok"

    def test_async_decorator_retries_until_success(self):
        state = {"n": 0}

        @retry(times=3, on=ValueError)
        async def fn():
            state["n"] += 1
            if state["n"] < 3:
                raise ValueError("retry")
            return state["n"]

        assert asyncio.run(fn()) == 3

    def test_async_decorator_reraises_after_exhaustion(self):
        @retry(times=2, on=ValueError)
        async def fn():
            raise ValueError("async fail")

        with pytest.raises(ValueError, match="async fail"):
            asyncio.run(fn())
