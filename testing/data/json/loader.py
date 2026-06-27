"""Loader helpers for data-driven tests.

Reads the JSON files shipped under ``testing/data/`` and exposes them through
a small set of typed accessor functions so test modules can simply do::

    from testing.data import loader

    cases = loader.errno_cases()
    specs = loader.single_error_specs()

If a data file is missing the loader raises a descriptive ``FileNotFoundError``
so the failure is obvious instead of crashing with a stack-trace inside a
test parametrize phase.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from . import DATA_DIR

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load(name: str) -> dict[str, Any]:
    """Load a JSON file from the data directory by name."""
    path: pathlib.Path = DATA_DIR / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Test data file not found: {path!s}. " "Expected under testing/data/.",
        )
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _walk_subclasses(root: type) -> list[type]:
    """Return every subclass (direct + indirect) of *root*."""
    out: list[type] = []
    stack: list[type] = list(root.__subclasses__())
    while stack:
        cls = stack.pop()
        out.append(cls)
        stack.extend(cls.__subclasses__())
    return out


def _resolve_type(name: str) -> type[BaseException]:
    """Resolve a fully qualified exception type name from the standard hierarchy."""
    import builtins

    # Built-in exceptions live in builtins (e.g. ValueError, KeyError).
    builtin = getattr(builtins, name, None)
    if isinstance(builtin, type) and issubclass(builtin, BaseException):
        return builtin

    # Some exceptions (KeyboardInterrupt, SystemExit, ...) live under
    # BaseException but not under Exception.  Walk the BaseException tree.
    for cls in _walk_subclasses(BaseException):
        if cls.__name__ == name:
            return cls

    raise LookupError(f"Unknown exception type: {name!r}")


def _resolve_warning(name: str) -> type[Warning]:
    """Resolve a fully qualified warning category by name.

    Warning categories live in ``builtins`` (alongside Exception types) and
    inherit from ``Warning`` (which itself inherits from ``Exception``).
    """
    import builtins

    builtin = getattr(builtins, name, None)
    if isinstance(builtin, type) and issubclass(builtin, Warning):
        return builtin

    for cls in _walk_subclasses(Warning):
        if cls.__name__ == name:
            return cls

    raise LookupError(f"Unknown warning category: {name!r}")


# ---------------------------------------------------------------------------
# Public accessors
# ---------------------------------------------------------------------------


def errno_cases() -> list[dict[str, Any]]:
    """Return valid (code, name) pairs for errno lookups."""
    data = _load("errno_codes.json")
    return list(data["cases"])


def errno_invalid_codes() -> list[int]:
    """Return numeric codes that are NOT valid errno constants."""
    data = _load("errno_codes.json")
    return list(data["invalid_codes"])


def single_error_specs() -> list[dict[str, Any]]:
    """Return single (type, message) specs."""
    return list(_load("exception_specs.json")["single_error_single_message"])


def multi_error_specs() -> list[dict[str, Any]]:
    """Return multi-error/multi-message Cartesian-product specs."""
    return list(_load("exception_specs.json")["multiple_errors_multiple_messages"])


def custom_baseerror_specs() -> list[dict[str, Any]]:
    """Return baseerror-validation specs."""
    return list(_load("exception_specs.json")["custom_baseerror_cases"])


def empty_input_specs() -> list[dict[str, Any]]:
    """Return empty-iterable specs for raises/raises_all."""
    return list(_load("exception_specs.json")["empty_inputs"])


def suppress_cases() -> list[dict[str, Any]]:
    """Return scenarios for the @suppress decorator."""
    return list(_load("suppress_cases.json")["cases"])


def ignore_suppress_cases() -> list[dict[str, Any]]:
    """Return scenarios for ignore / fast_ignore suppression."""
    return list(_load("ignore_cases.json")["suppress_cases"])


def ignore_propagate_cases() -> list[dict[str, Any]]:
    """Return scenarios for ignore propagating unrelated exceptions."""
    return list(_load("ignore_cases.json")["propagate_cases"])


def ignore_subclass_cases() -> list[dict[str, Any]]:
    """Return scenarios for ignore_subclass suppression."""
    return list(_load("ignore_cases.json")["subclass_cases"])


def ignore_subclass_propagates() -> list[dict[str, Any]]:
    """Return scenarios for ignore_subclass propagation."""
    return list(_load("ignore_cases.json")["subclass_propagates"])


def warning_single_cases() -> list[dict[str, Any]]:
    """Return single warning-category scenarios."""
    return list(_load("warning_categories.json")["single_category"])


def warning_multi_cases() -> list[dict[str, Any]]:
    """Return multi-category scenarios."""
    return list(_load("warning_categories.json")["multiple_categories"])


def warning_unrelated_cases() -> list[dict[str, Any]]:
    """Return scenarios where unrelated warnings still surface."""
    return list(_load("warning_categories.json")["unrelated_propagates"])


def warning_no_args_cases() -> list[dict[str, Any]]:
    """Return scenarios for ignore_warns() with no args."""
    return list(_load("warning_categories.json")["no_args_suppresses_all"])


def convert_cases() -> list[dict[str, Any]]:
    """Return scenarios for the @convert decorator."""
    return list(_load("convert_cases.json")["cases"])


def convert_chained_cases() -> list[dict[str, Any]]:
    """Return scenarios verifying __cause__ chaining in @convert."""
    return list(_load("convert_cases.json")["chained_cases"])


def convert_tuple_cases() -> list[dict[str, Any]]:
    """Return scenarios where source is a tuple of types."""
    return list(_load("convert_cases.json")["tuple_sources"])


def convert_custom_message_cases() -> list[dict[str, Any]]:
    """Return scenarios where a custom message overrides the source message."""
    return list(_load("convert_cases.json")["custom_message"])


def retry_success_cases() -> list[dict[str, Any]]:
    """Return scenarios where retry eventually succeeds."""
    return list(_load("retry_cases.json")["success_cases"])


def retry_exhaustion_cases() -> list[dict[str, Any]]:
    """Return scenarios where retry exhausts all attempts."""
    return list(_load("retry_cases.json")["exhaustion_cases"])


def retry_unrelated_cases() -> list[dict[str, Any]]:
    """Return scenarios where unrelated exceptions propagate."""
    return list(_load("retry_cases.json")["unrelated_propagates"])


def retry_exception_types() -> list[dict[str, Any]]:
    """Return scenarios describing which exception types trigger retry."""
    return list(_load("retry_cases.json")["exception_types"])


def normalization_valid_cases() -> list[dict[str, Any]]:
    """Return valid input cases for NonBlankErrorMsg."""
    return list(_load("message_normalization.json")["valid_inputs"])


def normalization_blank_cases() -> list[dict[str, Any]]:
    """Return blank inputs that should be rejected by NonBlankErrorMsg."""
    return list(_load("message_normalization.json")["blank_inputs"])


def normalization_non_string_cases() -> list[dict[str, Any]]:
    """Return non-string inputs that should be rejected by NonBlankErrorMsg."""
    return list(_load("message_normalization.json")["non_string_inputs"])


# ---------------------------------------------------------------------------
# Exception-construction helper used by tests
# ---------------------------------------------------------------------------


def make_exception(spec: str) -> BaseException:
    """Build an exception instance from a textual spec.

    ``spec`` follows the same format used in the JSON data, e.g.::

        "KeyError('missing')"
        "ValueError('bad value')"
        "RuntimeError('oops')"
    """
    import re

    match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$", spec)
    if not match:
        raise ValueError(f"Bad exception spec: {spec!r}")
    name, message = match.group(1), match.group(2)
    return _resolve_type(name)(message)


__all__ = [
    "DATA_DIR",
    "errno_cases",
    "errno_invalid_codes",
    "single_error_specs",
    "multi_error_specs",
    "custom_baseerror_specs",
    "empty_input_specs",
    "suppress_cases",
    "ignore_suppress_cases",
    "ignore_propagate_cases",
    "ignore_subclass_cases",
    "ignore_subclass_propagates",
    "warning_single_cases",
    "warning_multi_cases",
    "warning_unrelated_cases",
    "warning_no_args_cases",
    "convert_cases",
    "convert_chained_cases",
    "convert_tuple_cases",
    "convert_custom_message_cases",
    "retry_success_cases",
    "retry_exhaustion_cases",
    "retry_unrelated_cases",
    "retry_exception_types",
    "normalization_valid_cases",
    "normalization_blank_cases",
    "normalization_non_string_cases",
    "make_exception",
    "_resolve_type",
    "_resolve_warning",
    "_walk_subclasses",
]
