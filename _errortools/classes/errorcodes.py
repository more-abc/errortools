import uuid
import traceback
from typing import Any, Optional

__all__ = [
    "PureBaseException",
    "ContextException",
    "BaseErrorCodes",
    "InvalidInputError",
    "AccessDeniedError",
    "NotFoundError",
    "RuntimeFailure",
    "TimeoutFailure",
    "ConfigurationError",
]


# ==============================================
# 1. Pure Base Exception Class (core structure only, no additional capabilities)
# ==============================================
class PureBaseException(Exception):
    """
    Pure Base Exception Class (core skeleton)
    Only provides error code, default prompt message, basic initialization and string formatting, no additional functions included
    """

    # Class attributes: default error code and prompt, which can be overridden by subclasses
    code: int = -1
    default_detail: str = "An error occurred."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize pure base exception
        Args:
            detail: Custom error prompt, use default prompt (default_detail) when None
        """
        self.detail = detail if detail is not None else self.default_detail
        super().__init__(self.detail)

    def __str__(self) -> str:
        """Format exception string, unified format: [Error Code] Error Prompt"""
        return f"[{self.code}] {self.detail}"

    def __repr__(self) -> str:
        """Format exception repr information for easy debugging of core attributes"""
        return f"{type(self).__name__}(detail={self.detail!r}, code={self.code!r})"


# ==============================================
# 2. Context/Exception Chain Common Capability Class (core extension functions)
# ==============================================
class ContextException(PureBaseException):
    """
    Common Capability Exception Class (extension layer)
    Inherits from pure base exception, providing common capabilities such as trace ID, context management, exception chain, and simplified stack trace
    """

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize common capability exception, inherit parent class initialization and add extended attributes
        Args:
            detail: Custom error prompt, use default prompt (default_detail) when None
        """
        super().__init__(detail)
        # Extended attributes: trace ID (unique identifier for a single exception), context dictionary, root cause exception
        self.trace_id: str = uuid.uuid4().hex
        self.context: dict[str, Any] = {}
        self.cause: Optional[ContextException] = None

    def __repr__(self) -> str:
        """Format exception repr information including trace_id for debugging"""
        return f"{type(self).__name__}(detail={self.detail!r}, code={self.code!r}, trace_id={self.trace_id!r})"

    def with_context(self, **kwargs: Any) -> "ContextException":
        """
        Attach context data to the exception (such as user ID, request parameters, etc.)
        Args:
            **kwargs: Context key-value pairs (any type)
        Returns:
            Self instance (supports method chaining)
        """
        self.context.update(kwargs)
        return self

    def with_cause(self, cause: Exception) -> "ContextException":
        """
        Set the root cause exception for the current exception, retain the exception chain for easy troubleshooting
        Args:
            cause: Root cause exception (can be any subclass of Exception)
        Returns:
            Self instance (supports method chaining)
        """
        if isinstance(cause, ContextException):
            self.cause = cause
        self.__cause__ = cause  # Retain native exception chain
        return self

    @property
    def chain(self) -> list[dict[str, Any]]:
        """
        Get the complete exception chain (from current exception to the bottom root cause exception)
        Returns:
            Exception chain list, each element contains core exception information (type, error code, prompt, etc.)
        """
        chain = []
        exc: Optional[ContextException] = self
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
            exc = exc.cause
        return chain

    @property
    def traceback(self) -> str:
        """
        Get simplified exception stack trace (limited to 4 lines) for easy log output and troubleshooting
        Returns:
            Simplified stack trace string, no blank lines, each line separated by |
        """
        tb = self.__traceback__
        if not tb:
            return "no traceback"
        lines = traceback.format_tb(tb, limit=4)
        return " | ".join(line.strip() for line in lines if line.strip())


# ==============================================
# 3. Common Error Class (business convenience factory methods)
# ==============================================
class BaseErrorCodes(ContextException):
    """
    Common Error Class (business convenience layer)
    Inherits from common capability class, providing factory methods for various predefined errors to simplify business exception throwing
    """

    @classmethod
    def invalid_input(cls, detail: str | None = None) -> "InvalidInputError":
        """
        Input Validation Error (Error Code: 1001)
        Args:
            detail: Custom error prompt, use the default prompt of InvalidInputError if not provided
        Returns:
            InvalidInputError instance
        """
        return InvalidInputError(detail)

    @classmethod
    def not_found(cls, detail: str | None = None) -> "NotFoundError":
        """
        Resource Not Found Error (Error Code: 3001)
        Args:
            detail: Custom error prompt, use the default prompt of NotFoundError if not provided
        Returns:
            NotFoundError instance
        """
        return NotFoundError(detail)

    @classmethod
    def access_denied(cls, detail: str | None = None) -> "AccessDeniedError":
        """
        Access Denied Error (Error Code: 2001)
        Args:
            detail: Custom error prompt, use the default prompt of AccessDeniedError if not provided
        Returns:
            AccessDeniedError instance
        """
        return AccessDeniedError(detail)

    @classmethod
    def configuration_error(cls, detail: str | None = None) -> "ConfigurationError":
        """
        Configuration Error (Error Code: 5001)
        Args:
            detail: Custom error prompt, use the default prompt of ConfigurationError if not provided
        Returns:
            ConfigurationError instance
        """
        return ConfigurationError(detail)

    @classmethod
    def runtime_failure(cls, detail: str | None = None) -> "RuntimeFailure":
        """
        Runtime Failure (Error Code: 4001)
        Args:
            detail: Custom error prompt, use the default prompt of RuntimeFailure if not provided
        Returns:
            RuntimeFailure instance
        """
        return RuntimeFailure(detail)

    @classmethod
    def timeout_failure(cls, detail: str | None = None) -> "TimeoutFailure":
        """
        Timeout Failure (Error Code: 4002)
        Args:
            detail: Custom error prompt, use the default prompt of TimeoutFailure if not provided
        Returns:
            TimeoutFailure instance
        """
        return TimeoutFailure(detail)


# ==============================================
# Specific Business Error Subclasses (unified naming and format, corresponding to common error codes)
# ==============================================
class InvalidInputError(BaseErrorCodes):
    """Input Validation Error (1001): Used for scenarios where parameter or input format validation fails"""

    code = 1001
    default_detail = "Invalid input."


class NotFoundError(BaseErrorCodes):
    """Resource Not Found Error (3001): Used for scenarios where the queried resource does not exist"""

    code = 3001
    default_detail = "Resource not found."


class AccessDeniedError(BaseErrorCodes):
    """Access Denied Error (2001): Used for scenarios where access to resources is not permitted"""

    code = 2001
    default_detail = "Access denied."


class ConfigurationError(BaseErrorCodes):
    """Configuration Error (5001): Used for scenarios where system or service configuration is abnormal"""

    code = 5001
    default_detail = "Configuration error."


class RuntimeFailure(BaseErrorCodes):
    """Runtime Failure (4001): Used for unknown exception scenarios during system operation"""

    code = 4001
    default_detail = "Runtime failure."


class TimeoutFailure(BaseErrorCodes):
    """Timeout Failure (4002): Used for request or operation timeout scenarios"""

    code = 4002
    default_detail = "Operation timed out."
