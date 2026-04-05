"""Log level definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Level:
    """Represents a single log level with a name, numeric value, and ANSI color."""

    name: str
    no: int
    color: str  # ANSI escape prefix, e.g. "\033[32m"
    icon: str  # single-char icon shown in formatted output

    # ------------------------------------------------------------------ #
    # Pre-defined levels (loguru-compatible ordering)
    # ------------------------------------------------------------------ #

    TRACE: ClassVar[Level]
    DEBUG: ClassVar[Level]
    INFO: ClassVar[Level]
    SUCCESS: ClassVar[Level]
    WARNING: ClassVar[Level]
    ERROR: ClassVar[Level]
    CRITICAL: ClassVar[Level]

    def __str__(self) -> str:
        return self.name

    def __lt__(self, other: Level) -> bool:
        return self.no < other.no

    def __le__(self, other: Level) -> bool:
        return self.no <= other.no

    def __gt__(self, other: Level) -> bool:
        return self.no > other.no

    def __ge__(self, other: Level) -> bool:
        return self.no >= other.no


# Inject class-level constants after the class is defined so frozen dataclass
# works correctly (we cannot assign inside the class body).
Level.TRACE = Level("TRACE", 5, "\033[34m", "✎")  # blue
Level.DEBUG = Level("DEBUG", 10, "\033[36m", "⚙")  # cyan
Level.INFO = Level("INFO", 20, "\033[32m", "ℹ")  # green
Level.SUCCESS = Level("SUCCESS", 25, "\033[92m", "✔")  # bright green
Level.WARNING = Level("WARNING", 30, "\033[33m", "⚠")  # yellow
Level.ERROR = Level("ERROR", 40, "\033[31m", "✘")  # red
Level.CRITICAL = Level("CRITICAL", 50, "\033[1;31m", "☠")  # bold red


# Ordered list for iteration / lookup
LEVELS: tuple[Level, ...] = (
    Level.TRACE,
    Level.DEBUG,
    Level.INFO,
    Level.SUCCESS,
    Level.WARNING,
    Level.ERROR,
    Level.CRITICAL,
)

_NAME_MAP: dict[str, Level] = {lv.name: lv for lv in LEVELS}
_NO_MAP: dict[int, Level] = {lv.no: lv for lv in LEVELS}


def get_level(name_or_no: str | int) -> Level:
    """Return a `Level` by name (case-insensitive) or numeric value.

    Raises:
        KeyError: If the level is not found.
    """
    if isinstance(name_or_no, str):
        key = name_or_no.upper()
        if key not in _NAME_MAP:
            raise KeyError(f"Unknown log level: {name_or_no!r}")
        return _NAME_MAP[key]
    if name_or_no not in _NO_MAP:
        raise KeyError(f"Unknown log level number: {name_or_no!r}")
    return _NO_MAP[name_or_no]
