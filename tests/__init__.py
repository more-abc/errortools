"""Tests for `errortools` module. Using pytest."""

__version__ = "1.4"

try:
    import pytest
except ImportError:
    # A constant used to determine whether the pytest module exists.
    #  If it exists, tests can run normally; otherwise, a warning will be printed.
    HAS_PYTEST = False
else:
    HAS_PYTEST = True
