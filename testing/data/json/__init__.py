"""Test data for errortools.

This package contains structured test data used by data-driven tests.
Files in this directory are loaded at test time to validate the public API
across many input combinations.

Data files
----------
- ``errno_codes.json``        — list of (code, name) pairs for ``get_errno_name``
- ``exception_specs.json``    — (type, message, baseerror) tuples for ``raises``
- ``suppress_cases.json``     — scenarios for the ``@suppress`` decorator
- ``ignore_cases.json``       — scenarios for ``ignore`` / ``fast_ignore``
- ``warning_categories.json`` — warning category names for ``ignore_warns``
- ``convert_cases.json``      — source/raised pairs for the ``@convert`` decorator
- ``retry_cases.json``        — (times, fails_before_success) for ``@retry``
- ``message_normalization.json`` — whitespace edge cases for ``NonBlankErrorMsg``
"""

__all__ = [
    "DATA_DIR",
]

import pathlib

DATA_DIR = pathlib.Path(__file__).resolve().parent
"""Absolute path to this data directory."""
