"""Tests for _errortools/errno.py — errno tools."""

import errno

import pytest

from _errortools.errno import (
    get_errno_name,
    get_errno_message,
    get_all_errno_codes,
    is_valid_errno,
    strerror,
)
from . import HAS_PYTEST

if not HAS_PYTEST:
    print("pytest is required to run these tests, skip run test_errno.py")
    exit(0)


class TestGetErrnoName:
    def test_valid_errno_enoent(self):
        assert get_errno_name(errno.ENOENT) == "ENOENT"

    def test_valid_errno_eacces(self):
        assert get_errno_name(errno.EACCES) == "EACCES"

    def test_invalid_errno_code(self):
        assert get_errno_name(9999) is None

    def test_errno_zero(self):
        assert get_errno_name(0) is None


class TestGetErrnoMessage:
    def test_valid_errno_message(self):
        message = get_errno_message(errno.ENOENT)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_invalid_errno_message(self):
        with pytest.raises(ValueError):
            message = get_errno_message(9999)
            assert "Unknown error" in message or len(message) > 0

    def test_errno_two_message(self):
        message = get_errno_message(2)
        assert isinstance(message, str)


class TestGetAllErrnocodes:
    def test_returns_dict(self):
        codes = get_all_errno_codes()
        assert isinstance(codes, dict)

    def test_contains_enoent(self):
        codes = get_all_errno_codes()
        assert "ENOENT" in codes
        assert codes["ENOENT"] == errno.ENOENT

    def test_contains_eacces(self):
        codes = get_all_errno_codes()
        assert "EACCES" in codes
        assert codes["EACCES"] == errno.EACCES

    def test_all_values_are_integers(self):
        codes = get_all_errno_codes()
        for _, code in codes.items():
            assert isinstance(code, int)

    def test_all_keys_are_uppercase(self):
        codes = get_all_errno_codes()
        for name in codes.keys():
            assert name.isupper()


class TestIsValidErrno:
    def test_valid_errno_enoent(self):
        assert is_valid_errno(errno.ENOENT) is True

    def test_valid_errno_eacces(self):
        assert is_valid_errno(errno.EACCES) is True

    def test_invalid_errno(self):
        assert is_valid_errno(9999) is False

    def test_errno_zero(self):
        assert is_valid_errno(0) is False


class TestStrerror:
    def test_enoent_message(self):
        message = strerror(errno.ENOENT)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_eacces_message(self):
        message = strerror(errno.EACCES)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_invalid_errno_fallback(self):
        message = strerror(9999)
        assert isinstance(message, str)
        assert "Unknown error" in message or len(message) > 0

    def test_consistency_with_os_strerror(self):
        import os

        code = errno.ENOENT
        try:
            expected = os.strerror(code)
            assert strerror(code) == expected
        except (ValueError, OSError):
            pass
