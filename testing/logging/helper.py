"""Helpers functions for logging tests was all here."""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


from __future__ import annotations

from _errortools.logging import BaseLogger, Level

import io


def _make_logger(*args, **kwargs) -> tuple[BaseLogger, io.StringIO]:
    buf = io.StringIO()
    lg = BaseLogger(*args, **kwargs)
    lg.add(buf, level=Level.TRACE, colorize=False)
    return lg, buf
