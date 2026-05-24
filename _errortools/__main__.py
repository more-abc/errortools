"""Private debug CLI — run via `python -m _errortools`."""

import argparse
import shutil
import sys
from pathlib import Path

from _errortools.version import __version__


def _parse_args(args: list[str] | None = None) -> argparse.Namespace:
    desc = "errortools internal debug tools"

    if sys.version_info >= (3, 14):
        parser = argparse.ArgumentParser(prog="_errortools", description=desc, color=True)
    else:
        parser = argparse.ArgumentParser(prog="_errortools", description=desc)

    parser.add_argument("--debug", action="store_true", help="Show debug/environment information")
    parser.add_argument(
        "--reset", action="store_true", help="Clear all cached data (__pycache__, htmlcov, .pytest_cache, .mypy_cache)"
    )
    parser.add_argument("--check", action="store_true", help="Verify installation and dependencies")

    return parser.parse_args(args)


def _debug_info() -> None:
    import platform

    print(f"errortools v{__version__}")
    print(f"  Python:    {sys.version}")
    print(f"  Platform:  {platform.platform()}")
    print(f"  Arch:      {platform.machine()}")
    print(f"  Prefix:    {sys.prefix}")
    print(f"  Exec:      {sys.executable}")

    try:
        __import__("_errortools._speedup")
        print("  C speedup: available")
    except ImportError:
        print("  C speedup: not available (pure Python fallback)")


def _reset_cache() -> None:
    root = Path(__file__).resolve().parent.parent
    count = 0

    for d in root.rglob("__pycache__"):
        if d.is_dir():
            shutil.rmtree(d)
            count += 1

    for name in ["htmlcov", ".pytest_cache", ".mypy_cache"]:
        d = root / name
        if d.is_dir():
            shutil.rmtree(d)
            count += 1

    print(f"Reset complete. Cleared {count} cached directories.")


def _check_install() -> None:
    checks: list[tuple[str, bool]] = [("errortools importable", True)]

    for label, import_path in [
        ("C extension (_speedup)", "_errortools._speedup"),
        ("pytest", "pytest"),
        ("logging module", "_errortools.logging"),
        ("future module", "_errortools.future"),
        ("typing_extensions", "typing_extensions"),
    ]:
        try:
            __import__(import_path)
            checks.append((label, True))
        except ImportError:
            checks.append((label, False))

    for name, ok in checks:
        status = "OK" if ok else "MISSING"
        print(f"  [{status:>7s}] {name}")

    print()
    if all(ok for _, ok in checks):
        print("All checks passed.")
    else:
        print("Some checks failed. Install missing dependencies.")


_FLAG_ACTIONS = {
    "debug": _debug_info,
    "reset": _reset_cache,
    "check": _check_install,
}


def main() -> None:
    args = _parse_args(sys.argv[1:])

    for flag, action in _FLAG_ACTIONS.items():
        if getattr(args, flag, False):
            action()
            return

    _parse_args(["--help"])


if __name__ == "__main__":
    main()
