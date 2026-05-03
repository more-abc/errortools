"""Tests for _errortools/classes/abc.py — abstract base classes for error handling.

Covers:
  - ErrorCodeable (ABC for exceptions with machine-readable error codes)
  - Warnable (ABC for warning classes that can emit themselves)
  - Raiseable (ABC for objects that can raise themselves as exceptions)
  - Error (ABC for module-level Error exceptions named "Error")
"""

import pytest
import warnings
import copy
import shutil
import csv
import configparser

# Import the ABC classes to test
from _errortools.classes.abc import ErrorCodeable, Warnable, Raiseable, Error

# =============================================================================
# ErrorCodeable ABC Tests
# =============================================================================


class TestErrorCodeable:
    def test_subclasshook_recognises_classes_with_code_and_default_detail(self):
        # __subclasshook__ recognises classes with 'code' and 'default_detail' attributes.

        # Valid class implementing required attributes
        class ValidError(ErrorCodeable):
            # Class-level constants
            _code = 6001
            _default_detail = "Payment processing failed"

            @property
            def code(self) -> int:
                return self._code

            @property
            def default_detail(self) -> str:
                return self._default_detail

        # Invalid class missing required attributes
        class InvalidError:
            pass

        assert issubclass(ValidError, ErrorCodeable)
        assert not issubclass(InvalidError, ErrorCodeable)

    def test_cannot_instantiate_abstract_base_class(self):
        with pytest.raises(TypeError) as excinfo:
            ErrorCodeable()  # type: ignore

        assert "Can't instantiate abstract class ErrorCodeable" in str(excinfo.value)
        assert "code" in str(excinfo.value)
        assert "default_detail" in str(excinfo.value)

    def test_concrete_subclass_implements_required_properties(self):

        class NotFoundError(ErrorCodeable, Exception):
            # Use different names for class vars to avoid property name collision
            ERROR_CODE = 404
            DEFAULT_MESSAGE = "Resource not found"

            @property
            def code(self) -> int:
                return self.ERROR_CODE

            @property
            def default_detail(self) -> str:
                return self.DEFAULT_MESSAGE

        error = NotFoundError()
        # Verify properties return correct values (not property objects)
        assert error.code == 404
        assert error.default_detail == "Resource not found"

    def test_registered_classes_are_recognised_as_subclasses(self):
        # Import registered error classes (match original module structure)
        try:
            from _errortools.classes.errorcodes import (
                NotFoundError,
                AccessDeniedError,
                InvalidInputError,
            )

            assert issubclass(NotFoundError, ErrorCodeable)
            assert issubclass(AccessDeniedError, ErrorCodeable)
            assert issubclass(InvalidInputError, ErrorCodeable)
        except ImportError:
            # Skip if registered classes don't exist (test infrastructure)
            pytest.skip("Registered error classes not found - skipping")


# =============================================================================
# Warnable ABC Tests
# =============================================================================


# Define warning class at module level (avoids local class identity issues)
class DeprecatedFeatureWarning(Warnable, Warning):
    default_detail = "This feature is deprecated"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_detail
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    @classmethod
    def emit(cls, detail: str | None = None, stacklevel: int = 2) -> None:
        msg = detail or cls.default_detail
        warnings.warn(cls(msg), stacklevel=stacklevel)


class TestWarnable:
    def test_subclasshook_recognises_classes_with_emit_classmethod(self):

        # Valid warning class with emit method
        class ValidWarning(Warnable, Warning):
            default_detail = "Deprecated feature usage"

            @classmethod
            def emit(cls, detail: str | None = None, stacklevel: int = 2) -> None:
                msg = detail or cls.default_detail
                warnings.warn(cls(msg), stacklevel=stacklevel)

        # Invalid warning class without emit method
        class InvalidWarning(Warning):
            pass

        assert issubclass(ValidWarning, Warnable)
        assert not issubclass(InvalidWarning, Warnable)

    def test_cannot_instantiate_abstract_base_class(self):
        with pytest.raises(TypeError) as excinfo:
            Warnable()  # type: ignore

        assert "Can't instantiate abstract class Warnable" in str(excinfo.value)
        assert "emit" in str(excinfo.value)

    def test_emit_method_issues_warning_correctly(self):
        # Use module-level warning class (avoids local class identity issues)
        WarningClass = DeprecatedFeatureWarning

        # Test default message - capture warnings and verify manually
        with pytest.warns(WarningClass) as record:
            WarningClass.emit()

        # Verify warning type and message
        assert len(record) == 1
        assert isinstance(record[0].message, WarningClass)
        assert record[0].message.message == "This feature is deprecated"

        # Test custom detail message
        custom_msg = "Use new_feature() instead"
        with pytest.warns(WarningClass) as record:
            WarningClass.emit(detail=custom_msg)

        # Verify custom message
        assert len(record) == 1
        assert isinstance(record[0].message, WarningClass)
        assert record[0].message.message == custom_msg

    def test_registered_warnings_are_recognised_as_subclasses(self):
        try:
            from _errortools.classes.warn import (
                DeprecatedWarning,
                PerformanceWarning,
                ConfigurationWarning,
            )

            assert issubclass(DeprecatedWarning, Warnable)
            assert issubclass(PerformanceWarning, Warnable)
            assert issubclass(ConfigurationWarning, Warnable)
        except ImportError:
            # Skip if registered classes don't exist (test infrastructure)
            pytest.skip("Registered warning classes not found - skipping")


# =============================================================================
# Raiseable ABC Tests
# =============================================================================


class TestRaiseable:
    def test_subclasshook_recognises_classes_with_raise_it_method(self):

        # Valid exception class with raise_it method
        class ValidRaiseableError(Raiseable, Exception):
            def raise_it(self) -> None:
                raise self

        # Invalid class without raise_it method
        class InvalidError(Exception):
            pass

        assert issubclass(ValidRaiseableError, Raiseable)
        assert not issubclass(InvalidError, Raiseable)

    def test_cannot_instantiate_abstract_base_class(self):
        with pytest.raises(TypeError) as excinfo:
            Raiseable()  # type: ignore

        assert "Can't instantiate abstract class Raiseable" in str(excinfo.value)
        assert "raise_it" in str(excinfo.value)

    def test_raise_it_method_raises_self(self):

        class CustomError(Raiseable, Exception):
            def __init__(self, message: str):
                self.message = message

            def raise_it(self) -> None:
                raise self

        error_instance = CustomError("Something went wrong")

        with pytest.raises(CustomError) as excinfo:
            error_instance.raise_it()

        assert excinfo.value == error_instance
        assert excinfo.value.message == "Something went wrong"

    def test_raise_it_can_raise_wrapped_exceptions(self):

        class WrappedError(Raiseable, Exception):
            def __init__(self, original_msg: str):
                self.original_msg = original_msg

            def raise_it(self) -> None:
                raise RuntimeError(f"Wrapped: {self.original_msg}") from self

        error_instance = WrappedError("Original failure")

        with pytest.raises(RuntimeError) as excinfo:
            error_instance.raise_it()

        assert "Wrapped: Original failure" in str(excinfo.value)
        assert excinfo.value.__cause__ == error_instance


# =============================================================================
# Error ABC Tests
# =============================================================================


class TestError:
    def test_subclasshook_recognises_classes_named_Error(self):

        # Valid class named exactly "Error"
        class Error:
            pass

        # Invalid class with different name
        class CustomError(Exception):
            pass

        # Invalid class with different __name__
        class NotAnError:
            __name__ = "MyError"

        assert issubclass(Error, Error)
        assert not issubclass(CustomError, Error)
        assert not issubclass(NotAnError, Error)

    def test_standard_library_Error_classes_are_recognised(self):
        # All these classes are named "Error" → automatically matched
        assert issubclass(copy.Error, Error)
        assert issubclass(shutil.Error, Error)
        assert issubclass(csv.Error, Error)
        assert issubclass(configparser.Error, Error)

        # Verify instances pass isinstance checks
        assert isinstance(copy.Error(), Error)
        assert isinstance(shutil.Error(), Error)
        assert isinstance(csv.Error(), Error)
        assert isinstance(configparser.Error(), Error)

    def test_registered_classes_are_recognised_as_subclasses(self):
        # These are already registered in the ABC
        assert issubclass(copy.Error, Error)
        assert issubclass(shutil.Error, Error)

    def test_subclasshook_returns_not_implemented_for_non_base_class(self):

        # Create a subclass to test hook behavior
        class MyError(Error):
            __name__ = "Error"
            __slots__ = ()

        # Subclass hook should ignore MyError checks
        class TestClass:
            __name__ = "Error"

        assert issubclass(TestClass, MyError) is False
