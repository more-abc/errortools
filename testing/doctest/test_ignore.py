"""Doctests for :mod:`errortools.ignore` (and ``_errortools.ignore``).

These examples demonstrate and verify the behaviour of the
exception-suppression utilities exposed by :mod:`errortools`:

* :func:`errortools.ignore`           (full-featured, with metadata)
* :class:`errortools.fast_ignore`     (zero-overhead)
* :func:`errortools.ignore_subclass`  (matches a whole class hierarchy)
* :func:`errortools.ignore_warns`     (suppresses warnings)

The doctests can be executed via::

    python -m doctest testing/doctest/test_ignore.py -v

or simply by running :func:`testing.doctest.run_doctests`.


ignore() - basic usage
----------------------

The simplest form suppresses a single exception type::

    >>> from errortools import ignore
    >>> with ignore(KeyError):
    ...     {}["missing"]

Multiple types can be supplied positionally; the *first* matching
exception class is caught::

    >>> with ignore(KeyError, ValueError):
    ...     raise ValueError("suppressed")

Unrelated exceptions propagate unchanged::

    >>> with ignore(KeyError):
    ...     raise RuntimeError("not suppressed")
    Traceback (most recent call last):
    ...
    RuntimeError: not suppressed

Subclass instances are NOT suppressed when only the parent class is
listed - ``ignore`` uses exact-type matching::

    >>> with ignore(LookupError):
    ...     raise KeyError("subclass but not suppressed")
    Traceback (most recent call last):
    ...
    KeyError: 'subclass but not suppressed'


ignore() - captured metadata
---------------------------

When used in the form ``with ignore(...) as err:`` the captured
exception is exposed through an :class:`IgnoredError` instance.  After
the block executes, the object holds detailed metadata::

    >>> with ignore(NameError) as err:
    ...     raise NameError("undefined variable")
    >>> err.name
    'NameError'
    >>> err.be_ignore
    True
    >>> err.count
    1
    >>> isinstance(err.exception, NameError)
    True
    >>> err.traceback is None or "NameError" in err.traceback
    True

When no exception was raised inside the block, the captured object is
reset to its default values::

    >>> with ignore(ValueError) as err:
    ...     pass
    >>> err.be_ignore
    False
    >>> err.name is None
    True
    >>> err.count
    0
    >>> err.exception is None
    True


ignore() - as a decorator
-------------------------

``ignore`` may also wrap a function so every call is automatically
protected::

    >>> @ignore(ZeroDivisionError)
    ... def safe_divide(a, b):
    ...     return a / b
    >>> safe_divide(1, 0)  # returns None instead of raising
    >>> safe_divide(6, 2)
    3.0

The decorator can be combined with the context manager form so that
metadata from the most recent invocation is still available::

    >>> ig = ignore(ValueError)
    >>> @ig
    ... def may_fail():
    ...     raise ValueError("decorator test")
    >>> with ig as err:
    ...     may_fail()
    >>> err.name
    'ValueError'
    >>> err.be_ignore
    True


fast_ignore - high-performance suppression
-------------------------------------------

``fast_ignore`` provides a stripped-down context manager without any
metadata collection.  It catches the exact same exception types as
``ignore``.  The class lives in ``_errortools.ignore`` and is
re-exported (with a deprecation warning) via ``errortools``::

    >>> from _errortools.ignore import fast_ignore
    >>> with fast_ignore(KeyError):
    ...     {}["missing"]


ignore_subclass() - matches whole class hierarchies
---------------------------------------------------

``ignore_subclass`` is more permissive than ``ignore``: it suppresses
*any* exception whose type is a subclass of the supplied base (the
base itself included)::

    >>> from errortools import ignore_subclass
    >>> with ignore_subclass(LookupError):
    ...     raise IndexError("subclass of LookupError")  # suppressed

The base class itself is matched as well::

    >>> with ignore_subclass(KeyError):
    ...     raise KeyError("exact match")

Unrelated exceptions propagate unchanged::

    >>> with ignore_subclass(LookupError):
    ...     raise RuntimeError("unrelated")
    Traceback (most recent call last):
    ...
    RuntimeError: unrelated

Even deep hierarchies are supported, including :class:`BaseException`::

    >>> with ignore_subclass(BaseException):
    ...     raise KeyboardInterrupt()  # suppressed


ignore_warns() - suppressing warnings
-------------------------------------

``ignore_warns`` silences :mod:`warnings` of the supplied categories
for the duration of the block::

    >>> import warnings
    >>> from errortools import ignore_warns
    >>> with ignore_warns(DeprecationWarning):
    ...     warnings.warn("old api", DeprecationWarning, stacklevel=1)

Multiple categories can be listed::

    >>> with ignore_warns(DeprecationWarning, UserWarning):
    ...     warnings.warn("user", UserWarning, stacklevel=1)
    ...     warnings.warn("dep", DeprecationWarning, stacklevel=1)

Calling ``ignore_warns`` with no arguments silences *all* warnings
emitted inside the block::

    >>> with warnings.catch_warnings(record=True) as caught:
    ...     warnings.simplefilter("always")
    ...     with ignore_warns():
    ...         warnings.warn("any", UserWarning, stacklevel=1)
    ...     len(caught)
    0

Warnings outside the listed categories are unaffected.  The example
below records every emitted warning and checks that the
``UserWarning`` is *still* present after the ``ignore_warns`` block::

    >>> with warnings.catch_warnings(record=True) as caught:
    ...     warnings.resetwarnings()
    ...     warnings.simplefilter("always")
    ...     with ignore_warns(DeprecationWarning):
    ...         warnings.warn("user warning", UserWarning, stacklevel=1)
    ...     any(issubclass(w.category, UserWarning) for w in caught)
    True


Top-level :mod:`errortools` package exposure
--------------------------------------------

All four helpers are exported from the top-level package::

    >>> import errortools
    >>> callable(errortools.ignore)
    True
    >>> "fast_ignore" in errortools.__all__
    True
    >>> callable(errortools.ignore_subclass)
    True
    >>> callable(errortools.ignore_warns)
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
