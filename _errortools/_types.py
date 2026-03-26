import sys
import types

# Acquire the internal interpreter types for traceback objects and frame objects.

# This module uses a raised exception to safely obtain the runtime types
# of traceback and frame objects, for compatibility with older Python versions
# where these types are not easily importable from the types module.
if sys.version_info >= (3, 7):
    # No docstrings are provided for standard library versions.
    TracebackType = types.TracebackType
    FrameType = types.FrameType
else:
    try:
        raise TypeError
    except TypeError as exc:
        TracebackType = type(exc.__traceback__)
        """The type of traceback objects returned by exception.__traceback__."""

        FrameType = type(exc.__traceback__.tb_frame)  # type: ignore
        """The type of frame objects representing an execution frame in the call stack."""
