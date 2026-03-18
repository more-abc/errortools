"""
errortools - a toolset for working with Python exceptions.
"""

from .._errortools.raises import (raises, 
                     assert_raises, 
                     raises_all,
                     reraise)
from .._errortools.ignore import (ignore,
                     ignore_subclass,
                     ignore_warns)
from .._errortools.groups import (BaseGroup,
                    GroupErrors)
from .._errortools.cached.cache import error_cache
from .._errortools.classes.errorcodes import (
    BaseErrorCodes,
    InvalidInputError,
    NotFoundError,
    AccessDeniedError,
    ConfigurationError,
    RuntimeFailure,
    TimeoutFailure)
from .._errortools.classes.warn import (
    BaseWarning,
    DeprecatedWarning,
    PerformanceWarning,
    ResourceUsageWarning,
    RuntimeBehaviourWarning,
    ConfigurationWarning)
from .._errortools.classes.methods import (
    ErrorSetAttrMixin,
    ErrorAttrCheckMixin,
    ErrorAttrDeletionMixin,
    ErrorAttrMixin)

SafeIgnoreErrors: bool = True
"""If True, just import plugin `safe_ignore` for use `ignore` and `ignore_subclass` more safe."""

if SafeIgnoreErrors is True:
    from .._errortools.plugins import safe_ignore

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
    # setting vars
    "SafeIgnoreErrors"
]

__version__ = "0.19.339"
