"""Banner text for the logger shell REPL.

Kept in its own module so the banner string is easy to find, easy
to customise, and easy to test in isolation.  No side effects on
import beyond a single ``TEMPLATE`` definition.
"""

from __future__ import annotations

import sys
from typing import Final, Mapping, Union

TEMPLATE: Final[str] = """\
errortools Logger Shell REPL {sys.version} on {sys.platform}
Pre-imported shortcuts: info, debug, error, warning, critical, trace, success, exception, catch
Pre-imported types: logger, Level, LEVELS, BaseLogger, Record, StreamSink, FileSink, CallableSink
Pre-imported std-lib: Logger, Handler, Filter, Formatter
Type "help", "copyright", "credits" or "license" for more information."""


def build_banner(extra: Union[Mapping[str, str], None] = None) -> str:
    """Render the REPL banner for the current interpreter.

    Args:
        extra: Optional mapping merged into the template namespace
            (e.g. ``{"errortools_version": "3.5.6"}``).  Keys already
            present in :data:`TEMPLATE` (``sys``) take precedence
            unless you pass a key that does not collide.

    Returns:
        The formatted banner string.  Always non-empty.
    """
    fmt: dict[str, object] = {"sys": sys}
    if extra:
        for key, value in extra.items():
            fmt.setdefault(key, value)
    return TEMPLATE.format(**fmt)
