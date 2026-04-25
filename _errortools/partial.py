"""Partial function presets for errortools."""

from __future__ import annotations

from functools import partial
from typing import Callable

from .ignore import (
    ignore,
    ignore_subclass,
    ignore_warns,
    fast_ignore,
    timeout,
    retry,
)
from .decorator.cache import error_cache
from .const import (
    LARGE_ERROR_CACHE_SIZE,
    SMALL_ERROR_CACHE_SIZE,
    DEFAULT_ERROR_CACHE_SIZE,
    UNLIMITED_ERROR_CACHE,
)

# ------------------------------------------------------------------
# ignore: Common exception shortcuts
# ------------------------------------------------------------------

ignoreTypeError: Callable = partial(ignore, TypeError)
ignoreValueError: Callable = partial(ignore, ValueError)
ignoreIndexError: Callable = partial(ignore, IndexError)
ignoreKeyError: Callable = partial(ignore, KeyError)
ignoreAttributeError: Callable = partial(ignore, AttributeError)
ignoreNameError: Callable = partial(ignore, NameError)
ignoreZeroDivisionError: Callable = partial(ignore, ZeroDivisionError)
ignoreFileNotFoundError: Callable = partial(ignore, FileNotFoundError)
ignorePermissionError: Callable = partial(ignore, PermissionError)
ignoreOSError: Callable = partial(ignore, OSError)
ignoreIOError: Callable = partial(ignore, IOError)
ignoreRuntimeError: Callable = partial(ignore, RuntimeError)
ignoreNotImplementedError: Callable = partial(ignore, NotImplementedError)
ignoreOverflowError: Callable = partial(ignore, OverflowError)
ignoreTimeoutError: Callable = partial(ignore, TimeoutError)

# ------------------------------------------------------------------
# fast_ignore
# ------------------------------------------------------------------

fast_ignoreTypeError: Callable = partial(fast_ignore, TypeError)
fast_ignoreValueError: Callable = partial(fast_ignore, ValueError)
fast_ignoreIndexError: Callable = partial(fast_ignore, IndexError)
fast_ignoreKeyError: Callable = partial(fast_ignore, KeyError)
fast_ignoreAttributeError: Callable = partial(fast_ignore, AttributeError)
fast_ignoreNameError: Callable = partial(fast_ignore, NameError)
fast_ignoreZeroDivisionError: Callable = partial(fast_ignore, ZeroDivisionError)
fast_ignoreFileNotFoundError: Callable = partial(fast_ignore, FileNotFoundError)
fast_ignorePermissionError: Callable = partial(fast_ignore, PermissionError)
fast_ignoreOSError: Callable = partial(fast_ignore, OSError)
fast_ignoreIOError: Callable = partial(fast_ignore, IOError)
fast_ignoreRuntimeError: Callable = partial(fast_ignore, RuntimeError)
fast_ignoreNotImplementedError: Callable = partial(fast_ignore, NotImplementedError)
fast_ignoreOverflowError: Callable = partial(fast_ignore, OverflowError)
fast_ignoreTimeoutError: Callable = partial(fast_ignore, TimeoutError)

# ------------------------------------------------------------------
# ignore_subclass
# ------------------------------------------------------------------

ignoreSubclassException: Callable = partial(ignore_subclass, Exception)
ignoreSubclassOSError: Callable = partial(ignore_subclass, OSError)

# ------------------------------------------------------------------
# ignore_warns: Warning presets
# ------------------------------------------------------------------

ignoreUserWarning: Callable = partial(ignore_warns, UserWarning)
ignoreDeprecationWarning: Callable = partial(ignore_warns, DeprecationWarning)
ignorePendingDeprecationWarning: Callable = partial(
    ignore_warns, PendingDeprecationWarning
)
ignoreRuntimeWarning: Callable = partial(ignore_warns, RuntimeWarning)
ignoreSyntaxWarning: Callable = partial(ignore_warns, SyntaxWarning)
ignoreFutureWarning: Callable = partial(ignore_warns, FutureWarning)
ignoreImportWarning: Callable = partial(ignore_warns, ImportWarning)
ignoreUnicodeWarning: Callable = partial(ignore_warns, UnicodeWarning)
ignoreBytesWarning: Callable = partial(ignore_warns, BytesWarning)
ignoreResourceWarning: Callable = partial(ignore_warns, ResourceWarning)

# ------------------------------------------------------------------
# timeout presets (seconds)
# ------------------------------------------------------------------

timeout_1s: Callable = partial(timeout, 1)
timeout_2s: Callable = partial(timeout, 2)
timeout_3s: Callable = partial(timeout, 3)
timeout_5s: Callable = partial(timeout, 5)
timeout_10s: Callable = partial(timeout, 10)
timeout_30s: Callable = partial(timeout, 30)

# ------------------------------------------------------------------
# retry presets
# ------------------------------------------------------------------

retry_1: Callable = partial(retry, times=1)
retry_2: Callable = partial(retry, times=2)
retry_3: Callable = partial(retry, times=3)
retry_5: Callable = partial(retry, times=5)
retry_10: Callable = partial(retry, times=10)

retry_1_delay_1s: Callable = partial(retry, times=1, delay=1)
retry_2_delay_1s: Callable = partial(retry, times=2, delay=1)
retry_3_delay_1s: Callable = partial(retry, times=3, delay=1)
retry_3_delay_2s: Callable = partial(retry, times=3, delay=2)
retry_5_delay_1s: Callable = partial(retry, times=5, delay=1)

# ------------------------------------------------------------------
# error cache presets
# ------------------------------------------------------------------

unlimited_error_cache: Callable = partial(error_cache, maxsize=UNLIMITED_ERROR_CACHE)
lru_error_cache: Callable = partial(error_cache, maxsize=DEFAULT_ERROR_CACHE_SIZE)
small_error_cache: Callable = partial(error_cache, maxsize=SMALL_ERROR_CACHE_SIZE)
large_error_cache: Callable = partial(error_cache, maxsize=LARGE_ERROR_CACHE_SIZE)


# ------------------------------------------------------------------
# Export all
# ------------------------------------------------------------------

__all__ = [
    # ignore
    "ignoreTypeError",
    "ignoreValueError",
    "ignoreIndexError",
    "ignoreKeyError",
    "ignoreAttributeError",
    "ignoreNameError",
    "ignoreZeroDivisionError",
    "ignoreFileNotFoundError",
    "ignorePermissionError",
    "ignoreOSError",
    "ignoreIOError",
    "ignoreRuntimeError",
    "ignoreNotImplementedError",
    "ignoreOverflowError",
    "ignoreTimeoutError",
    # fast_ignore
    "fast_ignoreTypeError",
    "fast_ignoreValueError",
    "fast_ignoreIndexError",
    "fast_ignoreKeyError",
    "fast_ignoreAttributeError",
    "fast_ignoreNameError",
    "fast_ignoreZeroDivisionError",
    "fast_ignoreFileNotFoundError",
    "fast_ignorePermissionError",
    "fast_ignoreOSError",
    "fast_ignoreIOError",
    "fast_ignoreRuntimeError",
    "fast_ignoreNotImplementedError",
    "fast_ignoreOverflowError",
    "fast_ignoreTimeoutError",
    # ignore_subclass
    "ignoreSubclassException",
    "ignoreSubclassOSError",
    # ignore_warns
    "ignoreUserWarning",
    "ignoreDeprecationWarning",
    "ignorePendingDeprecationWarning",
    "ignoreRuntimeWarning",
    "ignoreSyntaxWarning",
    "ignoreFutureWarning",
    "ignoreImportWarning",
    "ignoreUnicodeWarning",
    "ignoreBytesWarning",
    "ignoreResourceWarning",
    # timeout
    "timeout_1s",
    "timeout_2s",
    "timeout_3s",
    "timeout_5s",
    "timeout_10s",
    "timeout_30s",
    # retry
    "retry_1",
    "retry_2",
    "retry_3",
    "retry_5",
    "retry_10",
    "retry_1_delay_1s",
    "retry_2_delay_1s",
    "retry_3_delay_1s",
    "retry_3_delay_2s",
    "retry_5_delay_1s",
    # cache
    "unlimited_error_cache",
    "lru_error_cache",
    "small_error_cache",
    "large_error_cache",
]
