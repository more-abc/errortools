"""Public command-line interface for errortools.

This module provides the entry points used by the ``errortools`` and
``logger`` console scripts declared in :file:`pyproject.toml`.

Two command families share this dispatcher:

* ``errortools``  - metadata, version and developer tooling flags.
* ``logger``      - log emission and an interactive debug shell.

The correct family is selected once, at module import time, by
inspecting :data:`sys.argv` rather than the parent process, so the
detection survives ``python -m _errortools`` invocations and works on
all supported platforms.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Sequence
from typing import Final, Union

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

# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------


def _detect_mode(argv0: Union[str, None] = None) -> str:
    """Return the CLI family inferred from ``argv0``.

    The detection uses the *basename* of the executable/script rather
    than a substring test, so paths such as ``/usr/bin/logger`` (a
    real Unix utility) or ``my_logger_tool`` do not accidentally
    trigger the logger dispatcher.
    """
    raw = argv0 if argv0 is not None else sys.argv[0]
    basename = os.path.basename(raw).lower()
    # Strip common suffixes so ``logger-script.py`` / ``logger.exe``
    # also collapse to the bare command name.
    for suffix in (".exe", ".py", ".pyw", ".pyz", ".sh"):
        if basename.endswith(suffix):
            basename = basename[: -len(suffix)]
    return "logger" if basename == "logger" else "errortools"


# ``sys.argv[0]`` is stable for the lifetime of the process; cache
# the resolved mode to avoid recomputing the basename on every call.
_CLI_MODE: Final[str] = _detect_mode()


def _make_parser(prog: str, description: str) -> argparse.ArgumentParser:
    """Build an `ArgumentParser`, enabling colour on 3.14+.

    Colour output is only supported by :mod:`argparse` from Python 3.14,
    so the ``color`` kwarg is conditionally supplied to stay compatible
    with the project's ``requires-python = ">=3.8"``.
    """
    if sys.version_info >= (3, 14):
        return argparse.ArgumentParser(prog=prog, description=description, color=True)
    return argparse.ArgumentParser(prog=prog, description=description)


# ---------------------------------------------------------------------------
# errortools family
# ---------------------------------------------------------------------------


def _build_errortools_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the ``errortools`` command."""
    parser = _make_parser(prog="errortools", description=__description__)
    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("-c", "--copyrights", action="store_true", help="Show copyright information")
    parser.add_argument("-a", "--author", action="store_true", help="Show author name")
    parser.add_argument("-e", "--email", action="store_true", help="Show author email")
    parser.add_argument("-l", "--license", action="store_true", help="Show license type")
    parser.add_argument("-u", "--url", action="store_true", help="Show project URL")
    parser.add_argument("-i", "--info", action="store_true", help="Show all package information")
    parser.add_argument("--run-tests", action="store_true", help="Run tests using pytest")
    return parser


# ---------------------------------------------------------------------------
# logger family
# ---------------------------------------------------------------------------


def _build_logger_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the ``logger`` command."""
    parser = _make_parser(
        prog="logger",
        description="Logger CLI - emit log records or open an interactive REPL.",
    )
    subparsers = parser.add_subparsers(
        dest="subcmd",
        required=True,
        title="available subcommands",
        metavar="{emit,shell}",
        help="run `logger {subcommand} -h` to view subcommand details",
    )

    parser_emit = subparsers.add_parser(
        "emit",
        help="Emit a single log message to stdout or stderr",
        description="Emit a single log message to stdout or stderr.",
    )
    parser_emit.add_argument("message", help="Text content of the log record")
    parser_emit.add_argument(
        "--level",
        "-l",
        default="info",
        choices=["trace", "debug", "info", "success", "warning", "error", "critical"],
        help="Log severity level (default: info)",
    )
    parser_emit.add_argument(
        "--output",
        "-o",
        choices=["stderr", "stdout"],
        default="stderr",
        help="Target output stream (default: stderr)",
    )

    subparsers.add_parser(
        "shell",
        help="Launch an interactive logger REPL debug shell",
        description="Launch an interactive logger REPL debug shell.",
    )
    return parser


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args(args: Union[Sequence[str], None] = None) -> argparse.Namespace:
    """Parse command-line arguments for the active CLI family."""
    if _CLI_MODE == "logger":
        return _build_logger_parser().parse_args(args)
    return _build_errortools_parser().parse_args(args)


# ---------------------------------------------------------------------------
# Flag dispatch (errortools family)
# ---------------------------------------------------------------------------


def _show_version() -> None:
    """Print ``errortools <version>`` in the same shape as ``--info``."""
    print(f"errortools {__version__}")


def _show_copyrights() -> None:
    """Print the project's copyright line."""
    print(__copyright__)


def _show_author() -> None:
    """Print the author's name."""
    print(f"Author: {__author__}")


def _show_email() -> None:
    """Print the author's contact email."""
    print(f"Email: {__author_email__}")


def _show_license() -> None:
    """Print the project's licence."""
    print(f"License: {__license__}")


def _show_url() -> None:
    """Print the project's homepage URL."""
    print(f"URL: {__url__}")


def _run_tests() -> None:
    """Delegate to :func:`testing.run_tests.run_tests` with a helpful message on failure."""
    try:
        from testing.run_tests import run_tests
    except ImportError as exc:  # pragma: no cover - environment dependent
        sys.stderr.write(
            "errortools: cannot import `testing` package " f"({exc!r}). Install the project with its test extras.\n"
        )
        sys.exit(2)
    run_tests()


_FLAG_ACTIONS: Final[dict[str, Callable[[], None]]] = {
    "version": _show_version,
    "copyrights": _show_copyrights,
    "author": _show_author,
    "email": _show_email,
    "license": _show_license,
    "url": _show_url,
    "run_tests": _run_tests,
    "info": _print_info,
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _dispatch_logger(args: argparse.Namespace) -> None:
    """Route a parsed ``logger`` namespace to its subcommand handler."""
    if args.subcmd == "shell":
        from _errortools._logger_shell import start_shell

        start_shell()
        return
    # ``subcmd`` is constrained to {"emit", "shell"} by argparse, but
    # keep a defensive fallback in case ``required=True`` is ever loosened.
    if args.subcmd == "emit":
        _cmd_log(args.message, args.level, args.output)
        return
    sys.stderr.write(f"errortools: unknown logger subcommand {args.subcmd!r}\n")
    sys.exit(2)


def _dispatch_errortools(args: argparse.Namespace) -> None:
    """Run the action selected by a flag on the ``errortools`` family."""
    for flag, action in _FLAG_ACTIONS.items():
        if getattr(args, flag, False):
            action()
            return
    # No flag supplied → render the help screen.
    _build_errortools_parser().parse_args(["--help"])


def main(argv: Union[Sequence[str], None] = None) -> None:
    """Module entry point dispatched to the active CLI family."""
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    if _CLI_MODE == "logger":
        _dispatch_logger(args)
        return

    _dispatch_errortools(args)


if __name__ == "__main__":
    main()
