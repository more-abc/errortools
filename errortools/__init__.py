"""
errortools - a toolset for working with Python exceptions and warnings.
"""

from _errortools.raises import raises, assert_raises, raises_all, reraise
from _errortools.ignore import ignore, ignore_subclass, ignore_warns
from _errortools.groups import BaseGroup, GroupErrors
from _errortools.cached.cache import error_cache
from _errortools._types import TracebackType, FrameType
from _errortools.classes.errorcodes import (
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
from _errortools.abc import ErrorAttrable, ErrorCodeable, Warnable, Raiseable
from _errortools._version import (
    __version__,
    __version_tuple__,
    __commit_id__,
    version,
    version_tuple,
    commit_id,
)

__all__ = [
    # functions
    "raises",
    "raises_all",
    "assert_raises",
    "reraise",
    "ignore",
    "ignore_subclass",
    "ignore_warns",
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
    # metadata
    "__version__",
    "__version_tuple__",
    "__commit_id__",
    "version",
    "version_tuple",
    "commit_id",
]

__description__ = (
    "errortools - a toolset for working with Python exceptions and warnings"
)
