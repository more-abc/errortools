"""Main base classes for all."""

from abc import ABC


class ErrorToolsBaseException(ABC, Exception):
    """Base Exception in `errortools` module."""

    pass


class ErrorToolsBaseWarning(ABC, Warning):
    """Base Warning in `errortools` module."""

    pass
