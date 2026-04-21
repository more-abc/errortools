"""Tests for _errortools/future.py — super_fast_ignore, super_fast_catch, super_fast_reraise, ExceptionCollector."""

import pytest

from _errortools.future import (
    super_fast_ignore,
    super_fast_catch,
    super_fast_reraise,
    ExceptionCollector,
)
from . import HAS_PYTEST

if not HAS_PYTEST:
    print("pytest is required to run these tests, skip run test_future.py")
    exit(0)


# =============================================================================
# super_fast_ignore
# =============================================================================


class TestSuperFastIgnore:
    """Tests for super_fast_ignore context manager."""

    def test_suppresses_single_exception(self):
        """Test that super_fast_ignore suppresses a single exception type."""
        with super_fast_ignore(ValueError):
            raise ValueError("ignored")

    def test_suppresses_multiple_exception_types(self):
        """Test that super_fast_ignore suppresses multiple exception types."""
        with super_fast_ignore(ValueError, KeyError):
            raise KeyError("ignored")

    def test_unrelated_exception_propagates(self):
        """Test that unrelated exceptions are not suppressed."""
        with pytest.raises(RuntimeError):
            with super_fast_ignore(ValueError):
                raise RuntimeError("not suppressed")

    def test_no_exception_in_block(self):
        """Test that block with no exception executes normally."""
        result = []
        with super_fast_ignore(ValueError):
            result.append(1)
        assert result == [1]

    def test_execution_continues_after_suppression(self):
        """Test that execution continues after exception is suppressed."""
        items = []
        with super_fast_ignore(ValueError):
            raise ValueError("ignored")
        items.append("after")
        assert items == ["after"]

    def test_suppresses_exception_subclass(self):
        """Test that subclasses of specified exceptions are suppressed."""
        with super_fast_ignore(LookupError):
            raise KeyError("subclass of LookupError")

    def test_nested_suppress(self):
        """Test nested super_fast_ignore context managers."""
        with super_fast_ignore(ValueError):
            with super_fast_ignore(KeyError):
                raise KeyError("inner")


# =============================================================================
# super_fast_catch
# =============================================================================


class TestSuperFastCatch:
    """Tests for super_fast_catch context manager."""

    def test_catches_single_exception_type(self):
        """Test that super_fast_catch catches a specified exception type."""
        with super_fast_catch(ValueError) as ctx:
            raise ValueError("caught")
        assert ctx.exception is not None
        assert isinstance(ctx.exception, ValueError)
        assert str(ctx.exception) == "caught"

    def test_catches_multiple_exception_types(self):
        """Test that super_fast_catch can catch multiple exception types."""
        with super_fast_catch(ValueError, KeyError) as ctx:
            raise KeyError("caught")
        assert isinstance(ctx.exception, KeyError)

    def test_catches_exception_subclass(self):
        """Test that subclasses of specified exceptions are caught."""
        with super_fast_catch(LookupError) as ctx:
            raise KeyError("subclass")
        assert isinstance(ctx.exception, KeyError)

    def test_no_exception_stored_when_none_raised(self):
        """Test that exception is None when no exception is raised."""
        with super_fast_catch(ValueError) as ctx:
            pass
        assert ctx.exception is None

    def test_unrelated_exception_propagates(self):
        """Test that unrelated exceptions propagate."""
        with pytest.raises(RuntimeError):
            with super_fast_catch(ValueError) as ctx:
                raise RuntimeError("not caught")

    def test_catch_all_when_no_args(self):
        """Test that super_fast_catch catches all exceptions when given no args."""
        with super_fast_catch() as ctx:
            raise RuntimeError("caught all")
        assert ctx.exception is not None
        assert isinstance(ctx.exception, RuntimeError)

    def test_returns_self(self):
        """Test that super_fast_catch returns itself."""
        with super_fast_catch(ValueError) as ctx:
            assert isinstance(ctx, super_fast_catch)


# =============================================================================
# super_fast_reraise
# =============================================================================


class TestSuperFastReraise:
    """Tests for super_fast_reraise context manager."""

    def test_converts_exception_type(self):
        """Test that super_fast_reraise converts exception types."""
        with pytest.raises(ValueError) as exc_info:
            with super_fast_reraise(KeyError, ValueError):
                raise KeyError("original")
        assert "'original'" in str(exc_info.value)
        assert exc_info.value.__cause__.__class__ == KeyError

    def test_preserves_exception_message(self):
        """Test that reraise preserves the original exception message."""
        msg = "test message"
        with pytest.raises(ValueError) as exc_info:
            with super_fast_reraise(KeyError, ValueError):
                raise KeyError(msg)
        assert msg in str(exc_info.value)

    def test_catches_multiple_types(self):
        """Test that super_fast_reraise can catch multiple exception types."""
        with pytest.raises(RuntimeError):
            with super_fast_reraise((KeyError, ValueError), RuntimeError):
                raise ValueError("caught")

    def test_unrelated_exception_propagates(self):
        """Test that unrelated exceptions propagate unchanged."""
        with pytest.raises(TypeError):
            with super_fast_reraise(ValueError, KeyError):
                raise TypeError("not caught")

    def test_chains_exceptions(self):
        """Test that original exception is chained with __cause__."""
        with pytest.raises(ValueError) as exc_info:
            with super_fast_reraise(KeyError, ValueError):
                raise KeyError("original")
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, KeyError)

    def test_no_exception_in_block(self):
        """Test that block with no exception executes normally."""
        with super_fast_reraise(ValueError, KeyError):
            pass


# =============================================================================
# ExceptionCollector
# =============================================================================


class TestExceptionCollector:
    """Tests for ExceptionCollector context manager."""

    def test_collects_single_exception(self):
        """Test that ExceptionCollector collects a single exception."""
        collector = ExceptionCollector()
        collector.catch(int, "not-a-number")
        assert collector.has_errors
        assert collector.count == 1
        assert len(collector.exceptions) == 1

    def test_collects_multiple_exceptions(self):
        """Test that ExceptionCollector collects multiple exceptions."""
        collector = ExceptionCollector()
        collector.catch(int, "bad1")
        collector.catch(int, "bad2")
        collector.catch(int, "bad3")
        assert collector.count == 3

    def test_catch_returns_false_on_success(self):
        """Test that catch returns False when no exception is raised."""
        collector = ExceptionCollector()
        result = collector.catch(int, "123")
        assert result is False

    def test_catch_returns_true_on_exception(self):
        """Test that catch returns True when exception is raised."""
        collector = ExceptionCollector()
        result = collector.catch(int, "not-a-number")
        assert result is True

    def test_add_method(self):
        """Test that add method adds exceptions manually."""
        collector = ExceptionCollector()
        exc = ValueError("test")
        collector.add(exc)
        assert collector.count == 1
        assert collector.exceptions[0] is exc

    def test_has_errors_property(self):
        """Test has_errors property."""
        collector = ExceptionCollector()
        assert not collector.has_errors
        collector.catch(int, "bad")
        assert collector.has_errors

    def test_clear_method(self):
        """Test that clear removes all exceptions."""
        collector = ExceptionCollector()
        collector.catch(int, "bad1")
        collector.catch(int, "bad2")
        assert collector.count == 2
        collector.clear()
        assert collector.count == 0
        assert not collector.has_errors

    def test_raise_all_with_errors(self):
        """Test that raise_all raises ExceptionGroup when errors collected."""
        collector = ExceptionCollector()
        collector.catch(int, "bad1")
        collector.catch(int, "bad2")
        with pytest.raises(ExceptionGroup) as exc_info:
            collector.raise_all()
        assert exc_info.value.message == "collected errors"
        assert len(exc_info.value.exceptions) == 2

    def test_raise_all_with_custom_message(self):
        """Test that raise_all uses custom message."""
        collector = ExceptionCollector()
        collector.catch(int, "bad")
        with pytest.raises(ExceptionGroup) as exc_info:
            collector.raise_all("custom error message")
        assert exc_info.value.message == "custom error message"

    def test_raise_all_without_errors(self):
        """Test that raise_all does nothing when no errors collected."""
        collector = ExceptionCollector()
        collector.raise_all()

    def test_context_manager_usage(self):
        """Test ExceptionCollector as context manager."""
        with ExceptionCollector() as collector:
            collector.catch(int, "bad1")
            collector.catch(int, "bad2")
        assert collector.count == 2

    def test_context_manager_with_exception_in_block(self):
        """Test context manager when exception raised in block."""
        with ExceptionCollector() as collector:
            raise ValueError("in block")
        assert collector.count == 1
        assert isinstance(collector.exceptions[0], ValueError)

    def test_stop_on_first_mode(self):
        """Test that stop_on_first=True raises immediately."""
        collector = ExceptionCollector(stop_on_first=True)
        with pytest.raises(ValueError):
            collector.catch(int, "bad")
        assert collector.count == 1

    def test_stop_on_first_add_method(self):
        """Test that add method respects stop_on_first."""
        collector = ExceptionCollector(stop_on_first=True)
        with pytest.raises(RuntimeError):
            collector.add(RuntimeError("test"))

    def test_exceptions_property(self):
        """Test that exceptions property returns list of exceptions."""
        collector = ExceptionCollector()
        exc1 = ValueError("test1")
        exc2 = TypeError("test2")
        collector.add(exc1)
        collector.add(exc2)
        exceptions = collector.exceptions
        assert len(exceptions) == 2
        assert exceptions[0] is exc1
        assert exceptions[1] is exc2

    def test_count_property(self):
        """Test that count property returns correct number."""
        collector = ExceptionCollector()
        assert collector.count == 0
        collector.catch(int, "bad1")
        assert collector.count == 1
        collector.catch(int, "bad2")
        assert collector.count == 2
