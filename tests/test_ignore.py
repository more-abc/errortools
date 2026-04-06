"""Tests for _errortools/ignore.py — ignore, ignore_subclass, ignore_warns, timeout, retry."""

import asyncio
import warnings
import pytest

from _errortools.ignore import (
    ignore,
    ignore_subclass,
    ignore_warns,
    fast_ignore,
    timeout,
    retry,
)
from _errortools.wrappers.ignore import IgnoredError, ErrorIgnoreWrapper

# =============================================================================
# ignore() (ErrorIgnoreWrapper)
# =============================================================================


class TestIgnore:
    def test_suppresses_specified_exception(self):
        with ignore(KeyError):
            raise KeyError("should be suppressed")

    def test_suppresses_multiple_types(self):
        with ignore(KeyError, ValueError):
            raise ValueError("suppressed")

    def test_unrelated_exception_propagates(self):
        with pytest.raises(RuntimeError):
            with ignore(KeyError):
                raise RuntimeError("not suppressed")

    def test_subclass_not_suppressed(self):
        with pytest.raises(KeyError):
            with ignore(LookupError):
                raise KeyError("subclass should not be suppressed")

    def test_no_exception_passes_through(self):
        result = []
        with ignore(KeyError):
            result.append(1)
        assert result == [1]

    def test_rejects_non_exception_subclass(self):
        with pytest.raises(TypeError):
            with ignore(int):  # type: ignore
                pass

    def test_execution_continues_after_suppression(self):
        sentinel = []
        with ignore(ValueError):
            raise ValueError("ignored")
        sentinel.append("after")
        assert sentinel == ["after"]

    def test_ignore_captures_error_attributes(self):
        with ignore(NameError) as error:
            raise NameError("test error")

        assert isinstance(error, IgnoredError)
        assert error.name == "NameError"
        assert error.be_ignore is True
        assert error.count == 1
        assert error.traceback is not None
        assert isinstance(error.exception, NameError)

    def test_ignore_no_error_has_default_attributes(self):
        with ignore(KeyError) as error:
            pass

        assert error.name is None
        assert error.be_ignore is False
        assert error.count == 0
        assert error.traceback is None
        assert error.exception is None

    def test_ignore_multiple_uses_reset_state(self):
        with ignore(KeyError) as e1:
            raise KeyError()
        with ignore(KeyError) as e2:
            pass

        assert e1.be_ignore is True
        assert e2.be_ignore is False

    def test_ignore_as_decorator(self):
        @ignore(ZeroDivisionError)
        def func():
            return 1 / 0

        func()

    def test_ignore_decorator_with_exception_info(self):
        ig = ignore(ValueError)

        @ig
        def func():
            raise ValueError("decorator test")

        with ig as err:
            func()

        assert err.name == "ValueError"
        assert err.be_ignore is True
        assert err.count == 1


# =============================================================================
# ignore_subclass()
# =============================================================================


class TestIgnoreSubclass:
    def test_suppresses_exact_base(self):
        with ignore_subclass(KeyError):
            raise KeyError("exact base")

    def test_suppresses_subclass(self):
        with ignore_subclass(LookupError):
            raise KeyError("subclass of LookupError")

    def test_unrelated_exception_propagates(self):
        with pytest.raises(RuntimeError):
            with ignore_subclass(LookupError):
                raise RuntimeError("unrelated")

    def test_no_exception_passes_through(self):
        result = []
        with ignore_subclass(ValueError):
            result.append("ok")
        assert result == ["ok"]

    def test_multiple_subclass_levels(self):
        class MyError(LookupError):
            pass

        class DeepError(MyError):
            pass

        with ignore_subclass(LookupError):
            raise DeepError("deep")

    def test_suppresses_base_exception_subclass(self):
        with ignore_subclass(BaseException):
            raise KeyboardInterrupt


# =============================================================================
# ignore_warns()
# =============================================================================


class TestIgnoreWarns:
    def test_suppresses_specified_warning(self):
        with ignore_warns(DeprecationWarning):
            warnings.warn("old api", DeprecationWarning, stacklevel=1)

    def test_suppresses_multiple_warning_categories(self):
        with ignore_warns(DeprecationWarning, UserWarning):
            warnings.warn("dep", DeprecationWarning, stacklevel=1)
            warnings.warn("user", UserWarning, stacklevel=1)

    def test_unrelated_warning_is_not_suppressed(self):
        with pytest.warns(UserWarning):
            with ignore_warns(DeprecationWarning):
                warnings.warn("unrelated", UserWarning, stacklevel=1)

    def test_no_args_suppresses_all(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with ignore_warns():
                warnings.warn("any", UserWarning, stacklevel=1)
        assert len(caught) == 0

    def test_execution_continues_after_suppression(self):
        sentinel = []
        with ignore_warns(UserWarning):
            warnings.warn("w", UserWarning, stacklevel=1)
            sentinel.append(1)
        assert sentinel == [1]


class TestIgnoreClasses:
    def test_ignored_error_reset(self):
        err = IgnoredError()
        err.name = "Test"
        err.be_ignore = True
        err.reset()
        assert err.name is None
        assert err.be_ignore is False

    def test_error_ignore_wrapper_instance(self):
        wrapper = ignore(KeyError)
        assert isinstance(wrapper, ErrorIgnoreWrapper)
        assert hasattr(wrapper, "__enter__")
        assert hasattr(wrapper, "__exit__")


# =============================================================================
# fast_ignore() (High-performance, no traceback, no state)
# =============================================================================


class TestFastIgnore:
    def test_fast_ignore_suppresses_specified_exception(self):
        with fast_ignore(KeyError):
            raise KeyError("should be suppressed")

    def test_fast_ignore_suppresses_multiple_types(self):
        with fast_ignore(KeyError, ValueError):
            raise ValueError("suppressed")

    def test_fast_ignore_unrelated_exception_propagates(self):
        with pytest.raises(RuntimeError):
            with fast_ignore(KeyError):
                raise RuntimeError("not suppressed")

    def test_fast_ignore_no_exception_passes_through(self):
        result = []
        with fast_ignore(KeyError):
            result.append(1)
        assert result == [1]

    def test_fast_ignore_rejects_non_exception_subclass(self):
        with pytest.raises(TypeError):
            with fast_ignore(int):  # type: ignore
                pass

    def test_fast_ignore_subclass_not_suppressed(self):
        with pytest.raises(KeyError):
            with fast_ignore(LookupError):
                raise KeyError("KeyError ⊆ LookupError, but not suppressed")

    def test_fast_ignore_execution_continues_after_suppression(self):
        sentinel = []
        with fast_ignore(ValueError):
            raise ValueError("ignored")
        sentinel.append("after")
        assert sentinel == ["after"]


# =============================================================================
# timeout() decorator
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
# retry()
# =============================================================================


class TestRetry:
    # --- init validation ---

    def test_negative_times_raises_value_error(self):
        with pytest.raises(ValueError):
            retry(times=-1, on=ValueError)

    def test_non_exception_type_raises_type_error(self):
        with pytest.raises(TypeError):
            retry(times=2, on=int)  # type: ignore

    # --- decorator (sync) ---

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

    # --- decorator (async) ---

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
