"""Tests for _errortools/const.py — constants."""

from _errortools.const import (
    LARGE_ERROR_CACHE_SIZE,
    SMALL_ERROR_CACHE_SIZE,
    DEFAULT_ERROR_CACHE_SIZE,
    UNLIMITED_ERROR_CACHE,
)


def test_constant_types():
    assert isinstance(LARGE_ERROR_CACHE_SIZE, int)
    assert isinstance(SMALL_ERROR_CACHE_SIZE, int)
    assert isinstance(DEFAULT_ERROR_CACHE_SIZE, int)
    # ``UNLIMITED_ERROR_CACHE`` was NoneType
    assert not isinstance(UNLIMITED_ERROR_CACHE, int)


def test_default_cache_is_valid():
    assert DEFAULT_ERROR_CACHE_SIZE > 0
    assert SMALL_ERROR_CACHE_SIZE <= DEFAULT_ERROR_CACHE_SIZE <= LARGE_ERROR_CACHE_SIZE


def test_cache_constant_value():
    assert DEFAULT_ERROR_CACHE_SIZE == 128
    assert SMALL_ERROR_CACHE_SIZE == 64
    assert LARGE_ERROR_CACHE_SIZE == 1024
    assert UNLIMITED_ERROR_CACHE == None
