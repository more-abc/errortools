"""Tests for _errortools/ignore.py — ignore, ignore_subclass, ignore_warns."""

import warnings
import pytest

from _errortools.ignore import ignore, ignore_subclass, ignore_warns

# =============================================================================
# ignore()
# =============================================================================


class TestIgnore:
    def test_suppresses_specified_exception(self):
        with ignore(KeyError):
            raise KeyError("should be suppressed")
        # execution reaches here

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
        """Passing a non-Exception type should raise ValueError."""
        with pytest.raises((ValueError, TypeError)):
            with ignore(int):  # int is not an Exception subclass
                pass

    def test_subclass_suppressed_when_parent_listed(self):
        """A subclass of a listed type should also be suppressed."""
        with ignore(LookupError):
            raise KeyError("KeyError ⊆ LookupError")

    def test_execution_continues_after_suppression(self):
        sentinel = []
        with ignore(ValueError):
            raise ValueError("ignored")
        sentinel.append("after")
        assert sentinel == ["after"]


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
        """Deeply nested subclass should still be suppressed."""

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
        # no warning propagated

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
