"""Doctests for the decorator modules re-exported from :mod:`errortools`.

These examples demonstrate and verify the behaviour of the
decorators shipped with :mod:`errortools`:

* :func:`errortools.deprecated`
* :func:`errortools.experimental`
* :func:`errortools.error_cache`
* :func:`errortools.suppress`
* :func:`errortools.convert`
* :func:`errortools.timeout`
* :func:`errortools.retry`

The doctests can be executed via::

    python -m doctest testing/doctest/test_decorator.py -v

or simply by running :func:`testing.doctest.run_doctests`.


deprecated() - emit a DeprecationWarning
----------------------------------------

``deprecated`` wraps a callable so that calling it emits a
``DeprecationWarning`` mentioning the version and reason::

    >>> import warnings
    >>> from errortools import deprecated
    >>> @deprecated(version="2.0", reason="Use new_func instead.")
    ... def old_func(x):
    ...     return x * 2
    >>> with warnings.catch_warnings(record=True) as caught:
    ...     warnings.simplefilter("always")
    ...     result = old_func(21)
    ...     len(caught)
    ...     "deprecated" in str(caught[0].message).lower()
    1
    True
    >>> result
    42

The wrapper preserves the original function's metadata so introspection
still works::

    >>> old_func.__name__
    'old_func'
    >>> old_func.__wrapped__(3)
    6


experimental() - emit a FutureWarning
-------------------------------------

``experimental`` works just like ``deprecated`` but emits a
``FutureWarning`` instead::

    >>> from errortools import experimental
    >>> @experimental(reason="API may change without notice.")
    ... def new_feature(x):
    ...     return x
    >>> with warnings.catch_warnings(record=True) as caught:
    ...     warnings.simplefilter("always")
    ...     _ = new_feature(7)
    ...     len(caught)
    ...     caught[0].category.__name__
    1
    'FutureWarning'


error_cache - caching exceptions per call signature
---------------------------------------------------

``error_cache`` stores exceptions thrown by the wrapped function,
keyed by the call arguments.  A subsequent call with the same
arguments re-raises the cached exception without re-executing the
body::

    >>> from errortools import error_cache
    >>> counter = {"n": 0}
    >>> @error_cache
    ... def may_fail(x):
    ...     counter["n"] += 1
    ...     raise RuntimeError(f"failure #{counter['n']}")
    >>> try:
    ...     may_fail(1)
    ... except RuntimeError as exc:
    ...     "failure" in str(exc)
    True
    >>> try:
    ...     may_fail(1)
    ... except RuntimeError as exc:
    ...     "failure" in str(exc)
    True

The cache can also be inspected and cleared explicitly::

    >>> cached = may_fail.get_cached_error(1)
    >>> isinstance(cached, RuntimeError)
    True
    >>> may_fail.clear_cache()
    >>> may_fail.get_cached_error(1) is None
    True


suppress() - turn exceptions into a default value
-------------------------------------------------

``suppress`` is the decorator counterpart of :func:`errortools.ignore`::

    >>> from errortools import suppress
    >>> @suppress(ZeroDivisionError, default=0)
    ... def divide(a, b):
    ...     return a / b
    >>> divide(1, 0)
    0
    >>> divide(10, 2)
    5.0

The default fallback defaults to ``None`` when not specified::

    >>> @suppress(ValueError)
    ... def parse(text):
    ...     return int(text)
    >>> parse("not a number") is None
    True


convert() - turn one exception type into another
------------------------------------------------

``convert`` re-raises a configured target exception type, chaining the
original via ``__cause__``::

    >>> from errortools import convert
    >>> @convert(KeyError, ValueError)
    ... def lookup(d, key):
    ...     return d[key]
    >>> try:
    ...     lookup({}, "missing")
    ... except ValueError as exc:
    ...     isinstance(exc.__cause__, KeyError)
    True

A custom message can be provided through the ``message`` keyword::

    >>> @convert(KeyError, RuntimeError, message="custom message")
    ... def another_lookup(d, key):
    ...     return d[key]
    >>> try:
    ...     another_lookup({}, "x")
    ... except RuntimeError as exc:
    ...     str(exc)
    'custom message'


timeout() - async functions only
--------------------------------

``timeout`` wraps a coroutine function with
:func:`asyncio.wait_for` and rejects non-async callables::

    >>> from errortools import timeout
    >>> @timeout(1.0)
    ... async def fetch():
    ...     return 42
    >>> import asyncio
    >>> asyncio.run(fetch())
    42

Applying ``timeout`` to a plain (non-async) function is rejected with
a ``ValueError``::

    >>> try:
    ...     timeout(1.0)(lambda: None)
    ... except ValueError as exc:
    ...     "async" in str(exc).lower()
    True


retry() - retry on a specific exception type
-------------------------------------------

``retry`` re-invokes the decorated function a configured number of
times when the watched exception type is raised.  When all attempts
fail the last exception is re-raised::

    >>> import asyncio
    >>> from errortools import retry
    >>> state = {"n": 0}
    >>> @retry(times=3, on=ValueError)
    ... def flaky():
    ...     state["n"] += 1
    ...     if state["n"] < 3:
    ...         raise ValueError("transient")
    ...     return state["n"]
    >>> flaky()
    3

The decorator also works with async callables::

    >>> state = {"n": 0}
    >>> @retry(times=2, on=RuntimeError)
    ... async def async_flaky():
    ...     state["n"] += 1
    ...     if state["n"] < 2:
    ...         raise RuntimeError("transient")
    ...     return state["n"]
    >>> asyncio.run(async_flaky())
    2


Top-level :mod:`errortools` package exposure
--------------------------------------------

All decorators are re-exported from the top-level package::

    >>> import errortools
    >>> callable(errortools.deprecated)
    True
    >>> callable(errortools.experimental)
    True
    >>> callable(errortools.error_cache)
    True
    >>> callable(errortools.suppress)
    True
    >>> callable(errortools.convert)
    True
    >>> callable(errortools.timeout)
    True
    >>> callable(errortools.retry)
    True
"""

from __future__ import annotations

__all__ = ["__doc__"]
