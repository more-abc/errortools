"""Interactive logger shell (REPL).

Run ``logger shell`` to launch a Python REPL with pre-imported logging
utilities from errortools and standard-library base classes.
"""

from __future__ import annotations

import code
import logging
import sys  # noqa: F401

from _errortools.logging import (
    BaseLogger,
    CallableSink,
    FileSink,
    Level,
    LEVELS,
    logger,
    Record,
    StreamSink,
)

from .banner import BAMMER

_BANNER: str = str.format(BAMMER, sys=sys)


def start_shell() -> None:
    """Launch an interactive Python REPL with logger helpers in scope."""
    namespace: dict[str, object] = {
        # Logger singleton and level methods
        "logger": logger,
        "info": logger.info,
        "debug": logger.debug,
        "error": logger.error,
        "warning": logger.warning,
        "critical": logger.critical,
        "trace": logger.trace,
        "success": logger.success,
        "exception": logger.exception,
        "catch": logger.catch,
        # errortools logging types
        "Level": Level,
        "LEVELS": LEVELS,
        "BaseLogger": BaseLogger,
        "Record": Record,
        "StreamSink": StreamSink,
        "FileSink": FileSink,
        "CallableSink": CallableSink,
        # std-lib logging base classes
        "Logger": logging.Logger,
        "Handler": logging.Handler,
        "Filter": logging.Filter,
        "Formatter": logging.Formatter,
    }
    code.interact(banner=_BANNER, local=namespace, exitmsg="")
