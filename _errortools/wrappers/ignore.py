import traceback
from collections.abc import Callable
from typing import Any, Generic, TypeVar, Optional, TypeAlias

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
    """Context manager & decorator to ignore specified exceptions with rich info."""

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
