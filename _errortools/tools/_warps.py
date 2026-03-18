"""Internal wrappers for common iteration patterns."""

from itertools import product
from collections.abc import Iterable

__all__ = [
    "warp_list_product",
    "is_base_subclass",
]


def warp_list_product(
    errors: Iterable[type[Exception]],
    msgs: Iterable[str],
) -> list[tuple[type[Exception], str]]:
    """Return the Cartesian product of *errors* x *msgs* as a list of pairs.
    """
    return list(product(errors, msgs))


def is_base_subclass(
    *,
    error: type[Exception],
    baseerror: type[Exception] = Exception,
) -> bool:
    """Return whether *error* is a subclass of *baseerror*.
    """
    return issubclass(error, baseerror)
