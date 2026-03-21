"""Tests for _errortools/raises.py — raises, assert_raises, raises_all, reraise."""

import pytest

from _errortools.raises import raises, assert_raises, raises_all, reraise


# =============================================================================
# raises()
# =============================================================================

class TestRaises:
    def test_raises_single_error_single_msg(self):
        """Should raise the first (error, msg) pair."""
        with pytest.raises(ValueError, match="bad value"):
            raises([ValueError], ["bad value"])

    def test_raises_first_cartesian_pair(self):
        """Cartesian product: first pair is (errors[0], msgs[0])."""
        with pytest.raises(ValueError, match="msg1"):
            raises([ValueError, TypeError], ["msg1", "msg2"])

    def test_raises_empty_errors(self):
        """Empty errors list → no raise."""
        raises([], ["some message"])  # should not raise

    def test_raises_empty_msgs(self):
        """Empty msgs list → no raise."""
        raises([ValueError], [])  # should not raise

    def test_raises_both_empty(self):
        """Both empty → no raise."""
        raises([], [])  # should not raise

    def test_raises_type_error_on_non_subclass(self):
        """Non-Exception subclass should raise TypeError."""
        with pytest.raises(TypeError):
            raises([ValueError], ["msg"], baseerror=LookupError)

    def test_raises_baseerror_respected_subclass(self):
        """Subclass of baseerror is valid."""
        with pytest.raises(KeyError):
            raises([KeyError], ["missing"], baseerror=LookupError)

    def test_raises_with_custom_exception(self):
        """Custom exception classes should work."""
        class MyError(Exception):
            pass

        with pytest.raises(MyError, match="custom"):
            raises([MyError], ["custom"])

    def test_raises_multiple_messages_first_wins(self):
        """When multiple messages, only the first pair is raised."""
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
        """Return value should be the caught exception."""
        exc = assert_raises(lambda: 1 / 0, [ZeroDivisionError])
        assert isinstance(exc, ZeroDivisionError)

    def test_raises_assertion_when_no_exception(self):
        """If func does not raise, AssertionError is raised."""
        with pytest.raises(AssertionError):
            assert_raises(lambda: 42, [ValueError])

    def test_raises_assertion_on_wrong_exception_type(self):
        """If func raises but the wrong type, AssertionError is raised."""
        with pytest.raises(AssertionError):
            assert_raises(lambda: 1 / 0, [ValueError])

    def test_accepts_multiple_expected_types(self):
        """Multiple expected types: any match is OK."""
        exc = assert_raises(int, [ValueError, TypeError], "bad")
        assert isinstance(exc, ValueError)

    def test_forwards_args_and_kwargs(self):
        """Positional and keyword args must be forwarded to func."""
        def f(a, b, c=None):
            if c is None:
                raise RuntimeError("c missing")

        exc = assert_raises(f, [RuntimeError], 1, 2)
        assert isinstance(exc, RuntimeError)

    def test_exc_message_in_assertion(self):
        """AssertionError message should mention expected types."""
        with pytest.raises(AssertionError, match="ValueError"):
            assert_raises(lambda: 1 / 0, [ValueError])


# =============================================================================
# raises_all()
# =============================================================================

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
        """2 errors × 3 messages = 6 exceptions."""
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
        """Each raised sub-exception should match its declared type."""
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
        """Exceptions not in 'catch' should propagate unchanged."""
        with pytest.raises(RuntimeError):
            with reraise(KeyError, ValueError):
                raise RuntimeError("unrelated")

    def test_catch_tuple_of_types(self):
        """catch can be a tuple of exception types."""
        with pytest.raises(ValueError):
            with reraise((KeyError, IndexError), ValueError):
                raise IndexError("out of range")

    def test_message_preserved(self):
        """The message of the original exception is preserved."""
        with pytest.raises(ValueError, match="orig-msg"):
            with reraise(RuntimeError, ValueError):
                raise RuntimeError("orig-msg")

    def test_no_exception_passes_through(self):
        """No exception inside block → reraise does nothing."""
        with reraise(KeyError, ValueError):
            x = 1 + 1  # should not raise
        assert x == 2
