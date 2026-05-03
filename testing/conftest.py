"""Shared fixtures and helpers for the errortools test suite."""

import sys

# ---------------------------------------------------------------------------
# Ensure the project root (contains both `errortools/` and `_errortools/`)
# is on sys.path so that `import errortools` and `from _errortools import …`
# both resolve correctly when running pytest from any directory.
# ---------------------------------------------------------------------------
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
