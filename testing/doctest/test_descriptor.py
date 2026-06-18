"""Doctests for the descriptor modules re-exported from :mod:`errortools`.

These examples demonstrate and verify the behaviour of the
descriptor classes shipped with :mod:`errortools`:

* :class:`errortools.ErrorMsg`        (read-only message)
* :class:`errortools.NonBlankErrorMsg` (validated, non-blank string)

The doctests can be executed via::

    python -m doctest testing/doctest/test_descriptor.py -v

or simply by running :func:`testing.doctest.run_doctests`.


ErrorMsg - read-only attribute with a fixed message
---------------------------------------------------

``ErrorMsg`` returns the configured message on every attribute
access.  Any attempt to modify the attribute raises an
``AttributeError``::

    >>> from errortools import ErrorMsg
    >>> class Status:
    ...     message = ErrorMsg("Read-only message")
    >>> Status.message
    'Read-only message'
    >>> Status().message
    'Read-only message'

The class-level and instance-level access both return the same
message::

    >>> class Info:
    ...     info = ErrorMsg("Information only")
    ...     warning = ErrorMsg("Warning only")
    >>> obj = Info()
    >>> obj.info
    'Information only'
    >>> obj.warning
    'Warning only'

Mutating the attribute raises ``AttributeError`` with the
"Modification of this attribute is not allowed!" message::

    >>> class Locked:
    ...     attr = ErrorMsg("locked")
    >>> try:
    ...     Locked().attr = "new value"
    ... except AttributeError as exc:
    ...     "Modification" in str(exc)
    True

Deleting the attribute is likewise rejected::

    >>> try:
    ...     del Locked().attr
    ... except AttributeError as exc:
    ...     "Deletion" in str(exc)
    True


NonBlankErrorMsg - validated, non-blank string attribute
--------------------------------------------------------

``NonBlankErrorMsg`` accepts arbitrary strings but rejects blank
ones after stripping whitespace.  Values are stored trimmed::

    >>> from errortools import NonBlankErrorMsg
    >>> class ApiError:
    ...     message = NonBlankErrorMsg("Error message")
    ...     def __init__(self, msg):
    ...         self.message = msg
    >>> err = ApiError("  Invalid token  ")
    >>> err.message
    'Invalid token'

Empty strings are rejected with a ``ValueError``::

    >>> try:
    ...     ApiError("")
    ... except ValueError as exc:
    ...     "blank" in str(exc).lower()
    True

Whitespace-only strings are likewise rejected (the validator strips
before checking)::

    >>> try:
    ...     ApiError("   \\t\\n  ")
    ... except ValueError as exc:
    ...     "blank" in str(exc).lower()
    True

Non-string values raise a ``ValueError`` mentioning the required
type::

    >>> try:
    ...     ApiError(123)  # type: ignore[arg-type]
    ... except ValueError as exc:
    ...     "string" in str(exc).lower()
    True

Deleting the attribute is rejected with ``AttributeError``::

    >>> try:
    ...     err = ApiError("hello")
    ...     del err.message
    ... except AttributeError as exc:
    ...     "Deletion" in str(exc)
    True


Top-level :mod:`errortools` package exposure
--------------------------------------------

Both descriptors are re-exported from the top-level package::

    >>> import errortools
    >>> errortools.ErrorMsg is ErrorMsg
    True
    >>> errortools.NonBlankErrorMsg is NonBlankErrorMsg
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
