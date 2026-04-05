# Acquire the internal interpreter types for traceback objects and frame objects.
# Uses a raised exception to safely obtain the runtime types without importing
# from the types module.
# Acquire traceback and frame types at runtime for compatibility.
try:
    raise TypeError
except TypeError as exc:
    TracebackType = type(exc.__traceback__)
    """The type of traceback objects returned by `exception.__traceback__`."""
    FrameType = type(exc.__traceback__.tb_frame)  # type: ignore
    """The type of frame objects representing an execution frame in the call stack."""
