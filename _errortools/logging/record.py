"""Log record — the structured object passed to every sink."""

from __future__ import annotations

import sys
import threading
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Any

if sys.version_info >= (3, 9):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc

from .level import Level


@dataclass
class Record:
    """Immutable snapshot of a single log event.

    Mirrors loguru's record dict but as a typed dataclass.

    Attributes:
        time:       UTC timestamp when the record was created.
        level:      The `logging.level.Level` of this event.
        message:    The formatted log message (after ``str.format`` / f-string).
        name:       Logger name (set by the caller or auto-detected).
        file:       Source file name (``__file__``).
        line:       Source line number.
        function:   Calling function name.
        thread_id:  OS thread identifier.
        thread_name: Thread name.
        process_id: OS process id.
        exception:  The active exception info tuple, or ``None``.
        extra:      Arbitrary key/value context bound via ``logger.bind()``.
    """

    time: datetime
    level: Level
    message: str
    name: str
    file: str
    line: int
    function: str
    thread_id: int
    thread_name: str
    process_id: int
    exception: tuple[type[BaseException], BaseException, TracebackType | None] | None
    extra: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def exc_text(self) -> str | None:
        """Formatted traceback string, or ``None`` if no exception."""
        if self.exception is None:
            return None
        return "".join(traceback.format_exception(*self.exception))

    def __str__(self) -> str:
        return self.message


def _current_frame_info(depth: int = 2) -> tuple[str, int, str]:
    """Return (filename, lineno, function_name) *depth* frames up the call stack."""
    frame = sys._getframe(depth)
    return frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name


def make_record(
    level: Level,
    message: str,
    name: str,
    depth: int,
    exception: bool,
    extra: dict[str, Any],
) -> Record:
    """Build a `Record` for the given log call.

    Args:
        level:     Log level.
        message:   Already-formatted message string.
        name:      Logger name.
        depth:     How many frames to skip when locating caller info.
        exception: Whether to capture the current exception info.
        extra:     Bound context from ``logger.bind()``.
    """
    file, line, func = _current_frame_info(depth)
    exc_info = sys.exc_info() if exception else None
    if exc_info == (None, None, None):
        exc_info = None
    t = threading.current_thread()
    import os

    return Record(
        time=datetime.now(UTC),
        level=level,
        message=message,
        name=name,
        file=file,
        line=line,
        function=func,
        thread_id=t.ident or 0,
        thread_name=t.name,
        process_id=os.getpid(),
        exception=exc_info,  # type: ignore[arg-type]
        extra=dict(extra),
    )
