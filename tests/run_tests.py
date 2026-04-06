"""Run tests. Usage: run `python tests/run_tests.py`"""

import subprocess
import sys


def run_tests():
    """Run pytest tests."""
    subprocess.run([sys.executable, "-m", "pytest"])


if __name__ == "__main__":
    run_tests()
