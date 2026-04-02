"""Tests for _errortools/ignore.py — ignore, ignore_subclass, ignore_warns."""

import warnings
import pytest

from _errortools.ignore import (
    ignore,
    ignore_subclass,
    ignore_warns,
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

    def test_no_exception_passes_through(self):
        result = []
        with ignore(KeyError):
            result.append(1)
        assert result == [1]

    def test_rejects_non_exception_subclass(self):
        with pytest.raises(TypeError):
            with ignore(int):  # type: ignore
                pass

    def test_subclass_suppressed_when_parent_listed(self):
        with ignore(LookupError):
            raise KeyError("KeyError ⊆ LookupError")

    def test_execution_continues_after_suppression(self):
        sentinel = []
        with ignore(ValueError):
            raise ValueError("ignored")
        sentinel.append("after")
        assert sentinel == ["after"]

    # ------------------------------
    # 新增：IgnoredError 属性测试
    # ------------------------------
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
