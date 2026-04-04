"""Utilities for silently suppressing exceptions and warnings."""

from collections.abc import Iterator
from contextlib import contextmanager
import warnings

from .wrappers.ignore import ErrorIgnoreWrapper

__all__ = [
    "ignore",
    "ignore_subclass",
    "ignore_warns",
]


# A Context Manager? Maybe it is...

# NOTE: Any exception raised inside the ``with`` block that is an instance of one
# of *errors* is caught and discarded.  All other exceptions propagate
# unchanged.  Execution resumes after the ``with`` block.
ignore = ErrorIgnoreWrapper
"""Context manager that silently suppresses the given exception types.

    Args:
        *excs: One or more exception types to suppress.

    Example:
        >>> with ignore(KeyError) as error:
        ...     d = {}
        ...     _ = d["missing"]
        ... print(error.be_ignore)  # True
"""


@contextmanager
def ignore_subclass(base: type[Exception]) -> Iterator[None]:
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
    except Exception as exc:
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
