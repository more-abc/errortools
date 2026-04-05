"""Command-line interface."""

import argparse
import sys

from ._metadata import (
    __description__,
    __copyright__,
    __author__,
    __author_email__,
    __license__,
    __url__,
)
from ._version import __version__


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__description__, color=True)

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

    return parser.parse_args(args)


def _print_info() -> None:
    """Print a summary of all package metadata."""
    print(f"errortools v{__version__}")
    print(f"  {__description__}")
    print(f"  Author:    {__author__} <{__author_email__}>")
    print(f"  License:   {__license__}")
    print(f"  URL:       {__url__}")
    print(f"  Copyright: {__copyright__}")


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

    elif args.info:
        _print_info()

    else:
        _print_info()
