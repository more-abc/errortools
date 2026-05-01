"""Tests for _errortools/raises.py — raises, assert_raises, raises_all, reraise."""

import sys

import pytest

from _errortools.raises import raises, assert_raises, raises_all, reraise
from . import HAS_PYTEST

if not HAS_PYTEST:
    print("pytest is required to run these teststests/test_raises.py")
    exit(0)
# =============================================================================
# raises()
# =============================================================================


class TestRaises:
    def test_raises_single_error_single_msg(self):
        with pytest.raises(ValueError, match="bad value"):
            raises([ValueError], ["bad value"])

    def test_raises_first_cartesian_pair(self):
        with pytest.raises(ValueError, match="msg1"):
            raises([ValueError, TypeError], ["msg1", "msg2"])

    def test_raises_empty_errors(self):
        raises([], ["some message"])  # should not raise

    def test_raises_empty_msgs(self):
        raises([ValueError], [])  # should not raise

    def test_raises_both_empty(self):
        raises([], [])  # should not raise

    def test_raises_type_error_on_non_subclass(self):
        with pytest.raises(TypeError):
            raises([ValueError], ["msg"], baseerror=LookupError)

    def test_raises_baseerror_respected_subclass(self):
        with pytest.raises(KeyError):
            raises([KeyError], ["missing"], baseerror=LookupError)

    def test_raises_with_custom_exception(self):

        class MyError(Exception):
            pass

        with pytest.raises(MyError, match="custom"):
            raises([MyError], ["custom"])

    def test_raises_multiple_messages_first_wins(self):
        with pytest.raises(ValueError, match="first"):
            raises([ValueError], ["first", "second", "third"])


# =============================================================================
# assert_raises()
# =============================================================================


class TestAssertRaises:
    def test_catches_expected_exception(self):
        exc = assert_raises(int, [ValueError], "not-a-number")
        assert isinstance(exc, ValueError)

    def test_returns_exception_instance(self):
        exc = assert_raises(lambda: 1 / 0, [ZeroDivisionError])
        assert isinstance(exc, ZeroDivisionError)

    def test_raises_assertion_when_no_exception(self):
        with pytest.raises(AssertionError):
            assert_raises(lambda: 42, [ValueError])

    def test_raises_assertion_on_wrong_exception_type(self):
        with pytest.raises(AssertionError):
            assert_raises(lambda: 1 / 0, [ValueError])

    def test_accepts_multiple_expected_types(self):
        exc = assert_raises(int, [ValueError, TypeError], "bad")
        assert isinstance(exc, ValueError)

    def test_forwards_args_and_kwargs(self):

        def f(a, b, c=None):
            if c is None:
                raise RuntimeError("c missing")

        exc = assert_raises(f, [RuntimeError], 1, 2)
        assert isinstance(exc, RuntimeError)

    def test_exc_message_in_assertion(self):
        with pytest.raises(AssertionError, match="ValueError"):
            assert_raises(lambda: 1 / 0, [ValueError])


# =============================================================================
# raises_all()
# =============================================================================


if sys.version_info >= (3, 11):

    class TestRaisesAll:
        def test_raises_exception_group(self):
            with pytest.raises(ExceptionGroup) as exc_info:
                raises_all([ValueError, TypeError], ["bad"])
            grp = exc_info.value
            assert len(grp.exceptions) == 2

        def test_group_message(self):
            with pytest.raises(ExceptionGroup) as exc_info:
                raises_all([ValueError], ["oops"], group_msg="my errors")
            assert exc_info.value.message == "my errors"

        def test_cartesian_product_count(self):
            with pytest.raises(ExceptionGroup) as exc_info:
                raises_all([ValueError, TypeError], ["m1", "m2", "m3"])
            assert len(exc_info.value.exceptions) == 6

        def test_empty_errors_no_raise(self):
            raises_all([], ["msg"])  # no raise

        def test_empty_msgs_no_raise(self):
            raises_all([ValueError], [])  # no raise

        def test_type_error_on_non_subclass(self):
            with pytest.raises(TypeError):
                raises_all([ValueError], ["msg"], baseerror=LookupError)

        def test_default_group_msg(self):
            with pytest.raises(ExceptionGroup) as exc_info:
                raises_all([ValueError], ["x"])
            assert exc_info.value.message == "multiple errors"

        def test_sub_exception_types(self):
            with pytest.raises(ExceptionGroup) as exc_info:
                raises_all([ValueError, TypeError], ["msg"])
            types = {type(e) for e in exc_info.value.exceptions}
            assert types == {ValueError, TypeError}


# =============================================================================
# reraise()
# =============================================================================


class TestReraise:
    def test_reraises_as_new_type(self):
        with pytest.raises(ValueError):
            with reraise(KeyError, ValueError):
                raise KeyError("missing")

    def test_original_exception_chained(self):
        with pytest.raises(ValueError) as exc_info:
            with reraise(KeyError, ValueError):
                raise KeyError("missing")
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, KeyError)

    def test_unrelated_exception_propagates(self):
        with pytest.raises(RuntimeError):
            with reraise(KeyError, ValueError):
                raise RuntimeError("unrelated")

    def test_catch_tuple_of_types(self):
        with pytest.raises(ValueError):
            with reraise((KeyError, IndexError), ValueError):
                raise IndexError("out of range")

    def test_message_preserved(self):
        with pytest.raises(ValueError, match="orig-msg"):
            with reraise(RuntimeError, ValueError):
                raise RuntimeError("orig-msg")

    def test_no_exception_passes_through(self):
        with reraise(KeyError, ValueError):
            x = 1 + 1  # should not raise
        assert x == 2
