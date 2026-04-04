"""Command-line interface."""

import argparse
import sys
from typing import Optional

from ._metadata import __description__, __copyright__, __author__, __author_email__
from ._version import __version__


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__description__, color=True)

    parser.add_argument(
        "-v", "--version", action="store_true", help="Show version and exit"
    )

    parser.add_argument(
        "-c", "--copyrights", action="store_true", help="Show copyright information"
    )

    parser.add_argument(
        "-a", "--author", action="store_true", help="Show author name"
    )

    parser.add_argument("-e", "--email", action="store_true", help="Show author email")

    return parser.parse_args(args)


def main() -> None:
    """Main CLI entry point."""
    args = parse_args(sys.argv[1:])

    if args.version:
        print(f"v{__version__}")
        return

    elif args.copyrights:
        print(__copyright__)
        return

    elif args.author:
        print(f"Author: {__author__}")
        return

    elif args.email:
        print(f"Email: {__author_email__}")
        return
