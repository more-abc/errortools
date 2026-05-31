"""
errortools - a toolset for working with Python exceptions and warnings and logging.
"""

from typing import Any

from _errortools.raises import raises, assert_raises, raises_all, reraise
from _errortools.ignore import (
    ignore,
    ignore_subclass,
    ignore_warns,
)
from _errortools.decorator.timeout import timeout
from _errortools.decorator.retry import retry
from _errortools.errno import (
    get_errno_message,
    get_errno_name,
    get_all_errno_codes,
    is_valid_errno,
)
from _errortools.classes.group import BaseGroup, GroupErrors
from _errortools.decorator.cache import error_cache
from _errortools.decorator.deprecated import deprecated, experimental
from _errortools.decorator.handlers import suppress, convert
from _errortools.classes.errorcodes import (
    PureBaseException,
    ContextException,
    BaseErrorCodes,
    InvalidInputError,
    NotFoundError,
    AccessDeniedError,
    ConfigurationError,
    RuntimeFailure,
    TimeoutFailure,
)
from _errortools.classes.warn import (
    BaseWarning,
    DeprecatedWarning,
    PerformanceWarning,
    ResourceUsageWarning,
    RuntimeBehaviourWarning,
    ConfigurationWarning,
)
from _errortools.classes.abc import (
    ErrorCodeable,
    Warnable,
    Raiseable,
    Error,
)
from _errortools.classes.protocol import (
    ExceptionLike,
    ExceptionGroupLike,
    BaseExceptionGroupLike,
    BlockingIOErrorLike,
    NameErrorLike,
    StopIterationLike,
    SyntaxErrorLike,
    SystemExitLike,
    ImportErrorLike,
    UnicodeDecodeErrorLike,
    UnicodeEncodeErrorLike,
    UnicodeTranslateErrorLike,
    AttributeErrorLike,
    GroupErrorsLike,
)
from _errortools.typing import (
    AnyErrorCode,
    BaseErrorCodesType,
    PureBaseExceptionType,
    ContextExceptionType,
    ExceptionType,
    WarningType,
    TracebackType,
    FrameType,
)
from _errortools.plugins import run, register, list_all, get, remove, Registry
from _errortools.descriptor.errormsg import ErrorMsg
from _errortools.descriptor.nonblankmsg import NonBlankErrorMsg
from _errortools.version import (
    __version__,
    __version_tuple__,
    __commit_id__,
    version,
    version_tuple,
    commit_id,
)
from _errortools.metadata import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __url__,
    __fullname__,
    __signature__,
    __slug__,
    __uid__,
)

_DEPRECATED_NAMES: dict[str, tuple[str, str]] = {
    "InputError": ("InputError", "Use InvalidInputError directly."),
    "AccessError": ("AccessError", "Use AccessDeniedError directly."),
    "LookupError_": ("LookupError_", "Use NotFoundError directly."),
    "RuntimeError_": ("RuntimeError_", "Use RuntimeFailure or TimeoutFailure directly."),
    "fast_ignore": ("fast_ignore", "Use errortools.future.super_fast_ignore instead."),
}


class ErrortoolsDeprecationWarning(DeprecationWarning):
    """Base class for warnings about deprecated features in errortools module."""


def __getattr__(name: str):
    import importlib
    import warnings

    if name in _DEPRECATED_NAMES:
        attr_name, reason = _DEPRECATED_NAMES[name]
        warnings.warn(
            f"errortools.{attr_name} is deprecated. {reason}",
            ErrortoolsDeprecationWarning,
            stacklevel=2,
        )
        return globals()[f"_{name}"] if f"_{name}" in globals() else globals().get(name)

    if name in ("future", "logging", "partial"):
        return importlib.import_module(f"_errortools.{name}")

    try:
        return get(name)
    except ValueError:
        pass

    raise AttributeError(f"module 'errortools' has no attribute {name!r}")


def __dir__() -> list[str]:
    return __all__


class PluginNamespace:
    def __getattr__(self, name: str) -> Any:
        plugin = get(name)
        if plugin is None:
            raise AttributeError(f"Plugin {name!r} not found")
        return plugin


plugins = PluginNamespace()

__all__ = [
    # functions
    "raises",
    "raises_all",
    "assert_raises",
    "reraise",
    "ignore",
    "fast_ignore",
    "ignore_subclass",
    "ignore_warns",
    "timeout",
    "retry",
    "get_errno_message",
    "get_errno_name",
    "get_all_errno_codes",
    "is_valid_errno",
    "deprecated",
    "experimental",
    "error_cache",
    "suppress",
    "convert",
    "TracebackType",
    "FrameType",
    # classes
    "GroupErrors",
    "BaseGroup",
    "BaseErrorCodes",
    "InvalidInputError",
    "NotFoundError",
    "AccessDeniedError",
    "ConfigurationError",
    "RuntimeFailure",
    "TimeoutFailure",
    "BaseWarning",
    "DeprecatedWarning",
    "PerformanceWarning",
    "ResourceUsageWarning",
    "RuntimeBehaviourWarning",
    "ConfigurationWarning",
    "ErrorCodeable",
    "Warnable",
    "Raiseable",
    "ErrorMsg",
    "NonBlankErrorMsg",
    "PureBaseException",
    "ContextException",
    "Error",
    "ExceptionLike",
    "ExceptionGroupLike",
    "BaseExceptionGroupLike",
    "BlockingIOErrorLike",
    "NameErrorLike",
    "StopIterationLike",
    "SystemExitLike",
    "ImportErrorLike",
    "SyntaxErrorLike",
    "UnicodeDecodeErrorLike",
    "UnicodeEncodeErrorLike",
    "UnicodeTranslateErrorLike",
    "AttributeErrorLike",
    "GroupErrorsLike",
    "ErrortoolsDeprecationWarning",
    # for type hints
    "PureBaseExceptionType",
    "ContextExceptionType",
    "BaseErrorCodesType",
    "AnyErrorCode",
    "InputError",
    "AccessError",
    "LookupError_",
    "RuntimeError_",
    "ExceptionType",
    "WarningType",
    # plugins
    "register",
    "get",
    "list_all",
    "run",
    "remove",
    "Registry",
    # metadata
    "__version__",
    "__version_tuple__",
    "__commit_id__",
    "version",
    "version_tuple",
    "commit_id",
    "__author__",
    "__author_email__",
    "__copyright__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__fullname__",
    "__signature__",
    "__slug__",
    "__uid__",
    # submodules
    "future",
    "logging",
    "partial",
]

__all__.append("plugins")
