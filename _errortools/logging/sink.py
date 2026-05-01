"""Sink abstraction — destinations that receive formatted log records."""

from __future__ import annotations

import sys
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import IO, Any

if sys.version_info >= (3, 9):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc

from .level import Level
from .record import Record

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"


def _supports_color(stream: IO[str]) -> bool:
    """Return True if *stream* is a real TTY that likely supports ANSI codes."""
    return hasattr(stream, "isatty") and stream.isatty()


def _format_record(record: Record, colorize: bool, fmt: str | None) -> str:
    """Render a `record.Record` to a string.

    Args:
        record:   The log record to render.
        colorize: Whether to emit ANSI colour codes.
        fmt:      Optional custom format string.  Placeholders:
                  ``{time}``, ``{level}``, ``{name}``, ``{file}``, ``{line}``,
                  ``{function}``, ``{message}``.  If ``None`` the default
                  loguru-style format is used.
    """
    lv: Level = record.level
    time_str = record.time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    if fmt is not None:
        text = fmt.format(
            time=time_str,
            level=lv.name,
            name=record.name,
            file=record.file,
            line=record.line,
            function=record.function,
            message=record.message,
        )
    else:
        # Default format (loguru-inspired)
        # 2024-01-01 12:00:00.000 | ℹ INFO     | module 10 - message
        level_tag = f"{lv.icon} {lv.name:<8}"
        location = f"{Path(record.file).stem}:{record.function}:{record.line}"

        if colorize:
            c = lv.color
            text = (
                f"{_DIM}{time_str}{_RESET} | "
                f"{c}{_BOLD}{level_tag}{_RESET} | "
                f"{_DIM}{location}{_RESET} - "
                f"{c}{record.message}{_RESET}"
            )
        else:
            text = f"{time_str} | {level_tag} | {location} - {record.message}"

    # Append exception traceback if present
    if record.exception is not None and record.exc_text:
        text = text + "\n" + record.exc_text.rstrip()

    return text


# ======================================================================
# Abstract base
# ======================================================================


class BaseSink(ABC):
    """Abstract base class for log sinks."""

    @abstractmethod
    def emit(self, record: Record) -> None:
        """Write *record* to this sink."""

    def close(self) -> None:
        """Optional cleanup called when sink is removed."""


# ======================================================================
# Stream sink (stderr / stdout / any IO)
# ======================================================================


class StreamSink(BaseSink):
    """Write colourised log lines to a text stream (default: ``sys.stderr``).

    Args:
        stream:    Writable text stream.  Defaults to ``sys.stderr``.
        level:     Minimum level to emit.  Defaults to ``Level.DEBUG``.
        colorize:  Force colour on/off.  ``None`` (default) auto-detects TTY.
        fmt:       Custom format string.  ``None`` uses the default format.
        diagnose:  Include exception variable values in tracebacks (future).
    """

    def __init__(
        self,
        stream: IO[str] | None = None,
        level: Level = Level.DEBUG,
        colorize: bool | None = None,
        fmt: str | None = None,
    ) -> None:
        self._stream = stream or sys.stderr
        self.level = level
        self._colorize = _supports_color(self._stream) if colorize is None else colorize
        self._fmt = fmt
        self._lock = threading.Lock()

    def emit(self, record: Record) -> None:
        if record.level < self.level:
            return
        line = _format_record(record, self._colorize, self._fmt)
        with self._lock:
            print(line, file=self._stream, flush=True)


# ======================================================================
# File sink (with optional rotation)
# ======================================================================


class FileSink(BaseSink):
    """Write plain-text log lines to a file, with optional size-based rotation.

    Args:
        path:      Path to the log file.  Parent directories are created.
        level:     Minimum level to emit.  Defaults to ``Level.DEBUG``.
        rotation:  Maximum file size in bytes before rotation.  ``0`` = no rotation.
        retention: Number of rotated files to keep (oldest are deleted).  ``0`` = keep all.
        encoding:  File encoding.  Defaults to ``"utf-8"``.
        fmt:       Custom format string.  ``None`` uses the default format.
    """

    def __init__(
        self,
        path: str | Path,
        level: Level = Level.DEBUG,
        rotation: int = 0,
        retention: int = 0,
        encoding: str = "utf-8",
        fmt: str | None = None,
    ) -> None:
        self._path = Path(path)
        self.level = level
        self._rotation = rotation
        self._retention = retention
        self._encoding = encoding
        self._fmt = fmt
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file: IO[str] = open(self._path, "a", encoding=self._encoding)

    # ------------------------------------------------------------------ #
    # Rotation helpers
    # ------------------------------------------------------------------ #

    def _needs_rotation(self) -> bool:
        if self._rotation <= 0:
            return False
        try:
            return self._path.stat().st_size >= self._rotation
        except FileNotFoundError:
            return False

    def _rotate(self) -> None:
        self._file.close()
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        rotated = self._path.with_suffix(f".{stamp}{self._path.suffix}")
        self._path.replace(rotated)
        self._purge_old()
        self._file = open(self._path, "a", encoding=self._encoding)

    def _purge_old(self) -> None:
        if self._retention <= 0:
            return
        stem = self._path.stem
        suffix = self._path.suffix
        parent = self._path.parent
        rotated = sorted(
            parent.glob(f"{stem}.*{suffix}"),
            key=lambda p: p.stat().st_mtime,
        )
        while len(rotated) > self._retention:
            rotated.pop(0).unlink(missing_ok=True)

    # ------------------------------------------------------------------ #

    def emit(self, record: Record) -> None:
        if record.level < self.level:
            return
        line = _format_record(record, colorize=False, fmt=self._fmt)
        with self._lock:
            if self._needs_rotation():
                self._rotate()
            print(line, file=self._file, flush=True)

    def close(self) -> None:
        with self._lock:
            self._file.close()


# ======================================================================
# Callable sink (wrap any function)
# ======================================================================


class CallableSink(BaseSink):
    """Wrap a plain callable as a sink.

    The callable receives a fully-rendered ``str`` (the formatted log line).

    Args:
        func:  ``(message: str) -> None`` callable.
        level: Minimum level to emit.
    """

    def __init__(self, func: Any, level: Level = Level.DEBUG) -> None:
        if not callable(func):
            raise TypeError(f"Expected callable, got {func!r}")
        self._func = func
        self.level = level

    def emit(self, record: Record) -> None:
        if record.level < self.level:
            return
        line = _format_record(record, colorize=False, fmt=None)
        self._func(line)
