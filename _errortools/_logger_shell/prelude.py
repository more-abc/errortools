"""Pre-REPL hook objects: easter egg and ``_`` / ``__`` / ``___`` history.

These are kept in their own module so the ``_logger_shell``
``__init__.py`` stays focused on the public API and so the easter
egg / history hook can be tested in isolation.
"""

from __future__ import annotations

import sys
from typing import Any, Final

from _errortools.logging import logger
from _errortools.logging.base import BaseLogger


class EasterEgg:
    """A hidden toy for the REPL.

    Type ``easteregg()`` at the prompt to see what happens.  The
    instance is exported as :data:`easteregg`.
    """

    __slots__ = ("logger",)

    def __init__(self, log: BaseLogger):
        self.logger: BaseLogger = log

    def __repr__(self) -> str:
        return "You find me! Use easteregg() to see something..."

    def __call__(self) -> Any:
        """Log a single info-level message and return ``None``."""
        self.logger.info("I'm just a fool for you")
        return None


class HistoryHook:
    """Display hook that rotates ``_``, ``__``, ``___`` history variables.

    CPython's default :data:`sys.displayhook` assigns the result of
    the last expression to ``_``; this subclass extends that
    behaviour to also keep the previous two results in ``__`` and
    ``___`` (mirroring the IPython / Jupyter convention).

    The original hook is preserved and called after the rotation so
    pretty-printing, ``_oh`` integration, etc. still work.
    """

    __slots__ = ("v1", "v2", "v3", "original_hook")

    # Explicit type for ``original_hook`` so type checkers can see
    # the value walked out of the loop in ``__init__``.
    original_hook: Any

    def __init__(self) -> None:
        self.v1: Any = None
        self.v2: Any = None
        self.v3: Any = None
        # Walk past any previously installed ``HistoryHook`` instances
        # so that ``original_hook`` is always the *real* (default)
        # displayhook, not another wrapper.  This keeps the delegation
        # chain at depth one even if ``start_shell`` (or similar) is
        # invoked multiple times in the same process.
        hook: Any = sys.displayhook
        while isinstance(hook, HistoryHook):
            hook = hook.original_hook
        self.original_hook = hook

    def __call__(self, value: Any) -> Any:
        """Rotate the history and delegate to the original hook.

        Mirrors the CPython default ``sys.displayhook`` behaviour of
        short-circuiting on ``None`` (e.g. the empty REPL prompt):
        ``_``/``__``/``___`` are left untouched in that case.
        """
        # CPython's default displayhook is a no-op for ``None``; match it
        # so the history is not polluted by empty prompt results.
        if value is None:
            return None

        # Rotate right: old v2 -> v3, old v1 -> v2, value -> v1.
        self.v3 = self.v2
        self.v2 = self.v1
        self.v1 = value

        # The caller's locals are one frame up; writing to ``f_locals``
        # does *not* propagate to actual variables, but it is what the
        # default displayhook relies on, so we keep the same shape.
        try:
            frame = sys._getframe(1)
            ns = frame.f_locals
            ns["_"] = self.v1
            ns["__"] = self.v2
            ns["___"] = self.v3
        except ValueError:
            # No caller frame available (e.g. invoked from C code or
            # an unusual context).  Rotation and delegation still
            # happen; only the namespace update is skipped.
            pass

        return self.original_hook(value)


# Module-level singleton — exported by the package for convenience.
easteregg: Final[EasterEgg] = EasterEgg(logger)
"""A ready-to-use :class:`EasterEgg` instance."""
