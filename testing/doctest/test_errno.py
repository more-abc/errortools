"""Doctests for :mod:`errortools.errno` (and ``_errortools.errno``).

These examples demonstrate and verify the behaviour of the
``errno``-introspection helpers exposed by :mod:`errortools`:

* :func:`errortools.get_errno_name`
* :func:`errortools.get_errno_message`
* :func:`errortools.get_all_errno_codes`
* :func:`errortools.is_valid_errno`

The doctests can be executed via::

    python -m doctest testing/doctest/test_errno.py -v

or simply by running :func:`testing.doctest.run_doctests`.


get_errno_name() - resolving codes to symbolic names
----------------------------------------------------

The most common errno codes map to well-known symbolic names::

    >>> import errno
    >>> from errortools import get_errno_name
    >>> get_errno_name(errno.ENOENT)
    'ENOENT'
    >>> get_errno_name(errno.EACCES)
    'EACCES'
    >>> get_errno_name(errno.EINVAL)
    'EINVAL'

Codes that are not part of the standard ``errno`` table return
``None`` instead of raising::

    >>> get_errno_name(9999) is None
    True

The special zero code is not a real errno, so it also returns ``None``::

    >>> get_errno_name(0) is None
    True


get_errno_message() - resolving codes to description strings
------------------------------------------------------------

A valid errno code resolves to a non-empty description string::

    >>> from errortools import get_errno_message
    >>> message = get_errno_message(errno.ENOENT)
    >>> isinstance(message, str) and len(message) > 0
    True
    >>> bool(message)
    True

An invalid errno code raises a ``ValueError``::

    >>> try:
    ...     get_errno_message(9999)
    ... except ValueError as exc:
    ...     "9999" in str(exc) or "Unknown" in str(exc)
    True


get_all_errno_codes() - bulk introspection
------------------------------------------

The function returns a ``dict`` mapping uppercase symbolic names to
their integer codes::

    >>> from errortools import get_all_errno_codes
    >>> codes = get_all_errno_codes()
    >>> isinstance(codes, dict)
    True
    >>> codes["ENOENT"] == errno.ENOENT
    True
    >>> codes["EACCES"] == errno.EACCES
    True

Every key is uppercase (matching the C convention) and every value is
an integer::

    >>> all(name.isupper() for name in codes)
    True
    >>> all(isinstance(value, int) for value in codes.values())
    True

The result is a *snapshot* - mutating it does not affect the standard
library's ``errno`` module::

    >>> snapshot = get_all_errno_codes()
    >>> _ = snapshot.pop("ENOENT", None)
    >>> "ENOENT" not in snapshot
    True
    >>> import errortools
    >>> errortools.is_valid_errno(errno.ENOENT)
    True


is_valid_errno() - membership check
-----------------------------------

The simplest way to ask "is this code known to the OS"::

    >>> from errortools import is_valid_errno
    >>> is_valid_errno(errno.ENOENT)
    True
    >>> is_valid_errno(errno.EACCES)
    True
    >>> is_valid_errno(9999)
    False
    >>> is_valid_errno(0)
    False


Top-level :mod:`errortools` package exposure
--------------------------------------------

The four helpers are re-exported from the top-level :mod:`errortools`
package::

    >>> import errortools
    >>> callable(errortools.get_errno_name)
    True
    >>> callable(errortools.get_errno_message)
    True
    >>> callable(errortools.get_all_errno_codes)
    True
    >>> callable(errortools.is_valid_errno)
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
