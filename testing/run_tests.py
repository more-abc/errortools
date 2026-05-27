"""Run tests. Usage: run `python -m testing` or call run_tests() directly."""

import subprocess
import sys

from . import HAS_PYTEST


def run_tests():
    if not HAS_PYTEST:
        print("No pytest, skip running. You can use `pip install pytest` to install it.")
        return False
    result = subprocess.run([sys.executable, "-m", "pytest"])
    return result.returncode == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
