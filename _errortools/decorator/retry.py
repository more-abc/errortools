"""
Retry decorator for sync and async functions.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar
import asyncio
import inspect
import time

Func = TypeVar("Func", bound=Callable[..., Any])
ExceptionType = type[BaseException]
ExceptionTypes = tuple[ExceptionType, ...]


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
        on: ExceptionType | ExceptionTypes = Exception,
        delay: float = 0,
    ) -> None:
        if times < 0:
            raise ValueError(f"times must be a non-negative integer, got {times!r}")

        exc_types = on if isinstance(on, tuple) else (on,)
        for t in exc_types:
            if not isinstance(t, type) or not issubclass(t, BaseException):
                raise TypeError(f"Expected Exception subclass, got {t!r}")

        self._times = times
        self._on = exc_types
        self._delay = delay

    def _sync_retry(self, func: Func) -> Func:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: BaseException | None = None
            for attempt in range(self._times + 1):
                try:
                    return func(*args, **kwargs)
                except self._on as exc:
                    last_exc = exc
                    if attempt < self._times and self._delay:
                        time.sleep(self._delay)
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("No exception to raise")

        return wrapper  # type: ignore

    def _async_retry(self, func: Func) -> Func:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: BaseException | None = None
            for attempt in range(self._times + 1):
                try:
                    return await func(*args, **kwargs)
                except self._on as exc:
                    last_exc = exc
                    if attempt < self._times and self._delay:
                        await asyncio.sleep(self._delay)
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("No exception to raise")

        return async_wrapper  # type: ignore

    def __call__(self, func: Func) -> Func:
        if inspect.iscoroutinefunction(func):
            return self._async_retry(func)
        return self._sync_retry(func)
