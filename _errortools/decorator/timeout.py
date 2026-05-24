"""
Timeout decorator for async functions.
"""

from functools import wraps
from typing import Callable
import asyncio
import inspect


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
