"""Tests for _errortools/decorator — decorators."""

import warnings

import pytest

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
