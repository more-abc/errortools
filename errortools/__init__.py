"""
errortools - a toolset for working with Python exceptions and warnings and logging.
"""

from __future__ import annotations

import importlib
import sys
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
from _errortools.classes.group import BaseGroup, GroupErrors  # noqa: F401
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
from _errortools.classes.protocol import (  # noqa: F401
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
from _errortools.plugins import run, register, list_all, get, has, remove, clear, Registry
from _errortools.descriptor.errormsg import ErrorMsg
from _errortools.descriptor.nonblankmsg import NonBlankErrorMsg
from _errortools.version import (
    __version__,
    __version_tuple__,
    __commit_id__,
    __version_info__,
    version,
    version_tuple,
    commit_id,
    version_info,
    VersionInfo,
    get_version_tuple,
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
from _errortools.warning_types import ErrortoolsDeprecationWarning, ErrortoolsWarning
from _errortools.warning_types import _deprecated_getattr
from _errortools.warning_types import _DEPRECATED_NAMES


# Public alias for the deprecated-name dispatcher so tests can introspect it.
def __getattr__(name: str) -> Any:
    """Module-level :pep:`562` lazy-attribute dispatcher.

    Order of resolution:

    1. **Deprecated names** (Table ``_DEPRECATED_NAMES``): emit a
       structured :class:`ErrortoolsDeprecationWarning` and return the
       canonical replacement registered in ``_DEPRECATED_RESOLVERS``.
    2. **Lazy submodules** (``future`` / ``logging``): import on demand.
    3. **Plugin namespace**: delegate to :func:`_errortools.plugins.get`.
    4. **Fall-through**: raise :class:`AttributeError`.
    """
    if name in _DEPRECATED_NAMES:
        return _deprecated_getattr(name)

    if name == "future" or name == "logging":
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

_PYTHON_3_11_CAN_USE: list[str] = [
    "GroupErrors",
    "BaseGroup",
    "BaseExceptionGroupLike",
    "ExceptionGroupLike",
    "GroupErrorsLike",
]
_PYTHON_3_10_CAN_USE: list[str] = [
    "NameErrorLike",
    "AttributeErrorLike",
]
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
    "BlockingIOErrorLike",
    "StopIterationLike",
    "SystemExitLike",
    "ImportErrorLike",
    "SyntaxErrorLike",
    "UnicodeDecodeErrorLike",
    "UnicodeEncodeErrorLike",
    "UnicodeTranslateErrorLike",
    "ErrortoolsWarning",
    "ErrortoolsDeprecationWarning",
    "VersionInfo",
    "get_version_tuple",
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
    "has",
    "list_all",
    "run",
    "remove",
    "clear",
    "Registry",
    # metadata
    "__version__",
    "__version_tuple__",
    "__commit_id__",
    "__version_info__",
    "version",
    "version_tuple",
    "commit_id",
    "version_info",
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

if sys.version_info >= (3, 11):
    __all__.append(_PYTHON_3_11_CAN_USE)

if sys.version_info >= (3, 10):
    __all__.append(_PYTHON_3_10_CAN_USE)
