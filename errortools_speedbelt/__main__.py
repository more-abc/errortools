"""Command-line interface for :mod:`errortools_speedbelt`.

Run this module as a script (for example ``python -m errortools_speedbelt``)
to inspect the C-extension support status of the speedbelt package and to
print version information.

The default action is a probe of the two C extensions shipped with
:mod:`errortools_speedbelt` — :func:`errortools_speedbelt._speedup` and
:func:`errortools_speedbelt._ignore_speed`.  The probe delegates to the
cached :data:`errortools_speedbelt.support_c_ext.ERRORTOOLS_SUPPORTS_C_EXTENSIONS`
constant so the result is consistent with what the rest of the package
sees at import time.

Exit codes
----------
``0``
    C extensions are available on this interpreter.
``1``
    C extensions are **not** available; the package will fall back to
    the pure-Python implementation at runtime.
``2``
    An unexpected error occurred while running the CLI.

Examples
--------
Inspect the speedbelt environment::

    $ python -m errortools_speedbelt
    errortools_speedbelt 0.1.3 (0.1.3)
    C extension support: True

Show only the version::

    $ python -m errortools_speedbelt --version
    errortools_speedbelt 0.1.3

Show a detailed environment report and the reason the detector chose
its verdict::

    $ python -m errortools_speedbelt --info --verbose
"""

from __future__ import annotations

import argparse
import sys
from typing import Final, Sequence, Union

from . import __version__, __version_info__
from .support_c_ext import ERRORTOOLS_SUPPORTS_C_EXTENSIONS

_PROG: Final[str] = "python -m errortools_speedbelt"
_DESCRIPTION: Final[str] = "Inspect the errortools_speedbelt C-extension support and report " "version information."


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Build the :mod:`argparse` parser for the speedbelt CLI.

    The ``color=True`` keyword is only available from Python 3.14, so it
    is supplied conditionally to remain compatible with the project's
    ``requires-python = ">=3.8"`` baseline.
    """
    if sys.version_info >= (3, 14):
        parser = argparse.ArgumentParser(prog=_PROG, description=_DESCRIPTION, color=True)
    else:
        parser = argparse.ArgumentParser(prog=_PROG, description=_DESCRIPTION)

    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Print the errortools_speedbelt version and exit.",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help=(
            "Probe the C extensions and report their availability. "
            "This is the default action when no other flag is supplied."
        ),
    )
    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Print a detailed environment report and exit.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print the per-check breakdown used by the detector.",
    )
    return parser


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def _show_version() -> None:
    """Print the speedbelt package version in the project's canonical shape."""
    print(f"errortools_speedbelt {__version__} ({__version_info__})")


def _diagnostics(verbose: bool) -> None:
    """Print the per-check breakdown used by :func:`_detect_c_ext_support`.

    The helpers live in :mod:`errortools_speedbelt.support_c_ext` and are
    prefixed with an underscore; importing them inside this function keeps
    the module import surface clean for callers that only want to look at
    the cached boolean verdict.
    """
    if not verbose:
        return
    # Local import keeps the helpers private to this CLI while still
    # surfacing them for diagnostics.
    from .support_c_ext import (
        _has_c_compiler,
        _has_ctypes,
        _is_windows_store_python,
        _looks_like_static_analysis_run,
    )

    print("  detector breakdown:")
    print(f"    Windows Store Python: {_is_windows_store_python()}")
    print(f"    ctypes available:     {_has_ctypes()}")
    print(f"    static-analysis run:  {_looks_like_static_analysis_run()}")
    print(f"    C compiler on PATH:   {_has_c_compiler()}")


def _show_check(verbose: bool = False) -> int:
    """Print whether the C extensions can be loaded.

    Returns ``0`` when :data:`ERRORTOOLS_SUPPORTS_C_EXTENSIONS` is ``True``
    and ``1`` otherwise.
    """
    print(f"errortools_speedbelt {__version__}")
    if ERRORTOOLS_SUPPORTS_C_EXTENSIONS:
        print("C speedup: available")
    else:
        print("C speedup: not available (pure Python fallback)")
    _diagnostics(verbose)
    return 0 if ERRORTOOLS_SUPPORTS_C_EXTENSIONS else 1


def _show_info(verbose: bool = False) -> int:
    """Print a multi-line summary of the speedbelt environment.

    The exit code reflects the C-extension availability verdict so the
    flag can be wired into shell scripts in the same way as ``--check``.
    """
    print(f"errortools_speedbelt {__version__}")
    print(f"  C extension support: {ERRORTOOLS_SUPPORTS_C_EXTENSIONS}")
    print(f"  Version (info):      {__version_info__}")
    _diagnostics(verbose)
    return 0 if ERRORTOOLS_SUPPORTS_C_EXTENSIONS else 1


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def _dispatch(args: argparse.Namespace) -> int:
    """Run the action selected by the parsed CLI arguments.

    When no flag is supplied the function falls back to :func:`_show_check`
    so ``python -m errortools_speedbelt`` keeps the original "probe the
    extensions" behaviour.
    """
    if args.version:
        _show_version()
        return 0
    if args.info:
        return _show_info(verbose=args.verbose)
    if args.check:
        return _show_check(verbose=args.verbose)
    # No flag → default to --check.
    return _show_check(verbose=args.verbose)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Union[Sequence[str], None] = None) -> int:
    """Module entry point for :mod:`errortools_speedbelt`.

    Args:
        argv: Optional sequence of command-line arguments.  When ``None``
            (the default) the arguments are read from :data:`sys.argv`.

    Returns:
        A process exit code — see the module docstring for the mapping.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except Exception as exc:  # pragma: no cover - defensive
        # A failure inside the CLI must never propagate as an
        # uncaught traceback; surface it on stderr with a non-zero
        # exit code instead.
        sys.stderr.write(f"errortools_speedbelt: unexpected error: {exc!r}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
