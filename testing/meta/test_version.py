"""Tests for _errortools/version.py."""

import pytest

from _errortools.version import (
    VersionInfo,
    get_version_tuple,
    __version__,
    __version_tuple__,
    __commit_id__,
    version,
    version_tuple,
    commit_id,
)

# =============================================================================
# get_version_tuple function
# =============================================================================


class TestGetVersionTuple:
    def test_parse_full_version(self):
        assert get_version_tuple("3.2.1") == (3, 2, 1)

    def test_parse_major_minor_only(self):
        assert get_version_tuple("3.2") == (3, 2, 0)

    def test_parse_major_only(self):
        assert get_version_tuple("3") == (3, 0, 0)

    def test_parse_empty_string(self):
        with pytest.raises(ValueError):
            get_version_tuple("")

    def test_non_numeric_part_raises_value_error(self):
        with pytest.raises(ValueError):
            get_version_tuple("3.2.a")

        with pytest.raises(ValueError):
            get_version_tuple("a.b.c")

    def test_extra_components_ignored_after_three(self):
        assert get_version_tuple("1.2.3.4.5") == (1, 2, 3)

    def test_trailing_dot_raises_value_error(self):
        with pytest.raises(ValueError):
            get_version_tuple("3.2.")

    def test_zero_components(self):
        assert get_version_tuple("0.0.0") == (0, 0, 0)

    def test_leading_zeros_are_accepted(self):
        # ``int("007")`` is legal Python and yields 7; the parser does not
        # treat the leading zero specially.
        assert get_version_tuple("007.002.01") == (7, 2, 1)

    def test_large_components(self):
        assert get_version_tuple("2025.12.31") == (2025, 12, 31)

    def test_returned_tuple_components_are_int(self):
        nums = get_version_tuple("1.2.3")
        assert all(isinstance(n, int) for n in nums)


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
        expected = get_version_tuple(__version__)
        assert __version_tuple__ == expected


# =============================================================================
# VersionInfo dataclass
# =============================================================================


class TestVersionInfoConstruction:
    def test_basic_construction(self):
        v = VersionInfo(3, 5, 1)
        assert v.major == 3
        assert v.minor == 5
        assert v.patch == 1

    def test_construction_with_zero(self):
        v = VersionInfo(0, 0, 0)
        assert v.major == v.minor == v.patch == 0

    def test_negative_components_are_stored_as_is(self):
        # The dataclass does not validate ranges; values are stored verbatim.
        v = VersionInfo(-1, -2, -3)
        assert v.major == -1
        assert v.minor == -2
        assert v.patch == -3

    def test_slots_prevent_dict_creation(self):
        v = VersionInfo(1, 2, 3)
        with pytest.raises(AttributeError):
            v.spurious = 4  # type: ignore[attr-defined]


class TestVersionInfoFromStr:
    def test_full_string(self):
        v = VersionInfo.from_str("3.5.1")
        assert v == VersionInfo(3, 5, 1)

    def test_major_minor_only(self):
        assert VersionInfo.from_str("3.2") == VersionInfo(3, 2, 0)

    def test_major_only(self):
        assert VersionInfo.from_str("3") == VersionInfo(3, 0, 0)

    def test_extra_components_are_ignored(self):
        assert VersionInfo.from_str("1.2.3.4.5") == VersionInfo(1, 2, 3)

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            VersionInfo.from_str("")

    def test_trailing_dot_raises_value_error(self):
        with pytest.raises(ValueError):
            VersionInfo.from_str("3.2.")

    def test_non_numeric_part_raises_value_error(self):
        with pytest.raises(ValueError):
            VersionInfo.from_str("3.2.a")

    def test_returns_version_info_instance(self):
        assert isinstance(VersionInfo.from_str("1.0.0"), VersionInfo)


class TestVersionInfoToTuple:
    def test_to_tuple_round_trip(self):
        v = VersionInfo(4, 2, 0)
        assert v.to_tuple() == (4, 2, 0)

    def test_to_tuple_components_are_int(self):
        major, minor, patch = VersionInfo(1, 2, 3).to_tuple()
        assert isinstance(major, int)
        assert isinstance(minor, int)
        assert isinstance(patch, int)


class TestVersionInfoDunder:
    def test_str(self):
        assert str(VersionInfo(3, 5, 1)) == "3.5.1"

    def test_str_zero(self):
        assert str(VersionInfo(0, 0, 0)) == "0.0.0"

    def test_repr(self):
        assert repr(VersionInfo(3, 5, 1)) == "VersionInfo(major=3, minor=5, patch=1)"

    def test_hash_equal_instances(self):
        assert hash(VersionInfo(1, 2, 3)) == hash(VersionInfo(1, 2, 3))

    def test_hash_unequal_instances_differ(self):
        assert hash(VersionInfo(1, 2, 3)) != hash(VersionInfo(1, 2, 4))

    def test_usable_in_set(self):
        versions = {VersionInfo(1, 0, 0), VersionInfo(1, 0, 0), VersionInfo(2, 0, 0)}
        assert len(versions) == 2

    def test_usable_as_dict_key(self):
        mapping = {VersionInfo(1, 0, 0): "one", VersionInfo(2, 0, 0): "two"}
        assert mapping[VersionInfo(1, 0, 0)] == "one"


class TestVersionInfoEquality:
    def test_equal_when_all_components_match(self):
        assert VersionInfo(1, 2, 3) == VersionInfo(1, 2, 3)

    def test_not_equal_when_major_differs(self):
        assert VersionInfo(1, 2, 3) != VersionInfo(2, 2, 3)

    def test_not_equal_when_minor_differs(self):
        assert VersionInfo(1, 2, 3) != VersionInfo(1, 3, 3)

    def test_not_equal_when_patch_differs(self):
        assert VersionInfo(1, 2, 3) != VersionInfo(1, 2, 4)

    def test_inequality_operator_is_inverse_of_equality(self):
        a, b = VersionInfo(1, 2, 3), VersionInfo(1, 2, 4)
        assert (a == b) is False
        assert (a != b) is True

    def test_not_equal_to_non_version_info(self):
        assert VersionInfo(1, 0, 0) != "1.0.0"
        assert VersionInfo(1, 0, 0) != (1, 0, 0)
        assert VersionInfo(1, 0, 0) != 1
        assert VersionInfo(1, 0, 0) != None  # noqa: E711


class TestVersionInfoOrdering:
    def test_less_than_by_major(self):
        assert VersionInfo(1, 9, 9) < VersionInfo(2, 0, 0)

    def test_less_than_by_minor(self):
        assert VersionInfo(1, 2, 9) < VersionInfo(1, 3, 0)

    def test_less_than_by_patch(self):
        assert VersionInfo(1, 2, 3) < VersionInfo(1, 2, 4)

    def test_less_than_or_equal_when_equal(self):
        assert VersionInfo(1, 2, 3) <= VersionInfo(1, 2, 3)

    def test_less_than_or_equal_when_less(self):
        assert VersionInfo(1, 2, 3) <= VersionInfo(1, 2, 4)

    def test_greater_than_by_major(self):
        assert VersionInfo(2, 0, 0) > VersionInfo(1, 9, 9)

    def test_greater_than_by_minor(self):
        assert VersionInfo(1, 3, 0) > VersionInfo(1, 2, 9)

    def test_greater_than_by_patch(self):
        assert VersionInfo(1, 2, 4) > VersionInfo(1, 2, 3)

    def test_greater_than_or_equal_when_equal(self):
        assert VersionInfo(1, 2, 3) >= VersionInfo(1, 2, 3)

    def test_greater_than_or_equal_when_greater(self):
        assert VersionInfo(1, 2, 4) >= VersionInfo(1, 2, 3)

    def test_cross_type_ordering_raises_type_error(self):
        # Python raises TypeError when neither operand knows how to order
        # itself against the other (``__lt__`` etc. both return NotImplemented).
        with pytest.raises(TypeError):
            VersionInfo(1, 0, 0) < "1.0.0"  # type: ignore[operator]
        with pytest.raises(TypeError):
            VersionInfo(1, 0, 0) <= "1.0.0"  # type: ignore[operator]
        with pytest.raises(TypeError):
            VersionInfo(1, 0, 0) > "1.0.0"  # type: ignore[operator]
        with pytest.raises(TypeError):
            VersionInfo(1, 0, 0) >= "1.0.0"  # type: ignore[operator]


class TestVersionInfoSorting:
    def test_sort_orders_lexicographically(self):
        versions = [
            VersionInfo(1, 0, 0),
            VersionInfo(2, 0, 0),
            VersionInfo(1, 2, 0),
            VersionInfo(1, 1, 5),
            VersionInfo(1, 2, 3),
        ]
        assert sorted(versions) == [
            VersionInfo(1, 0, 0),
            VersionInfo(1, 1, 5),
            VersionInfo(1, 2, 0),
            VersionInfo(1, 2, 3),
            VersionInfo(2, 0, 0),
        ]

    def test_min_and_max(self):
        versions = [VersionInfo(2, 0, 0), VersionInfo(1, 0, 0), VersionInfo(3, 0, 0)]
        assert min(versions) == VersionInfo(1, 0, 0)
        assert max(versions) == VersionInfo(3, 0, 0)


class TestVersionInfoApi:
    def test_in_module_all(self):
        from _errortools import version as version_module

        assert "VersionInfo" in version_module.__all__
        assert "get_version_tuple" in version_module.__all__

    def test_in_public_package_all(self):
        import errortools

        assert "VersionInfo" in errortools.__all__
        assert "get_version_tuple" in errortools.__all__

    def test_importable_from_public_package(self):
        import errortools

        assert errortools.VersionInfo is VersionInfo
        assert errortools.get_version_tuple is get_version_tuple
