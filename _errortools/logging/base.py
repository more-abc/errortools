"""BaseLogger — core logger implementation with loguru-style API."""

from __future__ import annotations

import sys
import threading
from collections.abc import Callable
from typing import Any, IO

from .level import Level, get_level, LEVELS
from .record import make_record
from .sink import BaseSink, StreamSink, FileSink, CallableSink


class BaseLogger:
    """A loguru-inspired logger with structured sinks, level filtering, and context binding.

    Key features
    ------------
    - **Leveled methods**: `trace`, `debug`, `info`,
      `success`, `warning`, `error`, `critical`
    - **Sink management**: add/remove multiple typed sinks via `add` /
      `remove` (stream, file, or any callable)
    - **Context binding**: create child loggers with extra fields via
      `bind` — original logger is untouched
    - **Exception capture**: pass ``exception=True`` (or use `exception`)
      to attach the current traceback to any record
    - **Level control**: change the minimum level at runtime via
      `set_level`

    Usage::

        from errortools.logging import logger

        logger.info("Server started on port {}", 8080)
        logger.warning("Disk usage at {pct:.1f}%", pct=92.5)

        with logger.catch():
            risky_operation()

        db_log = logger.bind(db="postgres", user="admin")
        db_log.debug("Query executed in {ms}ms", ms=42)
    """

    def __init__(
        self,
        name: str = "errortools",
        extra: dict[str, Any] | None = None,
    ) -> None:
        self._name = name
        self._extra: dict[str, Any] = extra or {}
        self._sinks: dict[int, BaseSink] = {}
        self._sink_id = 0
        self._lock = threading.Lock()
        self._level: Level = Level.DEBUG

    # ------------------------------------------------------------------
    # Sink management (loguru: logger.add / logger.remove)
    # ------------------------------------------------------------------

    def add(
        self,
        sink: IO[str] | str | Callable[[str], None] | BaseSink,
        *,
        level: str | int | Level = Level.DEBUG,
        colorize: bool | None = None,
        rotation: int = 0,
        retention: int = 0,
        encoding: str = "utf-8",
        fmt: str | None = None,
    ) -> int:
        """Register a new sink and return its integer handle.

        Args:
            sink:      Destination — one of:

                       * A writable text stream (``sys.stderr``, ``sys.stdout``, …)
                       * A file path string or `pathlib.Path`
                       * A callable ``(message: str) -> None``
                       * A `sink.BaseSink` instance

            level:     Minimum log level for this sink.  Accepts a
                       `level.Level`, a level name string, or a
                       numeric value.
            colorize:  Force colour on/off for stream sinks.  ``None``
                       auto-detects TTY.
            rotation:  Byte threshold for file rotation (file sinks only).
            retention: Number of rotated files to keep (file sinks only).
            encoding:  File encoding (file sinks only).
            fmt:       Custom format string.

        Returns:
            An integer sink ID that can be passed to `remove`.
        """
        if isinstance(level, str):
            lv = get_level(level)
        elif isinstance(level, int):
            lv = get_level(level)
        else:
            lv = level

        if isinstance(sink, BaseSink):
            sink_obj = sink
        elif hasattr(sink, "write"):
            sink_obj = StreamSink(sink, level=lv, colorize=colorize, fmt=fmt)  # type: ignore
        elif isinstance(sink, (str,)) or hasattr(sink, "__fspath__"):
            sink_obj = FileSink(
                sink,  # type: ignore[arg-type]
                level=lv,
                rotation=rotation,
                retention=retention,
                encoding=encoding,
                fmt=fmt,
            )
        elif callable(sink):
            sink_obj = CallableSink(sink, level=lv)
        else:
            raise TypeError(f"Unsupported sink type: {type(sink)!r}")

        with self._lock:
            sid = self._sink_id
            self._sinks[sid] = sink_obj
            self._sink_id += 1
        return sid

    def remove(self, sink_id: int | None = None) -> None:
        """Remove a sink by its ID, or remove **all** sinks if ``sink_id`` is ``None``.

        Args:
            sink_id: Handle returned by `add`.  Pass ``None`` to clear all.
        """
        with self._lock:
            if sink_id is None:
                for s in self._sinks.values():
                    s.close()
                self._sinks.clear()
            elif sink_id in self._sinks:
                self._sinks.pop(sink_id).close()

    # ------------------------------------------------------------------
    # Level control
    # ------------------------------------------------------------------

    def set_level(self, level: str | int | Level) -> None:
        """Set the global minimum level for this logger.

        Individual sinks can still have their own, stricter filters.

        Args:
            level: Level name, numeric value, or `level.Level`.
        """
        if isinstance(level, Level):
            self._level = level
        else:
            self._level = get_level(level)

    @property
    def level(self) -> Level:
        """The current global minimum `level.Level`."""
        return self._level

    # ------------------------------------------------------------------
    # Context binding
    # ------------------------------------------------------------------

    def bind(self, **kwargs: Any) -> "BaseLogger":
        """Return a **new** logger that carries extra context fields.

        The original logger is unmodified.  Bound fields appear in
        ``record.extra`` and can be accessed in custom format strings.

        Example::

            req_log = logger.bind(request_id="abc-123")
            req_log.info("Received request")  # record.extra["request_id"] == "abc-123"
        """
        child = BaseLogger(name=self._name, extra={**self._extra, **kwargs})
        with self._lock:
            child._sinks = dict(self._sinks)
            child._sink_id = self._sink_id
            child._level = self._level
        return child

    # ------------------------------------------------------------------
    # Core log dispatch
    # ------------------------------------------------------------------

    def log(
        self,
        level: str | int | Level,
        message: str,
        *args: Any,
        exception: bool = False,
        depth: int = 1,
        **kwargs: Any,
    ) -> None:
        """Emit a log record at an arbitrary level.

        Args:
            level:     Level name, numeric value, or `level.Level`.
            message:   Message template.  Supports ``str.format``-style
                       positional (``{}``) and keyword (``{key}``) placeholders.
            *args:     Positional arguments for the message template.
            exception: Capture the current exception info (like loguru's ``opt(exception=True)``).
            depth:     Stack depth offset for caller location detection.
            **kwargs:  Keyword arguments for the message template.
        """
        if isinstance(level, Level):
            lv = level
        else:
            lv = get_level(level)

        if lv < self._level:
            return

        formatted = message.format(*args, **kwargs) if (args or kwargs) else message
        record = make_record(
            level=lv,
            message=formatted,
            name=self._name,
            depth=depth + 2,  # skip log() + make_record()
            exception=exception,
            extra=self._extra,
        )
        with self._lock:
            sinks = list(self._sinks.values())
        for sink in sinks:
            try:
                sink.emit(record)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Convenience level methods (loguru-compatible)
    # ------------------------------------------------------------------

    def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at TRACE level (numeric 5)."""
        self.log(Level.TRACE, message, *args, depth=2, **kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at DEBUG level (numeric 10)."""
        self.log(Level.DEBUG, message, *args, depth=2, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at INFO level (numeric 20)."""
        self.log(Level.INFO, message, *args, depth=2, **kwargs)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at SUCCESS level (numeric 25)."""
        self.log(Level.SUCCESS, message, *args, depth=2, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at WARNING level (numeric 30)."""
        self.log(Level.WARNING, message, *args, depth=2, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at ERROR level (numeric 40)."""
        self.log(Level.ERROR, message, *args, depth=2, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at CRITICAL level (numeric 50)."""
        self.log(Level.CRITICAL, message, *args, depth=2, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log at ERROR level and attach the current exception traceback.

        Equivalent to ``logger.error(message, exception=True)``.

        Example::

            try:
                1 / 0
            except ZeroDivisionError:
                logger.exception("Math went wrong")
        """
        self.log(Level.ERROR, message, *args, exception=True, depth=2, **kwargs)

    # ------------------------------------------------------------------
    # catch() context manager — loguru-style
    # ------------------------------------------------------------------

    def catch(
        self,
        *exceptions: type[BaseException],
        level: str | int | Level = Level.ERROR,
        reraise: bool = False,
        message: str = "An error has been caught in function '{}', process '{}', thread '{}'",
    ) -> "_CatchContext":
        """Context manager / decorator that logs uncaught exceptions.

        Similar to loguru's ``logger.catch()``.

        Args:
            *exceptions: Exception types to catch.  Defaults to ``Exception``.
            level:       Log level to use when logging the exception.
            reraise:     If ``True``, re-raise after logging.
            message:     Message template — receives ``(function, process_id, thread_name)``.

        Example::

            with logger.catch():
                int("not a number")

            @logger.catch(reraise=True)
            def risky():
                ...
        """
        return _CatchContext(
            logger=self,
            exceptions=exceptions or (Exception,),
            level=level,
            reraise=reraise,
            message=message,
        )

    # ------------------------------------------------------------------
    # opt() — loguru-compatible option builder (minimal subset)
    # ------------------------------------------------------------------

    def opt(
        self,
        *,
        exception: bool = False,
        depth: int = 0,
        lazy: bool = False,
    ) -> "_OptLogger":
        """Return a temporary wrapper with extra options.

        Args:
            exception: Capture current exception info for the next log call.
            depth:     Additional stack depth offset for caller location.
            lazy:      Ignored (reserved for future lazy-evaluation support).

        Example::

            logger.opt(exception=True).error("Something went wrong")
        """
        return _OptLogger(self, exception=exception, extra_depth=depth)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} name={self._name!r} "
            f"level={self._level.name!r} sinks={len(self._sinks)}>"
        )


# ======================================================================
# Internal helpers
# ======================================================================


class _CatchContext:
    """Returned by `BaseLogger.catch`; can also decorate callables."""

    def __init__(
        self,
        logger: BaseLogger,
        exceptions: tuple[type[BaseException], ...],
        level: str | int | Level,
        reraise: bool,
        message: str,
    ) -> None:
        self._logger = logger
        self._exceptions = exceptions
        self._level = level
        self._reraise = reraise
        self._message = message

    # Context manager protocol
    def __enter__(self) -> "_CatchContext":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        if exc_type is None or not issubclass(exc_type, self._exceptions):
            return False
        import os, threading as _t

        frame = sys._getframe(1)
        func = frame.f_code.co_name
        pid = os.getpid()
        tname = _t.current_thread().name
        msg = self._message.format(func, pid, tname)
        try:
            self._logger.log(self._level, msg, exception=True, depth=1)
        except Exception:
            pass
        return not self._reraise

    # Decorator protocol
    def __call__(self, func: Callable) -> Callable:
        from functools import wraps

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with _CatchContext(
                self._logger,
                self._exceptions,
                self._level,
                self._reraise,
                self._message,
            ):
                return func(*args, **kwargs)

        return wrapper


class _OptLogger:
    """Thin wrapper returned by `BaseLogger.opt`."""

    def __init__(
        self, logger: BaseLogger, *, exception: bool, extra_depth: int
    ) -> None:
        self._logger = logger
        self._exception = exception
        self._depth = extra_depth

    def _relay(self, level: Level, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.log(
            level,
            message,
            *args,
            exception=self._exception,
            depth=self._depth + 3,
            **kwargs,
        )

    def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.TRACE, message, *args, **kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.INFO, message, *args, **kwargs)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.SUCCESS, message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.ERROR, message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._relay(Level.CRITICAL, message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.log(
            Level.ERROR,
            message,
            *args,
            exception=True,
            depth=self._depth + 3,
            **kwargs,
        )
