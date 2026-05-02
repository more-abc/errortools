"""Future-focused lightweight exception handling utilities."""

from __future__ import annotations

from typing import TypeAlias, cast, Literal

__all__ = [
    "super_fast_ignore",
    "super_fast_catch",
    "super_fast_reraise",
    "ExceptionCollector",
]

_ExcType: TypeAlias = type[BaseException]


class super_fast_ignore:
    """Ultra-lightweight context manager to suppress exceptions."""

    __slots__ = ("excs",)

    def __init__(self, *excs: _ExcType) -> None:
        self.excs = excs

    def __enter__(self) -> None:
        return

    def __exit__(self, typ: _ExcType | None, *_) -> bool:
        if typ is None:
            return False
        excs = self.excs
        return issubclass(typ, excs)


class super_fast_catch:
    """Ultra-lightweight context manager to catch and store exceptions.

    Args:
        *excs: Exception types to catch. Empty means catch all.

    Example:
        >>> with super_fast_catch(ValueError) as ctx:
        ...     raise ValueError("oops")
        >>> print(ctx.exception)
    """

    __slots__ = ("excs", "exception")

    def __init__(self, *excs: _ExcType) -> None:
        self.excs = excs if excs else (BaseException,)
        self.exception: BaseException | None = None

    def __enter__(self) -> super_fast_catch:
        return self

    def __exit__(self, typ: _ExcType | None, val, *_) -> bool:
        if typ is None or not issubclass(typ, self.excs):
            return False
        self.exception = val
        return True


class super_fast_reraise:
    """Ultra-lightweight context manager to convert exception types.

    Args:
        catch: Exception type(s) to intercept.
        raise_as: Exception type to raise instead.

    Example:
        >>> with super_fast_reraise(KeyError, ValueError):
        ...     raise KeyError("missing")
        >>> # Raises ValueError: missing
    """

    __slots__ = ("catch", "raise_as")

    def __init__(
        self,
        catch: _ExcType | tuple[_ExcType, ...],
        raise_as: _ExcType,
    ) -> None:
        self.catch = catch if isinstance(catch, tuple) else (catch,)
        self.raise_as = raise_as

    def __enter__(self) -> None:
        return

    def __exit__(self, typ: _ExcType | None, val, *_) -> Literal[False]:
        if typ is None or not issubclass(typ, self.catch):
            return False
        raise self.raise_as(str(val)) from val


class ExceptionCollector:
    """Collect multiple exceptions and raise together at the end.

    Useful for batch operations where you want all errors, not just the first.

    Example:
        >>> collector = ExceptionCollector()
        >>> with collector:
        ...     collector.catch(int, "bad1")
        ...     collector.catch(int, "bad2")
        >>> if collector.has_errors:
        ...     collector.raise_all()
    """

    __slots__ = ("_exceptions", "_stop_on_first")

    def __init__(self, stop_on_first: bool = False) -> None:
        self._exceptions: list[BaseException] = []
        self._stop_on_first = stop_on_first

    def __enter__(self) -> ExceptionCollector:
        return self

    def __exit__(self, exc_typ, exc_val, *_) -> bool:
        if exc_typ is not None:
            self._exceptions.append(exc_val)
            if self._stop_on_first:
                return False
            return True
        return False

    def catch(self, func, *args, **kwargs) -> bool:
        """Try to call func and catch any exception. Returns True if exception caught."""
        try:
            func(*args, **kwargs)
            return False
        except BaseException as exc:
            self._exceptions.append(exc)
            if self._stop_on_first:
                raise
            return True

    def add(self, exc: BaseException) -> None:
        """Manually add an exception."""
        self._exceptions.append(exc)
        if self._stop_on_first:
            raise exc

    @property
    def has_errors(self) -> bool:
        """Check if any exceptions were collected."""
        return len(self._exceptions) > 0

    @property
    def count(self) -> int:
        """Get number of collected exceptions."""
        return len(self._exceptions)

    @property
    def exceptions(self) -> list[BaseException]:
        """Get the list of exceptions."""
        return self._exceptions

    def raise_all(self, message: str = "collected errors") -> None:
        """Raise all collected exceptions as ExceptionGroup."""
        if self._exceptions:
            raise ExceptionGroup(message, cast(list[Exception], self._exceptions))

    def clear(self) -> None:
        """Clear all exceptions."""
        self._exceptions.clear()
