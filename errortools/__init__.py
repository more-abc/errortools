"""
errortools - a toolset for working with Python exceptions.
"""

from _errortools.raises import (raises, 
                     assert_raises, 
                     raises_all,
                     reraise)
from _errortools.ignore import (ignore,
                     ignore_subclass,
                     ignore_warns)
from _errortools.groups import (BaseGroup,
                    GroupErrors)
from _errortools.cached.cache import error_cache
from _errortools._types import TracebackType, FrameType
from _errortools._traceback import use_traceback
from _errortools.traceback._config import TracebackConfig
from _errortools.traceback._color_codes import ColorCodes
from _errortools.classes.errorcodes import (
    BaseErrorCodes,
    InvalidInputError,
    NotFoundError,
    AccessDeniedError,
    ConfigurationError,
    RuntimeFailure,
    TimeoutFailure)
from _errortools.classes.warn import (
    BaseWarning,
    DeprecatedWarning,
    PerformanceWarning,
    ResourceUsageWarning,
    RuntimeBehaviourWarning,
    ConfigurationWarning)
from _errortools.methods import (
    ErrorSetAttrMixin,
    ErrorAttrCheckMixin,
    ErrorAttrDeletionMixin,
    ErrorAttrMixin)

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
    "use_traceback",
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
    "TracebackConfig",
    "ColorCodes"
]

__version__ = "0.23"
