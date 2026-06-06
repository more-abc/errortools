"""Tests for `errortools` module. Using pytest."""

import warnings

from _errortools.version import _get_version_tuple

__all__ = [
    "__version__",
    "__version_tuple__",
    "HAS_PYTEST",
    "NO_ONE_CHANGE_VERSION",
]
__version__ = "1.3.3"
__version_tuple__ = _get_version_tuple(__version__)

try:
    import pytest
except ImportError:
    HAS_PYTEST = False
else:
    HAS_PYTEST = True

_NOTHING = "<invalid_version>"

if not isinstance(__version__, str):
    raise RuntimeError("__version__ must be a string")

if __version__ == _NOTHING:
    NO_ONE_CHANGE_VERSION = True
    warnings.warn(
        "__version__ has not been set to a valid value",
        stacklevel=1,
    )
else:
    NO_ONE_CHANGE_VERSION = False
