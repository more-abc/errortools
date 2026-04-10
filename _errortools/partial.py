"""Partial functions."""

from functools import partial

from .ignore import ignore, ignore_subclass, ignore_warns, fast_ignore, timeout, retry
from .cache import error_cache
from .const import (
    LARGE_ERROR_CACHE_SIZE,
    SMALL_ERROR_CACHE_SIZE,
    DEFAULT_ERROR_CACHE_SIZE,
    UNLIMITED_ERROR_CACHE,
)

# ------------------------------------------------------------------
# ignore
# ------------------------------------------------------------------

ignoreTypeError = partial(ignore, TypeError)
ignoreValueError = partial(ignore, ValueError)
ignoreIndexError = partial(ignore, IndexError)
ignoreKeyError = partial(ignore, KeyError)
ignoreAttributeError = partial(ignore, AttributeError)
ignoreNameError = partial(ignore, NameError)
ignoreZeroDivisionError = partial(ignore, ZeroDivisionError)
ignoreFileNotFoundError = partial(ignore, FileNotFoundError)
ignorePermissionError = partial(ignore, PermissionError)
ignoreOSError = partial(ignore, OSError)
ignoreIOError = partial(ignore, IOError)
ignoreRuntimeError = partial(ignore, RuntimeError)
ignoreNotImplementedError = partial(ignore, NotImplementedError)
ignoreOverflowError = partial(ignore, OverflowError)
ignoreTimeoutError = partial(ignore, TimeoutError)

# ------------------------------------------------------------------
# ignore
# ------------------------------------------------------------------

fast_ignoreTypeError = partial(fast_ignore, TypeError)
fast_ignoreValueError = partial(fast_ignore, ValueError)
fast_ignoreIndexError = partial(fast_ignore, IndexError)
fast_ignoreKeyError = partial(fast_ignore, KeyError)
fast_ignoreAttributeError = partial(fast_ignore, AttributeError)
fast_ignoreNameError = partial(fast_ignore, NameError)
fast_ignoreZeroDivisionError = partial(fast_ignore, ZeroDivisionError)
fast_ignoreFileNotFoundError = partial(fast_ignore, FileNotFoundError)
fast_ignorePermissionError = partial(fast_ignore, PermissionError)
fast_ignoreOSError = partial(fast_ignore, OSError)
fast_ignoreIOError = partial(fast_ignore, IOError)
fast_ignoreRuntimeError = partial(fast_ignore, RuntimeError)
fast_ignoreNotImplementedError = partial(fast_ignore, NotImplementedError)
fast_ignoreOverflowError = partial(fast_ignore, OverflowError)
fast_ignoreTimeoutError = partial(fast_ignore, TimeoutError)

# ------------------------------------------------------------------
# ignore_subclass
# ------------------------------------------------------------------

ignoreSubclassException = partial(ignore_subclass, Exception)
ignoreSubclassOSError = partial(ignore_subclass, OSError)

# ------------------------------------------------------------------
# ignore_warns
# ------------------------------------------------------------------

ignoreUserWarning = partial(ignore_warns, UserWarning)
ignoreDeprecationWarning = partial(ignore_warns, DeprecationWarning)
ignorePendingDeprecationWarning = partial(ignore_warns, PendingDeprecationWarning)
ignoreRuntimeWarning = partial(ignore_warns, RuntimeWarning)
ignoreSyntaxWarning = partial(ignore_warns, SyntaxWarning)
ignoreFutureWarning = partial(ignore_warns, FutureWarning)
ignoreImportWarning = partial(ignore_warns, ImportWarning)
ignoreUnicodeWarning = partial(ignore_warns, UnicodeWarning)
ignoreBytesWarning = partial(ignore_warns, BytesWarning)
ignoreResourceWarning = partial(ignore_warns, ResourceWarning)

# ------------------------------------------------------------------
# ignore
# ------------------------------------------------------------------

timeout_1s = partial(timeout, 1)
timeout_2s = partial(timeout, 2)
timeout_3s = partial(timeout, 3)
timeout_5s = partial(timeout, 5)
timeout_10s = partial(timeout, 10)
timeout_30s = partial(timeout, 30)

# ------------------------------------------------------------------
# retry
# ------------------------------------------------------------------

retry_1 = partial(retry, times=1)
retry_2 = partial(retry, times=2)
retry_3 = partial(retry, times=3)
retry_5 = partial(retry, times=5)
retry_10 = partial(retry, times=10)

retry_1_delay_1s = partial(retry, times=1, delay=1)
retry_2_delay_1s = partial(retry, times=2, delay=1)
retry_3_delay_1s = partial(retry, times=3, delay=1)
retry_3_delay_2s = partial(retry, times=3, delay=2)
retry_5_delay_1s = partial(retry, times=5, delay=1)

# ------------------------------------------------------------------
# error_cache
# ------------------------------------------------------------------

unlimited_error_cache = partial(error_cache, maxsize=UNLIMITED_ERROR_CACHE)
lru_error_cache = partial(error_cache, maxsize=DEFAULT_ERROR_CACHE_SIZE)
small_error_cache = partial(error_cache, maxsize=SMALL_ERROR_CACHE_SIZE)
large_error_cache = partial(error_cache, maxsize=LARGE_ERROR_CACHE_SIZE)
