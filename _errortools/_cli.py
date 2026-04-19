import sys

from _errortools.metadata import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __url__,
)
from _errortools.version import __version__


def _cmd_log(message: str, level: str, output: str) -> None:
    """Emit a single log message via the errortools logger."""
    from .logging import BaseLogger
    from .logging.level import get_level

    stream = sys.stdout if output == "stdout" else sys.stderr
    log = BaseLogger(name="errortools-cli")
    log.set_level("TRACE")
    log.add(stream, level=level, colorize=None)
    log.log(get_level(level), message)


def _print_info() -> None:
    """Print a summary of all package metadata."""
    print(f"errortools v{__version__}")
    print(f"  {__description__}")
    print(f"  Author:    {__author__} <{__author_email__}>")
    print(f"  License:   {__license__}")
    print(f"  URL:       {__url__}")
    print(f"  Copyright: {__copyright__}")
