"""Tests for _errortools/classes/errorcodes.py — BaseErrorCodes and subclasses."""

import pytest

from _errortools.classes.errorcodes import (
    BaseErrorCodes,
    InvalidInputError,
    AccessDeniedError,
    NotFoundError,
    RuntimeFailure,
    TimeoutFailure,
    ConfigurationError,
)

# =============================================================================
# BaseErrorCodes — basic behaviour
# =============================================================================


class TestBaseErrorCodes:
    def test_is_exception_subclass(self):
        assert issubclass(BaseErrorCodes, Exception)

    def test_default_detail_used_when_none(self):
        err = BaseErrorCodes()
        assert err.detail == BaseErrorCodes.default_detail

    def test_custom_detail_overrides_default(self):
        err = BaseErrorCodes("custom msg")
        assert err.detail == "custom msg"

    def test_str_includes_code_and_detail(self):
        err = BaseErrorCodes("some error")
        assert str(err) == f"[{BaseErrorCodes.code}] some error"

    def test_str_default_detail(self):
        err = BaseErrorCodes()
        assert str(err) == f"[-1] {BaseErrorCodes.default_detail}"

    def test_repr(self):
        err = BaseErrorCodes("msg")
        r = repr(err)
        assert "BaseErrorCodes" in r
        assert "msg" in r
        assert "-1" in r

    def test_can_be_raised(self):
        with pytest.raises(BaseErrorCodes):
            raise BaseErrorCodes("test")

    def test_custom_subclass(self):
        class PaymentError(BaseErrorCodes):
            code = 6001
            default_detail = "Payment failed."

        err = PaymentError()
        assert str(err) == "[6001] Payment failed."
        assert err.code == 6001


# =============================================================================
# Predefined error subclasses
# =============================================================================


class TestPredefinedErrorCodes:
    @pytest.mark.parametrize(
        "cls, expected_code, expected_default",
        [
            (InvalidInputError, 1001, "Invalid input."),
            (AccessDeniedError, 2001, "Access denied."),
            (NotFoundError, 3001, "Resource not found."),
            (RuntimeFailure, 4001, "Runtime failure."),
            (TimeoutFailure, 4002, "Operation timed out."),
            (ConfigurationError, 5001, "Configuration error."),
        ],
    )
    def test_code_and_default(self, cls, expected_code, expected_default):
        err = cls()
        assert err.code == expected_code
        assert err.detail == expected_default

    @pytest.mark.parametrize(
        "cls",
        [
            InvalidInputError,
            AccessDeniedError,
            NotFoundError,
            RuntimeFailure,
            TimeoutFailure,
            ConfigurationError,
        ],
    )
    def test_custom_detail(self, cls):
        err = cls("my detail")
        assert err.detail == "my detail"
        assert f"[{cls.code}] my detail" == str(err)

    @pytest.mark.parametrize(
        "cls",
        [
            InvalidInputError,
            AccessDeniedError,
            NotFoundError,
            RuntimeFailure,
            TimeoutFailure,
            ConfigurationError,
        ],
    )
    def test_is_base_subclass(self, cls):
        assert issubclass(cls, BaseErrorCodes)
        assert issubclass(cls, Exception)


# =============================================================================
# Factory classmethods on BaseErrorCodes
# =============================================================================


class TestFactoryMethods:
    def test_invalid_input_factory(self):
        err = BaseErrorCodes.invalid_input("bad")
        assert isinstance(err, InvalidInputError)
        assert err.detail == "bad"

    def test_not_found_factory(self):
        err = BaseErrorCodes.not_found()
        assert isinstance(err, NotFoundError)

    def test_access_denied_factory(self):
        err = BaseErrorCodes.access_denied()
        assert isinstance(err, AccessDeniedError)

    def test_configuration_error_factory(self):
        err = BaseErrorCodes.configuration_error("bad config")
        assert isinstance(err, ConfigurationError)
        assert err.detail == "bad config"

    def test_runtime_failure_factory(self):
        err = BaseErrorCodes.runtime_failure()
        assert isinstance(err, RuntimeFailure)

    def test_timeout_failure_factory(self):
        err = BaseErrorCodes.timeout_failure("took too long")
        assert isinstance(err, TimeoutFailure)
        assert err.detail == "took too long"

    def test_factory_with_none_uses_default(self):
        err = BaseErrorCodes.invalid_input(None)
        assert err.detail == InvalidInputError.default_detail
