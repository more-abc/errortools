"""Error messages."""

# NOTE: I will keep this code to maintain compatibility.
ErrorAttrableRaiseNotImplementedErrorMessage: str = (
    "Subclasses of ErrorAttrable must implement __errorattr__(self, name: str).\n"
    "See `collections.abc` for similar abstract method requirements (e.g., __iter__ for Iterable)."
)
