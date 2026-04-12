"""
errortools - a toolset for working with Python exceptions and warnings and logging.
"""

from _errortools.raises import raises, assert_raises, raises_all, reraise
from _errortools.ignore import (
    ignore,
    ignore_subclass,
    ignore_warns,
    fast_ignore,
    timeout,
    retry,
)
from _errortools.classes.group import BaseGroup, GroupErrors
from _errortools.decorator.cache import error_cache
from _errortools.decorator.deprecated import deprecated
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
from _errortools.methods import (
    ErrorSetAttrMixin,
    ErrorAttrCheckMixin,
    ErrorAttrDeletionMixin,
    ErrorAttrMixin,
)
from _errortools.classes.abc import (
    ErrorAttrable,
    ErrorCodeable,
    Warnable,
    Raiseable,
    Error,
)
from _errortools.typing import (
    AnyErrorCode,
    BaseErrorCodesType,
    PureBaseExceptionType,
    ContextExceptionType,
    RuntimeError_,
    LookupError_,
    InputError,
    AccessError,
    ExceptionType,
    TracebackType,
    FrameType,
)
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
import _errortools.future as future
import _errortools.logging as logging
import _errortools.partial as partial

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
    "deprecated",
    "error_cache",
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
    "ErrorAttrMixin",
    "ErrorAttrDeletionMixin",
    "ErrorAttrCheckMixin",
    "ErrorSetAttrMixin",
    "ErrorAttrable",
    "ErrorCodeable",
    "Warnable",
    "Raiseable",
    "ErrorMsg",
    "NonBlankErrorMsg",
    "PureBaseException",
    "ContextException",
    "Error",
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
