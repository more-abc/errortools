"""Base exception classes with general-purpose error code support."""

from __future__ import annotations

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
        super().__init__(self.detail)

    def __str__(self) -> str:
        return f"[{self.code}] {self.detail}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(detail={self.detail!r}, code={self.code!r})"

    # ------------------------------------------------------------------
    # Factory classmethods
    # ------------------------------------------------------------------

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
