import traceback
from collections.abc import Callable
import sys

if sys.version_info <= (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias
    
from typing import Any, Generic, TypeVar, Optional

_T = TypeVar("_T", bound=Callable[..., Any])
_ExcType: TypeAlias = type[Exception]


class IgnoredError:
    """Information holder for ignored exceptions."""

    __slots__ = (
        "name",
        "be_ignore",
        "count",
        "traceback",
        "exception",
    )

    def __init__(self) -> None:
        self.name: Optional[str] = None
        self.be_ignore: bool = False
        self.count: int = 0
        self.traceback: Optional[str] = None
        self.exception: Optional[Exception] = None

    def reset(self) -> None:
        self.name = None
        self.be_ignore = False
        self.traceback = None
        self.exception = None


class ErrorIgnoreWrapper(Generic[_T]):
    """Context manager & decorator to ignore specified exceptions with rich info.

    Catches and suppresses the given exception types within a ``with`` block
    or when used as a decorator, while recording detailed information about
    any suppressed exception.

    When used as a context manager, ``__enter__`` returns an ``IgnoredError``
    instance that provides the following attributes after the block executes.
    """

    #     Attributes:
    #     be_ignore (bool):
    #         ``True`` if an exception was suppressed during the block,
    #         ``False`` otherwise.

    #     name (str | None):
    #         The class name of the suppressed exception
    #         (e.g. ``'KeyError'``, ``'ValueError'``).
    #         ``None`` if no exception occurred.

    #     count (int):
    #         Number of exceptions suppressed in this context block.
    #         Typically 1 unless the context manager is reused.

    #     exception (Exception | None):
    #         The original exception instance that was caught and suppressed.
    #         ``None`` if no exception occurred.

    #     traceback (str | None):
    #         Formatted traceback string showing where the suppressed exception
    #         occurred.  Useful for debugging.  ``None`` if no exception occurred.

    # Example:
    #     >>> from errortools import ignore
    #     >>> with ignore(KeyError) as err:
    #     ...     _ = {}["missing"]
    #     >>> err.be_ignore
    #     True
    #     >>> err.name
    #     'KeyError'

    def __init__(self, *excs: _ExcType) -> None:
        for exc in excs:
            if not isinstance(exc, type) or not issubclass(exc, Exception):
                raise TypeError(f"Expected Exception subclass, got {exc!r}")

        self._excs = excs
        self._info = IgnoredError()

    def __enter__(self) -> IgnoredError:
        self._info.reset()
        return self._info

    def __exit__(
        self,
        exc_type: Optional[_ExcType],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> bool:
        if exc_type is None:
            return False

        if exc_type not in self._excs:
            return False

        self._info.name = exc_type.__name__
        self._info.be_ignore = True
        self._info.count += 1
        self._info.traceback = "".join(
            traceback.format_exception(exc_type, exc_val, exc_tb)
        )
        self._info.exception = exc_val
        return True

    def __call__(self, func: _T) -> _T:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            with self:
                return func(*args, **kwargs)

        wrapped.__wrapped__ = func  # type: ignore
        return wrapped  # type: ignore
