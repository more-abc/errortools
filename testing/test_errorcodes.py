"""Tests for _errortools/classes/errorcodes.py."""

import pytest

from _errortools.classes.errorcodes import (
    PureBaseException,
    ContextException,
    BaseErrorCodes,
    InvalidInputError,
    AccessDeniedError,
    NotFoundError,
    RuntimeFailure,
    TimeoutFailure,
    ConfigurationError,
)

# =============================================================================
# PureBaseException
# =============================================================================


class TestPureBaseException:
    def test_is_exception_subclass(self):
        assert issubclass(PureBaseException, Exception)

    def test_default_detail_used_when_none(self):
        err = PureBaseException()
        assert err.detail == PureBaseException.default_detail

    def test_custom_detail_overrides_default(self):
        err = PureBaseException("custom msg")
        assert err.detail == "custom msg"

    def test_str_includes_code_and_detail(self):
        err = PureBaseException("some error")
        assert str(err) == f"[{PureBaseException.code}] some error"

    def test_repr(self):
        err = PureBaseException("msg")
        r = repr(err)
        assert "PureBaseException" in r
        assert "msg" in r
        assert "-1" in r

    def test_can_be_raised(self):
        with pytest.raises(PureBaseException):
            raise PureBaseException("test")

    def test_custom_subclass(self):
        class MyError(PureBaseException):
            code = 9001
            default_detail = "My error."

        err = MyError()
        assert str(err) == "[9001] My error."
        assert err.code == 9001


# =============================================================================
# ContextException
# =============================================================================


class TestContextException:
    def test_is_pure_base_subclass(self):
        assert issubclass(ContextException, PureBaseException)

    def test_has_trace_id(self):
        err = ContextException()
        assert isinstance(err.trace_id, str)
        assert len(err.trace_id) == 32

    def test_trace_id_unique(self):
        err1 = ContextException()
        err2 = ContextException()
        assert err1.trace_id != err2.trace_id

    def test_context_default_empty_dict(self):
        err = ContextException()
        assert err.context == {}

    def test_cause_default_none(self):
        err = ContextException()
        assert err.cause is None

    def test_with_context_adds_data(self):
        err = ContextException().with_context(user_id=42, action="login")
        assert err.context["user_id"] == 42
        assert err.context["action"] == "login"

    def test_with_context_chaining(self):
        err = ContextException().with_context(a=1).with_context(b=2)
        assert err.context == {"a": 1, "b": 2}

    def test_with_context_returns_self(self):
        err = ContextException()
        assert err.with_context(x=1) is err

    def test_with_cause_non_context_exception(self):
        cause = ValueError("root")
        err = ContextException().with_cause(cause)
        assert err.__cause__ is cause
        assert err.cause is cause

    def test_with_cause_context_exception(self):
        cause = ContextException("root cause")
        err = ContextException().with_cause(cause)
        assert err.cause is cause
        assert err.__cause__ is cause

    def test_with_cause_returns_self(self):
        err = ContextException()
        assert err.with_cause(ValueError()) is err

    def test_chain_single(self):
        err = ContextException("only")
        chain = err.chain
        assert len(chain) == 1
        assert chain[0]["type"] == "ContextException"
        assert chain[0]["detail"] == "only"

    def test_chain_nested(self):
        root = ContextException("root")
        top = ContextException("top").with_cause(root)
        chain = top.chain
        assert len(chain) == 2
        assert chain[0]["type"] == "ContextException"
        assert chain[1]["type"] == "ContextException"

    def test_chain_entry_keys(self):
        err = ContextException()
        entry = err.chain[0]
        assert set(entry.keys()) == {"type", "code", "detail", "trace_id", "context"}

    def test_traceback_no_tb(self):
        err = ContextException()
        assert err.traceback == "no traceback"

    def test_traceback_with_tb(self):
        try:
            raise ContextException("raised")
        except ContextException as e:
            assert isinstance(e.traceback, str)
            assert len(e.traceback) > 0

    def test_repr_includes_trace_id(self):
        err = ContextException()
        r = repr(err)
        assert "trace_id" in r
        assert err.trace_id in r

    def test_can_be_raised(self):
        with pytest.raises(ContextException):
            raise ContextException("test")

    def test_custom_subclass(self):
        class PaymentError(ContextException):
            code = 6001
            default_detail = "Payment failed."

        err = PaymentError()
        assert err.code == 6001
        assert err.detail == "Payment failed."
        assert isinstance(err.trace_id, str)


# =============================================================================
# BaseErrorCodes — basic behaviour
# =============================================================================


class TestBaseErrorCodes:
    def test_is_exception_subclass(self):
        assert issubclass(BaseErrorCodes, Exception)

    def test_is_context_exception_subclass(self):
        assert issubclass(BaseErrorCodes, ContextException)

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
    def test__is_base_subclass(self, cls):
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


# =============================================================================
# Trace & context tracking (Exception Link Tracing Tests)
# =============================================================================


class TestErrorTracing:
    def test_has_trace_id(self):
        err = BaseErrorCodes()
        assert isinstance(err.trace_id, str)
        assert len(err.trace_id) == 32

    def test_trace_id_unique(self):
        err1 = BaseErrorCodes()
        err2 = BaseErrorCodes()
        assert err1.trace_id != err2.trace_id

    def test_context_default_empty_dict(self):
        err = BaseErrorCodes()
        assert err.context == {}
        assert isinstance(err.context, dict)

    def test_with_context_adds_data(self):
        err = InvalidInputError().with_context(user_id=123, request="abc")
        assert err.context["user_id"] == 123
        assert err.context["request"] == "abc"

    def test_with_context_chained_multiple(self):
        err = BaseErrorCodes().with_context(a=1).with_context(b=2)
        assert err.context == {"a": 1, "b": 2}

    def test_with_cause_sets_cause_attr(self):
        cause = ValueError("root")
        err = RuntimeFailure().with_cause(cause)
        assert err.__cause__ is cause
        assert err.cause is cause

    def test_with_cause_preserves_typed_cause(self):
        cause = InvalidInputError("bad input")
        err = RuntimeFailure().with_cause(cause)
        assert err.cause is cause
        assert err.__cause__ is cause

    def test_chain_includes_self(self):
        err = BaseErrorCodes()
        chain = err.chain
        assert len(chain) == 1
        assert chain[0]["type"] == "BaseErrorCodes"
        assert chain[0]["code"] == -1

    def test_chain_includes_cause_hierarchy(self):
        root = NotFoundError("missing")
        middle = AccessDeniedError().with_cause(root)
        top = RuntimeFailure().with_cause(middle)

        chain = top.chain
        assert len(chain) == 3
        assert chain[0]["type"] == "RuntimeFailure"
        assert chain[1]["type"] == "AccessDeniedError"
        assert chain[2]["type"] == "NotFoundError"

    def test_traceback_returns_safe_string(self):
        try:
            raise InvalidInputError()
        except InvalidInputError as e:
            tb_str = e.traceback
            assert isinstance(tb_str, str)
            assert len(tb_str) > 0

    def test_repr_includes_trace_id(self):
        err = BaseErrorCodes()
        r = repr(err)
        assert "trace_id" in r
        assert err.trace_id in r

    def test_all_subclasses_inherit_tracing(self):
        for cls in [
            InvalidInputError,
            AccessDeniedError,
            NotFoundError,
            RuntimeFailure,
            TimeoutFailure,
            ConfigurationError,
        ]:
            err = cls()
            assert hasattr(err, "trace_id")
            assert hasattr(err, "context")
            assert hasattr(err, "chain")
            assert hasattr(err, "with_context")
