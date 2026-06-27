# reproduce_issue_69.py
"""Reproduce #69: Import `TracebackType` and `FrameType` from `types` module in `_errortools/typing.py` to speedup."""

from types import TracebackType as typesTracebackType
from types import FrameType as typesFrameType

from errortools import TracebackType, FrameType

assert TracebackType is typesTracebackType
assert typesFrameType is FrameType
