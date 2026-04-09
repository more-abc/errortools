"""Tests for _errortools/typing.py - type alias validation."""

from typing import Union, get_args, get_origin
import pytest

from _errortools.typing import (
    PureBaseExceptionType,
    ContextExceptionType,
    BaseErrorCodesType,
    AnyErrorCode,
    InputError,
    AccessError,
    LookupError_,
    RuntimeError_,
    ExceptionType,
    TracebackType,
    FrameType,
)
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
from . import HAS_PYTEST

if not HAS_PYTEST:
    print("pytest is required to run these teststests/test_typing.py")


class TestBaseTypeAliases:

    def test_pure_base_exception_type(self):
        assert PureBaseExceptionType is PureBaseException

    def test_context_exception_type(self):
        assert ContextExceptionType is ContextException

    def test_base_error_codes_type(self):
        assert BaseErrorCodesType is BaseErrorCodes


class TestSimpleSemanticAliases:
    """Validate short, user-friendly aliases."""

    def test_input_error_alias(self):
        assert InputError is InvalidInputError

    def test_access_error_alias(self):
        assert AccessError is AccessDeniedError

    def test_lookup_error_alias(self):
        assert LookupError_ is NotFoundError


class TestUnionTypeAliases:

    def test_any_error_code_union(self):
        assert get_origin(AnyErrorCode) is Union
        members = set(get_args(AnyErrorCode))
        assert members == {
            InvalidInputError,
            AccessDeniedError,
            NotFoundError,
            RuntimeFailure,
            TimeoutFailure,
            ConfigurationError,
        }

    def test_runtime_error_union(self):
        assert get_origin(RuntimeError_) is Union
        assert set(get_args(RuntimeError_)) == {RuntimeFailure, TimeoutFailure}

    def test_all_error_codes_inherit_base(self):
        for exc_cls in get_args(AnyErrorCode):
            assert issubclass(exc_cls, BaseErrorCodes)


class TestExceptionTypeAlias:

    def test_exception_type(self):
        assert get_origin(ExceptionType) is type
        assert get_args(ExceptionType) == (Exception,)


class TestTracebackAndFrameTypes:

    def test_traceback_type_matches_real_traceback(self):
        try:
            raise RuntimeError
        except RuntimeError as exc:
            assert isinstance(exc.__traceback__, TracebackType)

    def test_frame_type_matches_real_frame(self):
        try:
            raise RuntimeError
        except RuntimeError as exc:
            assert isinstance(exc.__traceback__.tb_frame, FrameType)  # type: ignore

    def test_traceback_type_is_type(self):
        assert isinstance(TracebackType, type)

    def test_frame_type_is_type(self):
        assert isinstance(FrameType, type)

    def test_traceback_type_name(self):
        assert TracebackType.__name__ == "traceback"

    def test_frame_type_name(self):
        assert FrameType.__name__ == "frame"


class TestModuleExports:
    def test_all_exports_exist(self):
        import _errortools.typing as mod

        for name in mod.__all__:
            assert hasattr(mod, name), f"Missing exported name: {name}"

    def test_expected_exports(self):
        import _errortools.typing as mod

        expected = {
            "PureBaseExceptionType",
            "ContextExceptionType",
            "BaseErrorCodesType",
            "AnyErrorCode",
            "InputError",
            "AccessError",
            "LookupError_",
            "RuntimeError_",
            "ExceptionType",
            "TracebackType",
            "FrameType",
        }
        assert set(mod.__all__) == expected


def test_all_errors_can_be_raised():
    for exc_cls in get_args(AnyErrorCode):
        with pytest.raises(exc_cls):
            raise exc_cls("Test error")
