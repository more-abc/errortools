"""Version information for the errortools package.

This module exposes the package version as a dotted-decimal string
(``__version__``), a comparable :class:`VersionInfo` value object
(``__version_info__``) and a ``(major, minor, patch)`` integer triple
(``__version_tuple__``), plus an optional git commit identifier
(``__commit_id__``).

The structured form is convenient for callers that want to compare
versions programmatically (``v < VersionInfo(4, 0, 0)``, etc.) and
mirrors the convention used by :data:`sys.version_info`.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import NotImplementedType
from typing import Final, Union

__all__ = [
    "VersionInfo",
    "get_version_tuple",
    "__version__",
    "__version_info__",
    "__version_tuple__",
    "__commit_id__",
    "version",
    "version_info",
    "version_tuple",
    "commit_id",
]


@dataclass
class VersionInfo:
    """A lightweight value object representing a dotted-decimal version.

    The three components follow the standard ``major.minor.patch``
    convention.  Instances are fully comparable and hashable, so they
    can be used as dictionary keys or stored in sets.

    Example:

        >>> v = VersionInfo(3, 5, 1)
        >>> str(v)
        '3.5.1'
        >>> v < VersionInfo(4, 0, 0)
        True

    .. versionadded:: 3.5
    """

    major: int
    minor: int
    patch: int

    __slots__ = ("major", "minor", "patch")

    @classmethod
    def from_str(cls, version_str: str) -> VersionInfo:
        """Create a :class:`VersionInfo` from a dotted-decimal string.

        Missing components default to ``0`` and components past the
        third are silently discarded.  A :class:`ValueError` is raised
        when the string is empty, ends with a trailing dot, or
        contains a non-numeric component.

        Example:

            >>> VersionInfo.from_str("3.5.1")
            VersionInfo(major=3, minor=5, patch=1)
            >>> VersionInfo.from_str("3.2")
            VersionInfo(major=3, minor=2, patch=0)

        .. versionadded:: 3.5
        """
        return cls(*get_version_tuple(version_str))

    def to_tuple(self) -> tuple[int, int, int]:
        """Return the version as an ``(major, minor, patch)`` tuple."""
        return (self.major, self.minor, self.patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(major={self.major}, minor={self.minor}, patch={self.patch})"

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other: object) -> Union[bool, NotImplementedType]:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result  # type: ignore[no-any-return]
        return not result

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return self.to_tuple() < other.to_tuple()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return self.to_tuple() <= other.to_tuple()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return self.to_tuple() > other.to_tuple()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return self.to_tuple() >= other.to_tuple()


def get_version_tuple(version: str) -> tuple[int, int, int]:
    """Parse a dotted-decimal version string into an integer triple.

    Examples:
        >>> get_version_tuple("3.5.1")
        (3, 5, 1)
        >>> get_version_tuple("3.2")
        (3, 2, 0)
        >>> get_version_tuple("3")
        (3, 0, 0)
        >>> get_version_tuple("1.2.3.4.5")
        (1, 2, 3)

    Args:
        version: A dotted-decimal version string such as ``"3.5.1"``.

    Returns:
        A ``(major, minor, patch)`` tuple.  Missing components default
        to ``0`` and components past the third are discarded.

    Raises:
        ValueError: If the string is empty, ends with a trailing dot,
            or contains a non-numeric component.

    .. versionchanged :: 3.5
        add it to the public API.
    """
    parts = version.split(".")
    if not parts or not parts[0]:
        raise ValueError(f"Invalid version string: {version!r}")

    try:
        nums = [int(p) for p in parts]
    except ValueError as exc:
        raise ValueError(f"Invalid version string: {version!r}") from exc

    major = nums[0]
    minor = nums[1] if len(nums) >= 2 else 0
    patch = nums[2] if len(nums) >= 3 else 0

    return (major, minor, patch)


# The structured form of the current release.  ``__version_info__`` is the
# canonical, comparable representation; ``__version_tuple__`` is a
# backwards-compatible plain-tuple alias derived from it via ``to_tuple()``.
__version__: Final[str] = "3.6.0"
__version_info__: Final[VersionInfo] = VersionInfo.from_str(__version__)
__version_tuple__: Final[tuple[int, int, int]] = __version_info__.to_tuple()
__commit_id__: Final[Union[str, None]] = None

# Convenient lower-case aliases mirroring the dunder names.  They point
# to the *same* objects so identity-based assertions (e.g. ``x is y``)
# continue to hold.
version: Final[str] = __version__
version_info: Final[VersionInfo] = __version_info__
version_tuple: Final[tuple[int, int, int]] = __version_tuple__
commit_id: Final[Union[str, None]] = __commit_id__


if __name__ == "__main__":
    print(f"errortools version: {__version__}")
    print(f"errortools version (info): {__version_info__}")
    print(f"errortools version (tuple): {__version_tuple__}")
    print(f"errortools commit id: {__commit_id__}")
