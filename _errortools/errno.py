"""Lightweight utilities for errno error code inspection and handling."""

import errno


def get_errno_name(code: int) -> str | None:
    """Get the symbolic name for an errno code.

    Args:
        code: The numeric errno code (e.g., 2 for ENOENT)

    Returns:
        The symbolic errno name (e.g., "ENOENT") or None if not found
    """
    for name in dir(errno):
        if name.isupper() and getattr(errno, name) == code:
            return name
    return None


def get_errno_message(code: int) -> str:
    """Get the corresponding message description for an errno code.

    Args:
        code: The numeric errno code

    Returns:
        The message string corresponding to the errno code

    Raises:
        ValueError: If the given errno code is invalid
    """
    if not is_valid_errno(code):
        raise ValueError(f"Unknown error code: {code}")

    return errno.errorcode.get(code, f"Unknown error {code}")


def get_all_errno_codes() -> dict[str, int]:
    """Get a dictionary of all errno constant names and their numeric codes.

    Returns:
        Dictionary mapping uppercase errno names to their integer values
    """
    codes = {}
    for name in dir(errno):
        if name.isupper():
            try:
                value = getattr(errno, name)
                if isinstance(value, int):
                    codes[name] = value
            except (AttributeError, TypeError):
                pass
    return codes


def is_valid_errno(code: int) -> bool:
    """Check whether a given integer is a valid system errno code.

    Args:
        code: The numeric code to validate

    Returns:
        True if the code corresponds to a known errno constant, False otherwise
    """
    return get_errno_name(code) is not None


def strerror(code: int) -> str:
    """Get the human-readable system error message for an errno code.

    Args:
        code: The numeric errno code

    Returns:
        Human-readable error message string

    Raises:
        ValueError: If the error code is not recognized by the system
    """
    import os

    try:
        return os.strerror(code)
    except (ValueError, OSError):
        raise ValueError(f"Unknown error code: {code}")
