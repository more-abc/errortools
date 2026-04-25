"""Logging for errortools — loguru-inspired structured logger.

Quick start::

    from errortools.logging import logger

    logger.info("Hello, {}!", "world")
    logger.warning("Disk at {pct}%", pct=90)

    # Add a file sink
    logger.add("app.log", rotation=10_000_000, retention=5)

    # Bind context
    req_log = logger.bind(request_id="abc-123")
    req_log.debug("Request received")

    # Catch exceptions
    with logger.catch():
        int("oops")
"""

from _errortools.logging import *

__all__ = [
    # Core objects
    "logger",
    "BaseLogger",
    # Level helpers
    "Level",
    "get_level",
    "LEVELS",
    # Record
    "Record",
    # Sinks
    "BaseSink",
    "StreamSink",
    "FileSink",
    "CallableSink",
]
