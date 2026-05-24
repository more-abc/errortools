"""Public command-line interface."""

import argparse
import sys
from collections.abc import Callable

from _errortools._cli import _cmd_log, _print_info

from _errortools.metadata import (
    __description__,
    __copyright__,
    __author__,
    __author_email__,
    __license__,
    __url__,
)
from _errortools.version import __version__


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    is_logger = "logger" in sys.argv[0]

    if is_logger:
        parser = argparse.ArgumentParser(
            prog="logger",
            description="Logger CLI - Emit log messages from command line",
        )
        parser.add_argument("message", help="Log message")
        parser.add_argument(
            "--level",
            "-l",
            default="info",
            choices=[
                "trace",
                "debug",
                "info",
                "success",
                "warning",
                "error",
                "critical",
            ],
        )
        parser.add_argument("--output", "-o", choices=["stderr", "stdout"], default="stderr")
        return parser.parse_args(args)

    prog = "errortools"
    desc = __description__

    if sys.version_info >= (3, 14):
        parser = argparse.ArgumentParser(description=desc, prog=prog, color=True)
    else:
        parser = argparse.ArgumentParser(description=desc, prog=prog)

    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("-c", "--copyrights", action="store_true", help="Show copyright information")
    parser.add_argument("-a", "--author", action="store_true", help="Show author name")
    parser.add_argument("-e", "--email", action="store_true", help="Show author email")
    parser.add_argument("-l", "--license", action="store_true", help="Show license type")
    parser.add_argument("-u", "--url", action="store_true", help="Show project URL")
    parser.add_argument("-i", "--info", action="store_true", help="Show all package information")
    parser.add_argument("--run-tests", action="store_true", help="Run tests using pytest")

    return parser.parse_args(args)


def _run_tests() -> None:
    from testing.run_tests import run_tests

    run_tests()


_FLAG_ACTIONS: dict[str, Callable[[], None]] = {
    "version": lambda: print(f"v{__version__}"),
    "copyrights": lambda: print(__copyright__),
    "author": lambda: print(f"Author: {__author__}"),
    "email": lambda: print(f"Email: {__author_email__}"),
    "license": lambda: print(f"License: {__license__}"),
    "url": lambda: print(f"URL: {__url__}"),
    "run_tests": _run_tests,
    "info": _print_info,
}


def main() -> None:
    args = parse_args(sys.argv[1:])

    if "logger" in sys.argv[0]:
        _cmd_log(args.message, args.level, args.output)
        return

    for flag, action in _FLAG_ACTIONS.items():
        if getattr(args, flag, False):
            action()
            return

    parse_args(["--help"])


if __name__ == "__main__":
    main()
