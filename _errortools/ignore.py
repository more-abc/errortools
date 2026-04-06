"""Utilities for silently suppressing exceptions and warnings."""

from __future__ import annotations

from collections.abc import Iterator, Callable
from contextlib import contextmanager
from functools import wraps
import asyncio
import inspect
import time
import warnings

from .wrappers.ignore import ErrorIgnoreWrapper

__all__ = [
    "ignore",
    "fast_ignore",
    "ignore_subclass",
    "ignore_warns",
    "timeout",
    "retry",
]


# A Context Manager? Maybe it is...

# NOTE: Any exception raised inside the ``with`` block that is an instance of one
# of *errors* is caught and discarded.  All other exceptions propagate
# unchanged.  Execution resumes after the ``with`` block.

# Performance Note:
# The ``ignore`` context manager is intentionally designed for debugging, not for raw speed.
# It captures the full exception traceback and metadata, which results in higher overhead.
# Use it for error handling and diagnostics, not for tight loops.
ignore = ErrorIgnoreWrapper
"""Context manager that silently suppresses the given exception types.

    It captures the full exception traceback and metadata, which results in higher overhead.
    Use it for error handling and diagnostics, not for tight loops. (Use `fast_ignore` faster)

    Args:
        *excs: One or more exception types to suppress.

    Example:
        >>> with ignore(KeyError) as error:
        ...     d = {}
        ...     _ = d["missing"]
        >>> print(error.be_ignore)  # True
"""


class fast_ignore:
    """
    Ultra-lightweight context manager to suppress exceptions.

    A high-performance alternative to ``ignore`` without traceback collection.
    Only catches and ignores specified exceptions.

    Args:
        *excs: One or more exception types to suppress.

    Example:
        >>> with fast_ignore(KeyError):
        ...     d = {}
        ...     _ = d["missing"]
    """

    __slots__ = ("_excs",)

    def __init__(self, *excs: type[BaseException]) -> None:
        for exc in excs:
            if not isinstance(exc, type) or not issubclass(exc, BaseException):
                raise TypeError(f"Expected Exception subclass, got {exc!r}")
        self._excs = excs

    def __enter__(self) -> None:
        return

    def __exit__(self, typ: type[BaseException] | None, _, __) -> bool:
        if typ is None:
            return False
        return typ in self._excs


@contextmanager
def ignore_subclass(base: type[BaseException]) -> Iterator[None]:
    """Context manager that suppresses any exception whose type is a subclass of *base*.

    Args:
        base: The base exception class.  Any raised exception whose type is a
            subclass of *base* (including *base* itself) is suppressed.

    Example:
        >>> with ignore_subclass(LookupError):
        ...     raise IndexError("out of range")  # IndexError ⊆ LookupError
        ... # suppressed — execution continues here
    """
    # NOTE: Similar to `ignore`, but accepts a single base class and suppresses
    # every exception whose type satisfies ``issubclass(type(exc), base)``.
    # Useful when you want to express intent explicitly — "ignore anything
    # derived from X" — rather than listing concrete types.
    try:
        yield
    except BaseException as exc:
        if not issubclass(type(exc), base):
            raise


@contextmanager
def ignore_warns(*categories: type[Warning]) -> Iterator[None]:
    """Context manager that suppresses the given warning categories.

    Args:
        *categories: One or more `Warning` subclasses to suppress.
            Passing no arguments suppresses all warnings.

    Example:
        >>> with ignore_warns(DeprecationWarning):
        ...     warnings.warn("old api", DeprecationWarning)
        ... # no warning emitted
    """
    # NOTE: Uses `warnings.catch_warnings` and `warnings.simplefilter`
    # to silence any warning whose category is one of *categories* for the
    # duration of the ``with`` block.  All other warnings are unaffected.
    with warnings.catch_warnings():
        for category in categories:
            warnings.filterwarnings("ignore", category=category)
        if not categories:
            warnings.simplefilter("ignore")
        yield


def timeout(seconds: float) -> Callable:
    """Decorator that raises `asyncio.TimeoutError` if the async function exceeds *seconds*.

    Args:
        seconds: Maximum allowed execution time in seconds.

    Raises:
        ValueError: If the decorated function is not a coroutine function.
        asyncio.TimeoutError: If the function does not complete within *seconds*.

    Example:

        >>> @timeout(5.0)
        ... async def fetch(url: str) -> str:
        ...     ...
    """

    def decorator(func: Callable) -> Callable:
        if not inspect.iscoroutinefunction(func):
            raise ValueError("timeout only supports async functions")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)

        return wrapper

    return decorator


# NOTE: Exceptions thrown inside the body of a Python `for`
# loop are not propagated back to the iterator. As a result,
# the pattern `for _ in retry(): ...` cannot be implemented
# in Python. Therefore, `retry` is designed as a pure decorator.
class retry:
    """Decorator that retries a callable when specified exceptions are raised.

    Supports both **sync** and **async** functions.

    Args:
        times: Maximum number of *retries* (total attempts = times + 1).
        on: Exception type (or tuple of types) that triggers a retry.
            Any other exception propagates immediately.
        delay: Seconds to wait between retries.  Defaults to ``0`` (no wait).

    Raises:
        ValueError: If *times* is negative.
        TypeError: If any type in *on* is not an ``Exception`` subclass.
        The last exception: Re-raised when all retry attempts are exhausted.

    Example:
        >>> @retry(times=2, on=ValueError)
        ... def unstable():
        ...     raise ValueError("oops")
        >>> unstable()
        Traceback (most recent call last):
            ...
        ValueError: oops
    """

    def __init__(
        self,
        times: int,
        on: type[Exception] | tuple[type[Exception], ...] = Exception,
        delay: float = 0,
    ) -> None:
        if times < 0:
            raise ValueError(f"times must be a non-negative integer, got {times!r}")

        exc_types = on if isinstance(on, tuple) else (on,)
        for t in exc_types:
            if not isinstance(t, type) or not issubclass(t, Exception):
                raise TypeError(f"Expected Exception subclass, got {t!r}")

        self._times = times
        self._on = exc_types
        self._delay = delay

    # ------------------------------------------------------------------
    # Decorator protocol
    # ------------------------------------------------------------------

    def __call__(self, func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exc: Exception | None = None
                for attempt in range(self._times + 1):
                    try:
                        return await func(*args, **kwargs)
                    except self._on as exc:
                        last_exc = exc
                        if attempt < self._times and self._delay:
                            await asyncio.sleep(self._delay)
                raise last_exc

            return async_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(self._times + 1):
                try:
                    return func(*args, **kwargs)
                except self._on as exc:
                    last_exc = exc
                    if attempt < self._times and self._delay:
                        time.sleep(self._delay)
            raise last_exc

        return wrapper
