import sys

from . import run_doctests

if __name__ == "__main__":
    success = run_doctests(verbose=True)
    sys.exit(0 if success else 1)
