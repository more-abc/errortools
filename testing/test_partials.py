"""Tests for _errortools/partials.py — partial function wrappers."""

import warnings
import pytest

from _errortools.partial import (
    # ignore
    ignoreTypeError,
    ignoreValueError,
    ignoreIndexError,
    ignoreKeyError,
    ignoreAttributeError,
    ignoreNameError,
    ignoreZeroDivisionError,
    ignoreFileNotFoundError,
    ignorePermissionError,
    ignoreOSError,
    ignoreIOError,
    ignoreRuntimeError,
    ignoreNotImplementedError,
    ignoreOverflowError,
    ignoreTimeoutError,
    # fast_ignore
    fast_ignoreTypeError,
    fast_ignoreValueError,
    fast_ignoreIndexError,
    fast_ignoreKeyError,
    fast_ignoreAttributeError,
    fast_ignoreNameError,
    fast_ignoreZeroDivisionError,
    fast_ignoreFileNotFoundError,
    ignoreSubclassException,
    ignoreSubclassOSError,
    # ignore_warns
    ignoreUserWarning,
    ignoreDeprecationWarning,
    retry_1,
    retry_2,
    retry_3,
    retry_1_delay_1s,
)


# =============================================================================
# ignore partials
# =============================================================================
class TestIgnorePartials:
    def test_ignoreTypeError(self):
        with ignoreTypeError():
            raise TypeError

    def test_ignoreValueError(self):
        with ignoreValueError():
            raise ValueError

    def test_ignoreIndexError(self):
        with ignoreIndexError():
            raise IndexError

    def test_ignoreKeyError(self):
        with ignoreKeyError():
            raise KeyError

    def test_ignoreAttributeError(self):
        with ignoreAttributeError():
            raise AttributeError

    def test_ignoreNameError(self):
        with ignoreNameError():
            raise NameError

    def test_ignoreZeroDivisionError(self):
        with ignoreZeroDivisionError():
            _e = 1 / 0
            del _e

    def test_ignoreFileNotFoundError(self):
        with ignoreFileNotFoundError():
            open("no_such_file.txt")

    def test_ignorePermissionError(self):
        with ignorePermissionError():
            raise PermissionError

    def test_ignoreOSError(self):
        with ignoreOSError():
            raise OSError

    def test_ignoreIOError(self):
        with ignoreIOError():
            raise OSError

    def test_ignoreRuntimeError(self):
        with ignoreRuntimeError():
            raise RuntimeError

    def test_ignoreNotImplementedError(self):
        with ignoreNotImplementedError():
            raise NotImplementedError

    def test_ignoreOverflowError(self):
        with ignoreOverflowError():
            raise OverflowError

    def test_ignoreTimeoutError(self):
        with ignoreTimeoutError():
            raise TimeoutError


# =============================================================================
# fast_ignore partials
# =============================================================================
class TestFastIgnorePartials:
    def test_fast_ignoreTypeError(self):
        with fast_ignoreTypeError():
            raise TypeError

    def test_fast_ignoreValueError(self):
        with fast_ignoreValueError():
            raise ValueError

    def test_fast_ignoreIndexError(self):
        with fast_ignoreIndexError():
            raise IndexError

    def test_fast_ignoreKeyError(self):
        with fast_ignoreKeyError():
            raise KeyError

    def test_fast_ignoreAttributeError(self):
        with fast_ignoreAttributeError():
            raise AttributeError

    def test_fast_ignoreNameError(self):
        with fast_ignoreNameError():
            raise NameError

    def test_fast_ignoreZeroDivisionError(self):
        with fast_ignoreZeroDivisionError():
            _e = 1 / 0
            del _e

    def test_fast_ignoreFileNotFoundError(self):
        with fast_ignoreFileNotFoundError():
            raise FileNotFoundError


# =============================================================================
# ignore_subclass partials
# =============================================================================
class TestIgnoreSubclassPartials:
    def test_ignoreSubclassException(self):
        with ignoreSubclassException():
            raise RuntimeError

    def test_ignoreSubclassOSError(self):
        with ignoreSubclassOSError():
            raise FileNotFoundError


# =============================================================================
# ignore_warns partials
# =============================================================================
class TestIgnoreWarnsPartials:
    def test_ignoreUserWarning(self):
        with ignoreUserWarning():
            warnings.warn("test", UserWarning)

    def test_ignoreDeprecationWarning(self):
        with ignoreDeprecationWarning():
            warnings.warn("test", DeprecationWarning)


# =============================================================================
# retry partials
# =============================================================================
class TestRetryPartials:
    def test_retry_1(self):
        n = 0

        @retry_1()
        def f():
            nonlocal n
            n += 1
            raise ValueError

        with pytest.raises(ValueError):
            f()
        assert n == 2

    def test_retry_2(self):
        n = 0

        @retry_2()
        def f():
            nonlocal n
            n += 1
            raise ValueError

        with pytest.raises(ValueError):
            f()
        assert n == 3

    def test_retry_3(self):
        n = 0

        @retry_3()
        def f():
            nonlocal n
            n += 1
            raise ValueError

        with pytest.raises(ValueError):
            f()
        assert n == 4

    def test_retry_1_delay_1s(self):
        import time

        t0 = time.time()

        @retry_1_delay_1s()
        def f():
            raise RuntimeError

        with pytest.raises(RuntimeError):
            f()
        assert time.time() - t0 >= 1.0
