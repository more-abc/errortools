"""Tests for _errortools/typing.py — type aliases."""

from typing import Union, get_args, get_origin

from _errortools.typing import (
    PureBaseExceptionType,
    ContextExceptionType,
    BaseErrorCodesType,
    AnyErrorCode,
    InputError,
    AccessError,
    LookupError_,
    RuntimeError_,
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

# =============================================================================
# Per-class aliases resolve to the correct class
# =============================================================================


class TestPerClassAliases:
    def test_pure_base_exception_type_is_pure_base_exception(self):
        assert PureBaseExceptionType is PureBaseException

    def test_context_exception_type_is_context_exception(self):
        assert ContextExceptionType is ContextException

    def test_base_error_codes_type_is_base_error_codes(self):
        assert BaseErrorCodesType is BaseErrorCodes

    def test_instances_satisfy_per_class_aliases(self):
        assert isinstance(PureBaseException(), PureBaseExceptionType)
        assert isinstance(ContextException(), ContextExceptionType)
        assert isinstance(BaseErrorCodes(), BaseErrorCodesType)

    def test_subclasses_satisfy_per_class_aliases(self):
        # ContextException is a subclass of PureBaseException
        assert isinstance(ContextException(), PureBaseExceptionType)
        # BaseErrorCodes is a subclass of both
        assert isinstance(BaseErrorCodes(), PureBaseExceptionType)
        assert isinstance(BaseErrorCodes(), ContextExceptionType)


# =============================================================================
# Simple aliases resolve to the correct class
# =============================================================================


class TestSimpleAliases:
    def test_input_error_is_invalid_input_error(self):
        assert InputError is InvalidInputError

    def test_access_error_is_access_denied_error(self):
        assert AccessError is AccessDeniedError

    def test_lookup_error_is_not_found_error(self):
        assert LookupError_ is NotFoundError

    def test_instances_satisfy_simple_aliases(self):
        assert isinstance(InvalidInputError(), InputError)
        assert isinstance(AccessDeniedError(), AccessError)
        assert isinstance(NotFoundError(), LookupError_)


# =============================================================================
# Union aliases contain the correct members
# =============================================================================


class TestUnionAliases:
    def test_any_error_code_is_union(self):
        assert get_origin(AnyErrorCode) is Union

    def test_any_error_code_contains_all_six(self):
        args = set(get_args(AnyErrorCode))
        assert args == {
            InvalidInputError,
            AccessDeniedError,
            NotFoundError,
            RuntimeFailure,
            TimeoutFailure,
            ConfigurationError,
        }

    def test_runtime_error_is_union(self):
        assert get_origin(RuntimeError_) is Union

    def test_runtime_error_contains_failure_and_timeout(self):
        args = set(get_args(RuntimeError_))
        assert args == {RuntimeFailure, TimeoutFailure}

    def test_all_six_are_instances_of_base_error_codes(self):
        for cls in get_args(AnyErrorCode):
            assert isinstance(cls(), BaseErrorCodes)


# =============================================================================
# __all__ completeness
# =============================================================================


class TestDunderAll:
    def test_all_exported_names_are_importable(self):
        import _errortools.typing as m
        for name in m.__all__:
            assert hasattr(m, name), f"{name!r} in __all__ but not defined"

    def test_all_contains_expected_names(self):
        import _errortools.typing as m
        expected = {
            "PureBaseExceptionType",
            "ContextExceptionType",
            "BaseErrorCodesType",
            "AnyErrorCode",
            "InputError",
            "AccessError",
            "LookupError_",
            "RuntimeError_",
        }
        assert expected == set(m.__all__)