"""Tests for _errortools/version.py."""

import pytest

from _errortools.version import (
    _get_version_tuple,
    __version__,
    __version_tuple__,
    __commit_id__,
    version,
    version_tuple,
    commit_id,
)

# =============================================================================
# _get_version_tuple function
# =============================================================================


class TestGetVersionTuple:
    def test_parse_full_version(self):
        assert _get_version_tuple("3.2.1") == (3, 2, 1)

    def test_parse_major_minor_only(self):
        assert _get_version_tuple("3.2") == (3, 2, 0)

    def test_parse_major_only(self):
        assert _get_version_tuple("3") == (3, 0, 0)

    def test_parse_empty_string(self):
        with pytest.raises(ValueError):
            _get_version_tuple("")

    def test_non_numeric_part_raises_value_error(self):
        with pytest.raises(ValueError):
            _get_version_tuple("3.2.a")

        with pytest.raises(ValueError):
            _get_version_tuple("a.b.c")

    def test_extra_components_ignored_after_three(self):
        assert _get_version_tuple("1.2.3.4.5") == (1, 2, 3)

    def test_trailing_dot_raises_value_error(self):
        with pytest.raises(ValueError):
            _get_version_tuple("3.2.")


# =============================================================================
# Module version constants
# =============================================================================


class TestVersionConstants:
    def test_version_string_matches(self):
        assert isinstance(__version__, str)
        assert version == __version__

    def test_version_tuple_matches_parsed(self):
        assert isinstance(__version_tuple__, tuple)
        assert len(__version_tuple__) == 3
        assert all(isinstance(i, int) for i in __version_tuple__)
        assert version_tuple == __version_tuple__

    def test_commit_id_is_none_or_string(self):
        assert __commit_id__ is None or isinstance(__commit_id__, str)
        assert commit_id is __commit_id__

    def test_version_tuple_matches_version_string(self):
        expected = _get_version_tuple(__version__)
        assert __version_tuple__ == expected
