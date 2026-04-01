"""Public type aliases for _errortools exception classes."""

from typing import TypeAlias, Union

from .classes.errorcodes import (
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

__all__ = [
    "PureBaseExceptionType",
    "ContextExceptionType",
    "BaseErrorCodesType",
    "AnyErrorCode",
    "InputError",
    "AccessError",
    "LookupError_",
    "RuntimeError_",
]

# ---------------------------------------------------------------------------
# Per-class aliases
# ---------------------------------------------------------------------------

PureBaseExceptionType: TypeAlias = PureBaseException
"""Any instance of `PureBaseException` (the core skeleton layer)."""

ContextExceptionType: TypeAlias = ContextException
"""Any instance of `ContextException` (adds trace_id / context / cause)."""

BaseErrorCodesType: TypeAlias = BaseErrorCodes
"""Any instance of `BaseErrorCodes` (adds factory classmethods)."""

# ---------------------------------------------------------------------------
# Semantic union aliases  (group related error types)
# ---------------------------------------------------------------------------

AnyErrorCode: TypeAlias = Union[
    InvalidInputError,
    AccessDeniedError,
    NotFoundError,
    RuntimeFailure,
    TimeoutFailure,
    ConfigurationError,
]
"""Union of all predefined error-code subclasses."""

InputError: TypeAlias = InvalidInputError
"""Alias for `InvalidInputError` (1001)."""

AccessError: TypeAlias = AccessDeniedError
"""Alias for `AccessDeniedError` (2001)."""

LookupError_: TypeAlias = NotFoundError
"""Alias for `NotFoundError` (3001). Trailing underscore avoids shadowing builtins."""

RuntimeError_: TypeAlias = Union[RuntimeFailure, TimeoutFailure]
"""Union of runtime-related errors: `RuntimeFailure` (4001) and `TimeoutFailure` (4002)."""