"""Module-level singleton logger — ``from errortools.logging import logger``."""

from __future__ import annotations

import sys

from .base import BaseLogger
from .level import Level
from .sink import StreamSink

# Create the default global logger.
# It ships with a single stderr sink at DEBUG level (mirrors loguru's default).
logger: BaseLogger = BaseLogger(name="errortools")
logger.add(sys.stderr, level=Level.DEBUG, colorize=None)
