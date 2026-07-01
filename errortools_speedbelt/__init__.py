"""
errortools-speedbelt — High-speed core for errortools.
Downloaded alongside the :mod:`errortools` module.

.. versionadded:: 3.6
"""

from typing import Final

from errortools import VersionInfo

from .support_c_ext import ERRORTOOLS_SUPPORTS_C_EXTENSIONS  # noqa: F401

__version__: Final[str] = "0.1.2"
__version_info__: Final[VersionInfo] = VersionInfo.from_str(__version__)
__version_tuple__: Final[tuple[int, int, int]] = __version_info__.to_tuple()
