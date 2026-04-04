"""Utilities for raising exceptions."""

from contextlib import contextmanager
from typing import Callable, Any
from collections.abc import Iterable, Iterator

from .tools._warps import _warp_list_product, is_base_subclass

__all__ = ["raises", "assert_raises", "raises_all", "reraise"]


def raises(
    errors: Iterable[type[Exception]],
    msgs: Iterable[str],
    baseerror: type[Exception] = Exception,
) -> None:
    """Validate exception types and raise the first (error, message) combination.

    Args:
        errors: An iterable of exception types to raise.
        msgs: An iterable of message strings to pair with each exception type.
        baseerror: The base exception class that every type in *errors* must
        inherit from. Defaults to `Exception`.

    Raises:
        TypeError: If any type in *errors* is not a subclass of *baseerror*.

    Example:
        >>> raises([ValueError], ["invalid input"])
        Traceback (most recent call last):
            ...
        ValueError: invalid input
    """
    # NOTE: Computes the Cartesian product of *errors* x *msgs*, validates that every
    # error type is a subclass of *baseerror*, then raises the first resulting
    # exception.  If the product is empty (either iterable is empty) the function
    # returns without raising.
    pairs = _warp_list_product(errors, msgs)
    if not pairs:
        return
    for error, _ in pairs:
        if not is_base_subclass(error=error, baseerror=baseerror):
            raise TypeError(f"{error!r} is not a subclass of {baseerror.__name__}")
    error, msg = pairs[0]
    raise error(msg)


def assert_raises(
    func: Callable[..., Any],
    errors: Iterable[type[Exception]],
    *args: Any,
    **kwargs: Any,
) -> Exception:
    """Call *func* and assert that it raises one of the expected exception types.

    Args:
        func: The callable to invoke.
        errors: An iterable of exception types that are considered acceptable.
        *args: Positional arguments forwarded to *func*.
        **kwargs: Keyword arguments forwarded to *func*.

    Returns:
        The caught exception instance, so callers can inspect its message or
        attributes.

    Raises:
        AssertionError: If *func* does not raise, or raises a type not listed
            in *errors*.

    Example:
        >>> exc = assert_raises(int, [ValueError], "not-a-number")
        >>> str(exc)
        "invalid literal for int() with base 10: 'not-a-number'"
    """
    # NOTE: Invokes ``func(*args, **kwargs)`` and checks that the exception raised is
    # an instance of at least one type in *errors*.  If no exception is raised,
    # or the wrong type is raised, an `AssertionError` is raised instead.
    expected = tuple(errors)
    try:
        func(*args, **kwargs)
    except Exception as exc:
        if not isinstance(exc, expected):
            raise AssertionError(
                f"{func!r} raised {type(exc)!r}, expected one of "
                f"{[e.__name__ for e in expected]}"
            ) from exc
        return exc
    raise AssertionError(
        f"{func!r} did not raise; expected one of " f"{[e.__name__ for e in expected]}"
    )


def raises_all(
    errors: Iterable[type[Exception]],
    msgs: Iterable[str],
    baseerror: type[Exception] = Exception,
    group_msg: str = "multiple errors",
) -> None:
    """Validate exception types and raise all (error, message) combinations as an ExceptionGroup.

    Args:
        errors: An iterable of exception types to include in the group.
        msgs: An iterable of message strings to pair with each exception type.
        baseerror: The base exception class that every type in *errors* must
            inherit from.  Defaults to `Exception`.
        group_msg: The message attached to the `ExceptionGroup` itself.
            Defaults to ``"multiple errors"``.

    Raises:
        TypeError: If any type in *errors* is not a subclass of *baseerror*.
        ExceptionGroup: Containing one ``errors[i](msgs[j])`` instance for
            every ``(i, j)`` pair in the Cartesian product.

    Example:
        >>> raises_all([ValueError, TypeError], ["bad input"])
        Traceback (most recent call last):
            ...
        ExceptionGroup: multiple errors (2 sub-exceptions)
    """
    # NOTE: Computes the Cartesian product of *errors* x *msgs*, validates that every
    # error type is a subclass of *baseerror*, then raises a single
    # `ExceptionGroup` containing one instantiated exception per pair.
    # If the product is empty (either iterable is empty) the function returns
    # without raising.
    pairs = _warp_list_product(errors, msgs)
    if not pairs:
        return
    for error, _ in pairs:
        if not is_base_subclass(error=error, baseerror=baseerror):
            raise TypeError(f"{error!r} is not a subclass of {baseerror.__name__}")
    raise ExceptionGroup(group_msg, [error(msg) for error, msg in pairs])


@contextmanager
def reraise(
    catch: type[Exception] | tuple[type[Exception], ...],
    raise_as: type[Exception],
) -> Iterator[None]:
    """Context manager that catches *catch* and re-raises it as *raise_as*.

    Args:
        catch: An exception type (or tuple of types) to intercept.
        raise_as: The exception type to raise in its place.

    Raises:
        raise_as: Wrapping the original exception whenever a *catch* instance
            is raised inside the block.

    Example:
        >>> with reraise(KeyError, ValueError):
        ...     raise KeyError("missing key")
        Traceback (most recent call last):
            ...
        ValueError: 'missing key'
    """
    # NOTE: Catches any exception that is an instance of *catch* within the ``with``
    # block and raises a new *raise_as* instance with the same message, chaining
    # the original via ``__cause__``.  All other exceptions propagate unchanged.

    # Performance Note:
    # The reraise context manager adds lightweight exception type conversion on top of native try/except logic.
    # It introduces minimal overhead and is safe for general-purpose use in most applications.
    try:
        yield
    except catch as exc:
        raise raise_as(str(exc)) from exc
