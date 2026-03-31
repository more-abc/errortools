"""Base exception classes with general-purpose error code support."""

from __future__ import annotations

from typing import Any, Optional
import traceback
import uuid

from .base.base import ErrorToolsBaseException

__all__ = [
    "BaseErrorCodes",
    "InvalidInputError",
    "NotFoundError",
    "AccessDeniedError",
    "ConfigurationError",
    "RuntimeFailure",
    "TimeoutFailure",
]


class BaseErrorCodes(ErrorToolsBaseException):
    """A base exception with class-level error code and default detail.

    Subclass and override `code` and `default_detail` to define
    domain-specific exceptions with stable, machine-readable codes.  The
    ``detail`` passed at raise-time overrides the class default.

    Error code ranges (by convention):

    - ``1xxx`` — input / validation
    - ``2xxx`` — access / permission
    - ``3xxx`` — resource lookup
    - ``4xxx`` — runtime / execution
    - ``5xxx`` — configuration / setup
    - ``-1``   — unspecified

    Attributes:
        code: Integer error code for this exception class.  Defaults to ``-1``.
        default_detail: Fallback message used when no *detail* is supplied.
        trace_id: Unique UUID for this error instance.
        context: Dictionary for request/user/business context data.
        cause: Optional root cause exception.
        chain: Full list of nested exceptions in the error chain.

    Example:
        >>> class PaymentError(BaseErrorCodes):
        ...     code = 6001
        ...     default_detail = "Payment processing failed."
        >>> raise PaymentError()
        Traceback (most recent call last):
            ...
        PaymentError: [6001] Payment processing failed.
        >>> raise PaymentError("card declined")
        Traceback (most recent call last):
            ...
        PaymentError: [6001] card declined
    """

    code: int = -1
    default_detail: str = "An error occurred."

    def __init__(self, detail: str | None = None) -> None:
        """Initialise the exception with an optional detail message.

        Args:
            detail: Human-readable description of the error.  Falls back to
                `default_detail` when ``None``.
        """
        self.detail = detail if detail is not None else self.default_detail
        self.trace_id: str = uuid.uuid4().hex
        self.context: dict[str, Any] = {}
        self.cause: Optional[BaseErrorCodes] = None
        super().__init__(self.detail)

    def __str__(self) -> str:
        return f"[{self.code}] {self.detail}"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(detail={self.detail!r}, "
            f"code={self.code!r}, trace_id={self.trace_id!r})"
        )

    def with_context(self, **kwargs: Any) -> "BaseErrorCodes":
        """Attach key-value context to this error.

        Example:

            >>> e = InvalidInputError().with_context(user_id=123, field="email")
            >>> e.context
            {'user_id': 123, 'field': 'email'}
        """
        self.context.update(kwargs)
        return self

    def with_cause(self, cause: Exception) -> "BaseErrorCodes":
        """Set a root cause exception and preserve the chain.

        Example:

            >>> try:
            ...     1 / 0
            ... except Exception as exc:
            ...     raise RuntimeFailure().with_cause(exc)
        """
        if isinstance(cause, BaseErrorCodes):
            self.cause = cause
        self.__cause__ = cause
        return self

    @property
    def chain(self) -> list[dict[str, Any]]:
        """Return the full chain of exceptions from root to leaf."""
        chain = []
        exc: Optional[BaseErrorCodes] = self
        while exc:
            chain.append(
                {
                    "type": exc.__class__.__name__,
                    "code": exc.code,
                    "detail": exc.detail,
                    "trace_id": exc.trace_id,
                    "context": exc.context,
                }
            )
            exc = exc.cause if isinstance(exc, BaseErrorCodes) else None
        return chain

    @property
    def traceback(self) -> str:
        """Return a clean, safe short traceback string."""
        tb = self.__traceback__
        if not tb:
            return "no traceback"
        lines = traceback.format_tb(tb, limit=4)
        return " | ".join(line.strip() for line in lines if line.strip())

    @classmethod
    def invalid_input(cls, detail: str | None = None) -> InvalidInputError:
        """Return an `InvalidInputError` (1001) instance."""
        return InvalidInputError(detail)

    @classmethod
    def not_found(cls, detail: str | None = None) -> NotFoundError:
        """Return a `NotFoundError` (3001) instance."""
        return NotFoundError(detail)

    @classmethod
    def access_denied(cls, detail: str | None = None) -> AccessDeniedError:
        """Return an `AccessDeniedError` (2001) instance."""
        return AccessDeniedError(detail)

    @classmethod
    def configuration_error(cls, detail: str | None = None) -> ConfigurationError:
        """Return a `ConfigurationError` (5001) instance."""
        return ConfigurationError(detail)

    @classmethod
    def runtime_failure(cls, detail: str | None = None) -> RuntimeFailure:
        """Return a `RuntimeFailure` (4001) instance."""
        return RuntimeFailure(detail)

    @classmethod
    def timeout_failure(cls, detail: str | None = None) -> TimeoutFailure:
        """Return a `TimeoutFailure` (4002) instance."""
        return TimeoutFailure(detail)


# ----------------------------------------------------------------------
# Predefined subclasses — general application categories
# ----------------------------------------------------------------------


class InvalidInputError(BaseErrorCodes):
    """1001 — Input failed validation or is of the wrong type/format."""

    code = 1001
    default_detail = "Invalid input."


class AccessDeniedError(BaseErrorCodes):
    """2001 — The caller lacks permission to perform the requested action."""

    code = 2001
    default_detail = "Access denied."


class NotFoundError(BaseErrorCodes):
    """3001 — The requested resource or item could not be located."""

    code = 3001
    default_detail = "Resource not found."


class RuntimeFailure(BaseErrorCodes):
    """4001 — An unexpected failure occurred during execution."""

    code = 4001
    default_detail = "Runtime failure."


class TimeoutFailure(BaseErrorCodes):
    """4002 — An operation exceeded its allowed time limit."""

    code = 4002
    default_detail = "Operation timed out."


class ConfigurationError(BaseErrorCodes):
    """5001 — The application is misconfigured or missing required settings."""

    code = 5001
    default_detail = "Configuration error."
