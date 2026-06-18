"""Doctests for :mod:`errortools.classes.errorcodes` and
:mod:`errortools.classes.warn` (re-exported from the top-level
:mod:`errortools` package).

These examples demonstrate and verify the predefined exception and
warning classes exposed by :mod:`errortools`:

* :class:`errortools.PureBaseException`
* :class:`errortools.ContextException`
* :class:`errortools.BaseErrorCodes`
* :class:`errortools.InvalidInputError` / ``NotFoundError`` / ...
* :class:`errortools.GroupErrors`   (Python 3.11+ only)
* :class:`errortools.BaseWarning` and the predefined subclasses

The doctests can be executed via::

    python -m doctest testing/doctest/test_classes.py -v

or simply by running :func:`testing.doctest.run_doctests`.


PureBaseException - basic exception with error code
---------------------------------------------------

``PureBaseException`` provides an integer ``code`` and a fallback
``default_detail`` that are surfaced through ``__str__``::

    >>> from errortools import PureBaseException, InvalidInputError
    >>> err = InvalidInputError("age must be positive")
    >>> err.code
    1001
    >>> str(err)
    '[1001] age must be positive'
    >>> repr(err)  # doctest: +ELLIPSIS
    "InvalidInputError(detail='age must be positive', code=1001, trace_id='...')"

When no detail is provided, ``default_detail`` is used::

    >>> err = InvalidInputError()
    >>> err.detail
    'Invalid input.'
    >>> "Invalid input" in str(err)
    True


ContextException - trace_id, context, and chaining
---------------------------------------------------

``ContextException`` extends ``PureBaseException`` with a unique
``trace_id``, a ``context`` dict and an optional ``cause``::

    >>> from errortools import RuntimeFailure
    >>> err = RuntimeFailure("oops").with_context(user="alice", op="submit")
    >>> isinstance(err.trace_id, str) and len(err.trace_id) == 32
    True
    >>> all(c in "0123456789abcdef" for c in err.trace_id)
    True
    >>> err.context["user"]
    'alice'
    >>> err.context["op"]
    'submit'

Chaining a root cause works through :meth:`with_cause` (and the
native ``__cause__`` attribute)::

    >>> err = RuntimeFailure("wrapper").with_cause(ValueError("root"))
    >>> isinstance(err.cause, ValueError)
    True
    >>> err.__cause__ is err.cause
    True

The :attr:`chain` property walks the chain and produces a JSON-like
list of dicts::

    >>> chain = err.chain
    >>> chain[0]["type"]
    'RuntimeFailure'
    >>> chain[0]["trace_id"] == err.trace_id
    True
    >>> chain[1]["type"]
    'ValueError'


BaseErrorCodes - factory classmethods
-------------------------------------

``BaseErrorCodes`` exposes a small collection of ``classmethod``
factories that return the corresponding specialised exception::

    >>> from errortools import BaseErrorCodes
    >>> err = BaseErrorCodes.invalid_input("bad parameter")
    >>> isinstance(err, InvalidInputError)
    True
    >>> err.code
    1001

    >>> err = BaseErrorCodes.not_found("user 42 missing")
    >>> err.code
    3001

    >>> err = BaseErrorCodes.access_denied("forbidden")
    >>> err.code
    2001

    >>> err = BaseErrorCodes.configuration_error("missing setting")
    >>> err.code
    5001

    >>> err = BaseErrorCodes.runtime_failure("boom")
    >>> err.code
    4001

    >>> err = BaseErrorCodes.timeout_failure("too slow")
    >>> err.code
    4002

Calling a factory without a detail uses the default message of the
target class::

    >>> err = BaseErrorCodes.timeout_failure()
    >>> "timed out" in err.detail.lower()
    True


Predefined error subclasses
---------------------------

Each predefined error class has its own integer code and default
detail::

    >>> from errortools import (
    ...     InvalidInputError, NotFoundError, AccessDeniedError,
    ...     ConfigurationError, RuntimeFailure, TimeoutFailure,
    ... )
    >>> InvalidInputError.code
    1001
    >>> NotFoundError.code
    3001
    >>> AccessDeniedError.code
    2001
    >>> ConfigurationError.code
    5001
    >>> RuntimeFailure.code
    4001
    >>> TimeoutFailure.code
    4002

All of them inherit from ``ContextException`` (and therefore from
``PureBaseException``)::

    >>> issubclass(InvalidInputError, RuntimeFailure.__mro__[1])
    True
    >>> issubclass(TimeoutFailure, RuntimeFailure.__mro__[1])
    True


GroupErrors - collecting and raising an ExceptionGroup (3.11+)
-------------------------------------------------------------

On Python 3.11+, :class:`GroupErrors` collects exceptions and raises
them together inside an :class:`ExceptionGroup`::

    >>> import sys
    >>> if sys.version_info >= (3, 11):
    ...     from errortools import GroupErrors
    ...     g = GroupErrors("validation failed")
    ...     g.collect(TypeError("expected str"))
    ...     g.collect(ValueError("value out of range"))
    ...     len(g)
    ... else:
    ...     "skipped on Python < 3.11"
    2

The boolean conversion reflects whether the group has any errors::

    >>> if sys.version_info >= (3, 11):
    ...     from errortools import GroupErrors
    ...     empty = GroupErrors()
    ...     bool(empty)
    ... else:
    ...     False
    False

Calling :meth:`raise_group` raises the group as an
``ExceptionGroup``::

    >>> if sys.version_info >= (3, 11):
    ...     from errortools import GroupErrors
    ...     g = GroupErrors("validation failed")
    ...     g.collect(ValueError("bad value"))
    ...     try:
    ...         g.raise_group()
    ...     except ExceptionGroup as eg:
    ...         eg.message
    ... else:
    ...     "skipped"
    'validation failed'

Calling :meth:`clear` empties the group; subsequent
:meth:`raise_group` is a no-op::

    >>> if sys.version_info >= (3, 11):
    ...     from errortools import GroupErrors
    ...     g = GroupErrors()
    ...     g.collect(ValueError("x"))
    ...     g.clear()
    ...     len(g)
    ... else:
    ...     "skipped"
    0


BaseWarning - emitting warnings through the class hierarchy
-----------------------------------------------------------

:mod:`errortools` also provides a hierarchy of warning classes that
integrate with the standard :mod:`warnings` module::

    >>> from errortools import (
    ...     BaseWarning, DeprecatedWarning, PerformanceWarning,
    ...     ResourceUsageWarning, RuntimeBehaviourWarning,
    ...     ConfigurationWarning,
    ... )

All five predefined subclasses are real :class:`Warning` subclasses
with their own default detail::

    >>> all(issubclass(cls, BaseWarning) for cls in (
    ...     DeprecatedWarning, PerformanceWarning,
    ...     ResourceUsageWarning, RuntimeBehaviourWarning,
    ...     ConfigurationWarning,
    ... ))
    True
    >>> DeprecatedWarning.default_detail
    'This feature is deprecated.'
    >>> PerformanceWarning.default_detail
    'This operation may be slow.'

Each instance has a ``detail`` attribute and a helpful ``__repr__``::

    >>> w = PerformanceWarning("custom perf hint")
    >>> w.detail
    'custom perf hint'
    >>> repr(w)
    "PerformanceWarning(detail='custom perf hint')"


Top-level :mod:`errortools` package exposure
--------------------------------------------

The classes are all re-exported from the top-level package::

    >>> import errortools
    >>> errortools.PureBaseException is PureBaseException
    True
    >>> errortools.ContextException.__name__
    'ContextException'
    >>> errortools.BaseErrorCodes is BaseErrorCodes
    True
    >>> errortools.InvalidInputError is InvalidInputError
    True
    >>> errortools.BaseWarning is BaseWarning
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
