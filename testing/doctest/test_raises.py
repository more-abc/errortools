"""Doctests for :mod:`errortools.raises` (and ``_errortools.raises``).

These examples demonstrate and verify the behaviour of the exception
helpers exposed by :mod:`errortools`:

* :func:`errortools.raises`
* :func:`errortools.assert_raises`
* :func:`errortools.raises_all`   (Python 3.11+ only)
* :func:`errortools.reraise`

The doctests can be executed via::

    python -m doctest testing/doctest/test_raises.py -v

or simply by running :func:`testing.doctest.run_doctests`.


raises() - basic usage
----------------------

The simplest possible usage: one error type, one message::

    >>> from errortools import raises
    >>> raises([ValueError], ["bad value"])
    Traceback (most recent call last):
    ...
    ValueError: bad value

Multiple error types: the *first* error in the iterable is raised
together with the *first* message (Cartesian product, head element)::

    >>> raises([ValueError, TypeError], ["msg1", "msg2"])
    Traceback (most recent call last):
    ...
    ValueError: msg1

Empty inputs are valid no-ops - nothing is raised::

    >>> raises([], ["any message"]) is None
    True
    >>> raises([ValueError], []) is None
    True
    >>> raises([], []) is None
    True

The default *baseerror* is :class:`Exception`.  Passing a *baseerror*
that is not actually a base of every supplied error type raises
``TypeError``::

    >>> raises([ValueError], ["bad"], baseerror=LookupError)
    Traceback (most recent call last):
    ...
    TypeError: <class 'ValueError'> is not a subclass of LookupError

Custom exception subclasses work transparently.  The fully-qualified
class name in the traceback reflects the doctest module that hosts
the temporary class::

    >>> class MyDomainError(Exception):
    ...     pass
    >>> raises([MyDomainError], ["domain failure"])  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    test_raises.MyDomainError: domain failure

Only the *first* message is consumed when several are provided for a
single error type::

    >>> raises([ValueError], ["first", "second", "third"])
    Traceback (most recent call last):
    ...
    ValueError: first


assert_raises() - basic usage
-----------------------------

When the call *does* raise one of the expected types, the exception is
returned for further inspection::

    >>> from errortools import assert_raises
    >>> exc = assert_raises(int, [ValueError], "not-a-number")
    >>> isinstance(exc, ValueError)
    True
    >>> "invalid literal" in str(exc)
    True

Multiple expected types are accepted::

    >>> exc = assert_raises(lambda: 1 / 0, [ZeroDivisionError, ArithmeticError])
    >>> isinstance(exc, ZeroDivisionError)
    True

Forwarding ``*args`` and ``**kwargs`` works exactly like a normal call::

    >>> def _func(a, b, c=None):
    ...     if c is None:
    ...         raise RuntimeError("c is required")
    ...     return a + b + c
    >>> exc = assert_raises(_func, [RuntimeError], 1, 2)
    >>> isinstance(exc, RuntimeError)
    True
    >>> _func(1, 2, c=3)
    6

When the function raises the *wrong* type, an ``AssertionError`` is
raised.  The message contains both the actual and expected types::

    >>> try:
    ...     assert_raises(lambda: 1 / 0, [ValueError])
    ... except AssertionError as exc_info:
    ...     "ZeroDivisionError" in str(exc_info) and "ValueError" in str(exc_info)
    True

When the function does not raise at all, an ``AssertionError`` is
raised::

    >>> try:
    ...     assert_raises(lambda: 42, [ValueError])
    ... except AssertionError:
    ...     True
    True


reraise() - context manager
---------------------------

``reraise`` converts a caught exception into a different type while
chaining the original via ``__cause__``.  Note that ``KeyError``
renders its message with surrounding quotes (because
``str(KeyError(...))`` falls back to ``repr``), while exceptions such
as ``IndexError`` render the plain string::

    >>> from errortools import reraise
    >>> with reraise(KeyError, ValueError):
    ...     raise KeyError("missing key")
    Traceback (most recent call last):
    ...
    ValueError: 'missing key'

A tuple of source types is accepted::

    >>> with reraise((KeyError, IndexError), ValueError):
    ...     raise IndexError("oob")
    Traceback (most recent call last):
    ...
    ValueError: oob

Unrelated exceptions propagate unchanged::

    >>> with reraise(KeyError, ValueError):
    ...     raise RuntimeError("not converted")
    Traceback (most recent call last):
    ...
    RuntimeError: not converted

When no exception occurs inside the ``with`` block, the context manager
is a complete no-op::

    >>> value = 0
    >>> with reraise(KeyError, ValueError):
    ...     value = 21 * 2
    >>> value
    42


raises_all() - Python 3.11+ only
--------------------------------

``raises_all`` raises one :class:`ExceptionGroup` containing every
Cartesian product of errors and messages::

    >>> import sys
    >>> if sys.version_info >= (3, 11):
    ...     from errortools import raises_all
    ...     try:
    ...         raises_all([ValueError, TypeError], ["oops"])
    ...     except ExceptionGroup as eg:
    ...         len(eg.exceptions)
    ... else:
    ...     "skipped on Python < 3.11"
    2

The custom ``group_msg`` keyword is reflected in the resulting
``ExceptionGroup``::

    >>> if sys.version_info >= (3, 11):
    ...     from errortools import raises_all
    ...     try:
    ...         raises_all([ValueError], ["x"], group_msg="my errors")
    ...     except ExceptionGroup as eg:
    ...         eg.message
    ... else:
    ...     "skipped"
    'my errors'

Empty inputs produce no exception group at all::

    >>> if sys.version_info >= (3, 11):
    ...     from errortools import raises_all
    ...     result = raises_all([], ["x"])
    ...     result = raises_all([ValueError], [])
    ...     "ok"
    ... else:
    ...     "skipped"
    'ok'


Top-level :mod:`errortools` package exposure
--------------------------------------------

All four helpers are exported from the top-level package as callable
objects::

    >>> import errortools
    >>> callable(errortools.raises)
    True
    >>> callable(errortools.assert_raises)
    True
    >>> callable(errortools.reraise)
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
