"""Run tests. Usage: run `python tests/run_tests.py` or call run_tests() directly."""

import subprocess
import sys

from . import HAS_PYTEST


def run_tests():
    result = subprocess.run([sys.executable, "-m", "pytest"])
    if not HAS_PYTEST:
        print("No pytest, skip runing. You can use `pip install pytest` to let it run")
        return False
    return result.returncode == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
