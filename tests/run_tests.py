"""Run tests. Usage: run `python tests/run_tests.py` or call run_tests() directly."""

import subprocess
import sys


def run_tests():
    result = subprocess.run([sys.executable, "-m", "pytest"])
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
