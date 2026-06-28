"""Interactive logger shell (REPL).

Run ``logger shell`` to launch a Python REPL with pre-imported logging
utilities from errortools and standard-library base classes.

Module layout
-------------
- :mod:`_errortools._logger_shell.banner`  - the REPL banner text
- :mod:`_errortools._logger_shell.prelude` - :class:`EasterEgg`,
  :class:`HistoryHook`, and the module-level ``easteregg`` instance
- :mod:`_errortools._logger_shell`         - public API
  (:func:`start_shell`, :func:`build_namespace`, :data:`BANNER`)

Example
-------
::

    $ logger shell
    errortools Logger Shell REPL 3.13.0 ... on win32
    Pre-imported shortcuts: info, debug, error, warning, critical, trace,
    success, exception, catch
    ...
    >>> logger.info("hello from the shell")
    >>> easteregg()
"""

from __future__ import annotations

import code
import logging
import sys
from typing import Any, Mapping, Union

# Note: the ``logger`` import is kept as the *bare* name (not aliased)
# because ``testing/test_logger_shell.py`` patches
# ``_errortools._logger_shell.logger`` to swap the singleton for
# tests.  Do not rename this import.
from _errortools.logging import (
    BaseLogger,
    CallableSink,
    FileSink,
    Level,
    LEVELS,
    Record,
    StreamSink,
    logger,
)

from .banner import TEMPLATE, build_banner
from .prelude import EasterEgg, HistoryHook, easteregg

__all__ = [
    "BANNER",
    "EasterEgg",
    "HistoryHook",
    "TEMPLATE",
    "banner",
    "build_banner",
    "build_namespace",
    "easteregg",
    "start_shell",
]


# ---------------------------------------------------------------------------
# Public namespace builder
# ---------------------------------------------------------------------------


def build_namespace(
    extra: Union[Mapping[str, Any], None] = None,
) -> dict[str, Any]:
    """Return the dict of names that the REPL exposes by default.

    The result is a fresh dict on every call, so callers can mutate
    it freely without affecting subsequent REPL sessions.

    Args:
        extra: Optional mapping of additional names to inject into
            the namespace.  Existing keys are not overwritten.

    Returns:
        A ``dict[str, Any]`` ready to be passed to
        :func:`code.interact` as the ``local`` kwarg.
    """
    namespace: dict[str, Any] = {
        # Logger singleton + level methods
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
        # easter egg
        "easteregg": easteregg,
    }
    if extra:
        for key, value in extra.items():
            namespace.setdefault(key, value)
    return namespace


# ---------------------------------------------------------------------------
# Pre-rendered banner (importable for tests / docs)
# ---------------------------------------------------------------------------

BANNER: str = build_banner()
"""The default REPL banner, rendered once at import time.

If you need a freshly-rendered banner (e.g. with an updated
``errortools.__version__``), call :func:`build_banner` directly."""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def start_shell(
    banner: Union[str, None] = None,
    namespace: Union[Mapping[str, Any], None] = None,
    exitmsg: str = "",
    install_history_hook: bool = True,
) -> None:
    """Launch an interactive Python REPL with logger helpers in scope.

    Args:
        banner: Banner string.  Defaults to :data:`BANNER`.  Pass
            ``""`` for a silent REPL, or your own string for a
            customised one.
        namespace: Pre-populated names.  Defaults to the result of
            :func:`build_namespace`.  Pass your own dict to add or
            remove names.
        exitmsg: Message printed on exit.  Empty by default; matches
            the vanilla :func:`code.interact` behaviour.
        install_history_hook: When ``True`` (the default), install
            :class:`HistoryHook` so that ``_``, ``__``, ``___`` keep
            the last three results.  Set to ``False`` to keep the
            interpreter default displayhook.

    Side Effects:
        - Replaces :data:`sys.displayhook` if
          ``install_history_hook`` is true.
        - Hands control over to :func:`code.interact`, which blocks
          until the user exits the REPL (``Ctrl-D`` / ``exit()``).
    """
    if banner is None:
        banner = BANNER
    if namespace is None:
        namespace = build_namespace()

    if install_history_hook:
        sys.displayhook = HistoryHook()

    code.interact(banner=banner, local=dict(namespace), exitmsg=exitmsg)
