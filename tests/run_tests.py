"""Run tests. Usage: run `python tests/run_tests.py`"""

import subprocess
import sys

subprocess.run([sys.executable, "-m", "pytest"])