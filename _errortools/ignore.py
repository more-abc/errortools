"""Utilities for silently suppressing exceptions and warnings."""

from __future__ import annotations

from collections.abc import Iterator, Callable
from contextlib import contextmanager
from typing import Any, TypeVar
import warnings

from .wrappers.ignore import ErrorIgnoreWrapper
from .decorator.timeout import timeout
from .decorator.retry import retry

__all__ = [
    "ignore",
    "fast_ignore",
    "ignore_subclass",
    "ignore_warns",
    "timeout",
    "retry",
]

Func = TypeVar("Func", bound=Callable[..., Any])
ExceptionType = type[BaseException]
ExceptionTypes = tuple[ExceptionType, ...]

ignore = ErrorIgnoreWrapper
"""Context manager that suppresses specified exceptions and captures metadata.

    Catches and suppresses the given exception types within a ``with`` block,
    while recording detailed information about any suppressed exception.

    Args:
        *excs: One or more exception types to suppress.

    Returns:
        An ``IgnoredError`` instance (via ``as``) that provides access to
        exception metadata after the block executes.

    Attributes on the returned ``IgnoredError``:
        be_ignore (bool):
            ``True`` if an exception was suppressed during the block,
            ``False`` otherwise.

        name (str | None):
            The class name of the suppressed exception
            (e.g. ``'KeyError'``, ``'ValueError'``).
            ``None`` if no exception occurred.

        count (int):
            Number of exceptions suppressed in this context block.
            Typically 1 unless the context manager is reused.

        exception (Exception | None):
            The original exception instance that was caught and suppressed.
            ``None`` if no exception occurred.

        traceback (str | None):
            Formatted traceback string showing where the suppressed exception
            occurred.  Useful for debugging.  ``None`` if no exception occurred.

    Examples:

        >>> with ignore(KeyError, ValueError) as err:
        ...     data = {}["missing_key"]
        ...
        >>> print(err.be_ignore)    # True
        >>> print(err.name)          # 'KeyError'
        >>> print(err.count)         # 1
        >>> print(err.exception)     # KeyError('missing_key')
        >>> print(err.traceback)     # Formatted traceback string

    Note:
        Use  `fast_ignore` or  `super_fast_ignore`(in `future` submodule) for zero-overhead
        suppression when metadata collection is not needed.

    See Also:
        -  `fast_ignore` — minimal overhead, no metadata
        -  `ignore_subclass` — suppress exceptions including subclasses
        -  `retry` — automatic retry on exception
    """
# NOTE: Any exception raised inside the ``with`` block that is an instance of one
# of *errors* is caught and discarded.  All other exceptions propagate
# unchanged.  Execution resumes after the ``with`` block.


class fast_ignore:
    """
    Ultra-lightweight context manager to suppress exceptions.

    A high-performance alternative to ``ignore`` without traceback collection.
    Only catches and ignores specified exceptions.

    Args:
        *excs: One or more exception types to suppress.

    Examples:
        >>> with fast_ignore(KeyError):
        ...     d = {}
        ...     _ = d["missing"]

    .. deprecated:: 3.0.0
        This class is deprecated as it is functionally redundant.
    """

    __slots__ = ("_excs",)

    def __init__(self, *excs: ExceptionType) -> None:
        warnings.warn(
            "fast_ignore is deprecated as it is functionally redundant.",
            DeprecationWarning,
            stacklevel=2,
        )
        for exc in excs:
            if not isinstance(exc, type) or not issubclass(exc, BaseException):
                raise TypeError(f"Expected Exception subclass, got {exc!r}")
        self._excs = excs

    def __enter__(self) -> None:
        return

    def __exit__(self, typ: ExceptionType | None, _, __) -> bool:
        if typ is None:
            return False
        return typ in self._excs


@contextmanager
def ignore_subclass(base: ExceptionType) -> Iterator[None]:
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
