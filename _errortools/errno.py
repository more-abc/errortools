import errno


def get_errno_name(code: int) -> str | None:
    """Get the symbolic name for an errno code.

    Args:
        code: The errno code (e.g., 2 for ENOENT)

    Returns:
        The errno name (e.g., "ENOENT") or None if not found
    """
    for name in dir(errno):
        if name.isupper() and getattr(errno, name) == code:
            return name
    return None


def get_errno_message(code: int) -> str:
    """Get the error message for an errno code.

    Args:
        code: The errno code

    Returns:
        The error message string
    """
    try:
        return errno.errorcode.get(code, f"Unknown error {code}")
    except (AttributeError, KeyError):
        return f"Unknown error {code}"


def get_all_errno_codes() -> dict[str, int]:
    """Get a mapping of all errno names to their numeric codes.

    Returns:
        Dictionary mapping errno names to their numeric values
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
    """Check if a code is a valid errno constant.

    Args:
        code: The code to check

    Returns:
        True if the code is a valid errno, False otherwise
    """
    return get_errno_name(code) is not None


def strerror(code: int) -> str:
    """Get human-readable error message for errno code.

    Args:
        code: The errno code

    Returns:
        Error message string
    """
    import os

    try:
        return os.strerror(code)
    except (ValueError, OSError):
        return f"Unknown error {code}"
