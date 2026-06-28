"""Interactive logger shell (REPL).

Run ``logger shell`` to launch a Python REPL with pre-imported logging
utilities from errortools and standard-library base classes.
"""

from __future__ import annotations

import code
import logging
import sys
from typing import Any

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


class EasterEgg(object):
    def __repr__(self) -> str:
        return "You find me! Use easteregg() to see something..."

    def __call__(self) -> Any:
        logger.info("I'm just a fool for you")


easteregg: EasterEgg = EasterEgg()

BAMMER: str = """errortools Logger Shell REPL {sys.version} on {sys.platform}
Pre-imported shortcuts: info, debug, error, warning, critical, trace, success, exception, catch
Pre-imported types: logger, Level, LEVELS, BaseLogger, Record, StreamSink, FileSink, CallableSink
Pre-imported std-lib: Logger, Handler, Filter, Formatter
Type "help", "copyright", "credits" or "license" for more information."""

BANNER: str = str.format(BAMMER, sys=sys)


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
        # easteregg
        "easteregg": easteregg,
    }
    code.interact(banner=BANNER, local=namespace, exitmsg="")
