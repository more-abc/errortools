"""Doctests for :mod:`_errortools.version` (and its public re-exports).

These examples demonstrate and verify the behaviour of the public
version helpers exposed by :mod:`errortools`:

* :class:`errortools.VersionInfo`  - comparable / hashable version triple
* :func:`errortools.get_version_tuple` - parse a dotted-decimal string

The doctests can be executed via::

    python -m doctest testing/doctest/test_version.py -v

or simply by running :func:`testing.doctest.run_doctests`.


VersionInfo - construction
--------------------------

:class:`VersionInfo` is a thin dataclass holding three integer
components.  The components are exposed as plain attributes::

    >>> from errortools import VersionInfo
    >>> v = VersionInfo(3, 5, 1)
    >>> v.major
    3
    >>> v.minor
    5
    >>> v.patch
    1

Instances support both ``str()`` and ``repr()``::

    >>> str(VersionInfo(3, 5, 1))
    '3.5.1'
    >>> repr(VersionInfo(3, 5, 1))
    'VersionInfo(major=3, minor=5, patch=1)'


VersionInfo - from_str
----------------------

The :meth:`VersionInfo.from_str` classmethod parses a dotted-decimal
string and silently fills missing components with ``0``::

    >>> from errortools import VersionInfo
    >>> VersionInfo.from_str("3.5.1")
    VersionInfo(major=3, minor=5, patch=1)
    >>> VersionInfo.from_str("3.2")
    VersionInfo(major=3, minor=2, patch=0)
    >>> VersionInfo.from_str("3")
    VersionInfo(major=3, minor=0, patch=0)

Components beyond the third are discarded::

    >>> VersionInfo.from_str("1.2.3.4.5")
    VersionInfo(major=1, minor=2, patch=3)

A :class:`ValueError` is raised for empty strings, trailing dots, or
non-numeric components::

    >>> VersionInfo.from_str("")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: ''
    >>> VersionInfo.from_str("3.2.")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: '3.2.'
    >>> VersionInfo.from_str("3.2.a")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: '3.2.a'


VersionInfo - to_tuple
----------------------

:meth:`VersionInfo.to_tuple` returns the components as a plain
``(major, minor, patch)`` integer triple::

    >>> from errortools import VersionInfo
    >>> VersionInfo(3, 5, 1).to_tuple()
    (3, 5, 1)
    >>> tuple(VersionInfo(0, 0, 0).to_tuple())
    (0, 0, 0)


VersionInfo - equality and hashing
----------------------------------

Two :class:`VersionInfo` objects are equal iff their three components
are equal.  Instances are hashable, so they can be used as dictionary
keys or stored in sets::

    >>> from errortools import VersionInfo
    >>> VersionInfo(3, 5, 1) == VersionInfo(3, 5, 1)
    True
    >>> VersionInfo(3, 5, 1) != VersionInfo(3, 5, 2)
    True
    >>> hash(VersionInfo(3, 5, 1)) == hash(VersionInfo(3, 5, 1))
    True
    >>> {VersionInfo(1, 0, 0), VersionInfo(1, 0, 0), VersionInfo(2, 0, 0)} == {
    ...     VersionInfo(1, 0, 0), VersionInfo(2, 0, 0)
    ... }
    True
    >>> mapping = {VersionInfo(1, 0, 0): "v1", VersionInfo(2, 0, 0): "v2"}
    >>> mapping[VersionInfo(2, 0, 0)]
    'v2'

Equality against unrelated types returns ``False`` (the standard
``__eq__`` ``NotImplemented`` fallback)::

    >>> VersionInfo(1, 0, 0) == "1.0.0"
    False
    >>> VersionInfo(1, 0, 0) == (1, 0, 0)
    False


VersionInfo - ordering
----------------------

Instances are totally ordered component-wise, the same way Python
compares integer triples::

    >>> from errortools import VersionInfo
    >>> VersionInfo(1, 9, 9) < VersionInfo(2, 0, 0)
    True
    >>> VersionInfo(1, 2, 3) < VersionInfo(1, 2, 4)
    True
    >>> VersionInfo(1, 2, 3) <= VersionInfo(1, 2, 3)
    True
    >>> VersionInfo(2, 0, 0) > VersionInfo(1, 9, 9)
    True
    >>> VersionInfo(1, 2, 4) >= VersionInfo(1, 2, 4)
    True

Ordering works inside the standard library / ``sorted`` / ``min`` /
``max`` helpers::

    >>> sorted([
    ...     VersionInfo(2, 0, 0),
    ...     VersionInfo(1, 1, 5),
    ...     VersionInfo(1, 2, 0),
    ...     VersionInfo(1, 2, 3),
    ... ])
    [VersionInfo(major=1, minor=1, patch=5), VersionInfo(major=1, minor=2, patch=0), VersionInfo(major=1, minor=2, patch=3), VersionInfo(major=2, minor=0, patch=0)]
    >>> min(VersionInfo(1, 0, 0), VersionInfo(2, 0, 0), VersionInfo(1, 5, 0))
    VersionInfo(major=1, minor=0, patch=0)
    >>> max(VersionInfo(1, 0, 0), VersionInfo(2, 0, 0), VersionInfo(1, 5, 0))
    VersionInfo(major=2, minor=0, patch=0)


get_version_tuple - happy-path parsing
--------------------------------------

:func:`get_version_tuple` parses a dotted-decimal string into a
``(major, minor, patch)`` integer triple.  Missing components default
to ``0`` and components past the third are discarded::

    >>> from errortools import get_version_tuple
    >>> get_version_tuple("3.5.1")
    (3, 5, 1)
    >>> get_version_tuple("3.2")
    (3, 2, 0)
    >>> get_version_tuple("3")
    (3, 0, 0)
    >>> get_version_tuple("1.2.3.4.5")
    (1, 2, 3)
    >>> get_version_tuple("0.0.0")
    (0, 0, 0)

The returned tuple components are real ``int`` objects::

    >>> result = get_version_tuple("1.2.3")
    >>> all(isinstance(x, int) for x in result)
    True


get_version_tuple - error handling
----------------------------------

An empty string, a trailing dot, or any non-numeric component triggers
a :class:`ValueError` whose message identifies the offending input::

    >>> get_version_tuple("")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: ''
    >>> get_version_tuple("3.2.")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: '3.2.'
    >>> get_version_tuple("3.2.a")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: '3.2.a'
    >>> get_version_tuple("a.b.c")
    Traceback (most recent call last):
    ...
    ValueError: Invalid version string: 'a.b.c'


Consistency between VersionInfo and get_version_tuple
-----------------------------------------------------

:meth:`VersionInfo.from_str` delegates to :func:`get_version_tuple`, so
the two functions agree on every input::

    >>> from errortools import VersionInfo, get_version_tuple
    >>> for text in ("3.5.1", "3.2", "3", "1.2.3.4.5", "0.0.0"):
    ...     VersionInfo.from_str(text).to_tuple() == get_version_tuple(text)
    True
    True
    True
    True
    True


Top-level :mod:`errortools` package exposure
--------------------------------------------

:class:`VersionInfo` and :func:`get_version_tuple` are re-exported from
the top-level :mod:`errortools` package and listed in its ``__all__``::

    >>> import errortools
    >>> "VersionInfo" in errortools.__all__
    True
    >>> "get_version_tuple" in errortools.__all__
    True
    >>> errortools.VersionInfo is __import__("_errortools.version", fromlist=["VersionInfo"]).VersionInfo
    True
    >>> errortools.get_version_tuple is __import__("_errortools.version", fromlist=["get_version_tuple"]).get_version_tuple
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
