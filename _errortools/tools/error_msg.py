"""Error messages."""

from typing import TypeAlias

# Good!
ErrorMsg: TypeAlias = str

IgnoreNotExceptionSubclassMessage: ErrorMsg = "You can't ignore Error like SystemExit or KeyboardInterrupt!"

ErrorAttrableRaiseNotImplementedErrorMessage: ErrorMsg = (
    f"Subclasses of ErrorAttrable must implement __errorattr__(self, name: str).\n"
    "See `collections.abc` for similar abstract method requirements (e.g., __iter__ for Iterable)."
)