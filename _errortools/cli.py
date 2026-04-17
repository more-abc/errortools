"""Command-line interface."""

import argparse
import sys

from _errortools._cli import _cmd_log, _print_info

from .metadata import (
    __description__,
    __copyright__,
    __author__,
    __author_email__,
    __license__,
    __url__,
)
from .version import __version__


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    if sys.version_info >= (3, 14):
        parser = argparse.ArgumentParser(description=__description__, color=True)
    else:
        parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument(
        "-v", "--version", action="store_true", help="Show version and exit"
    )

    parser.add_argument(
        "-c", "--copyrights", action="store_true", help="Show copyright information"
    )

    parser.add_argument("-a", "--author", action="store_true", help="Show author name")

    parser.add_argument("-e", "--email", action="store_true", help="Show author email")

    parser.add_argument(
        "-l", "--license", action="store_true", help="Show license type"
    )

    parser.add_argument("-u", "--url", action="store_true", help="Show project URL")

    parser.add_argument(
        "-i", "--info", action="store_true", help="Show all package information"
    )

    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run tests for errortools module. (Using pytest)",
    )

    subparsers = parser.add_subparsers(dest="subcommand")

    log_parser = subparsers.add_parser(
        "log",
        help="Emit a log message from the command line",
    )
    log_parser.add_argument(
        "message",
        help="The message to log",
    )
    log_parser.add_argument(
        "--level",
        "-l",
        default="info",
        choices=["trace", "debug", "info", "success", "warning", "error", "critical"],
        help="Log level (default: info)",
    )
    log_parser.add_argument(
        "--output",
        "-o",
        choices=["stderr", "stdout"],
        default="stderr",
        help="Output stream (default: stderr)",
    )

    return parser.parse_args(args)


def log_main() -> None:
    """Logging main CLI entry point."""
    args = parse_args(sys.argv[1:])

    if args.subcommand == "log":
        _cmd_log(args.message, args.level, args.output)


def main() -> None:
    """Main CLI entry point."""
    args = parse_args(sys.argv[1:])

    if args.version:
        print(f"v{__version__}")

    elif args.copyrights:
        print(__copyright__)

    elif args.author:
        print(f"Author: {__author__}")

    elif args.email:
        print(f"Email: {__author_email__}")

    elif args.license:
        print(f"License: {__license__}")

    elif args.url:
        print(f"URL: {__url__}")

    elif args.run_tests:
        from tests.run_tests import run_tests

        run_tests()

    elif args.info:
        _print_info()

    else:
        parse_args(["--help"])


if __name__ == "__main__":
    main()
