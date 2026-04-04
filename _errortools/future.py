"""Futures classes and functions."""

from typing import TypeAlias, Optional

_ExcType: TypeAlias = type[BaseException]


class super_fast_ignore:
    """Ultra-lightweight context manager to suppress exceptions."""

    __slots__ = ("excs",)

    def __init__(self, *excs: _ExcType) -> None:
        self.excs = excs

    def __enter__(self) -> None:
        return

    def __exit__(self, typ: Optional[_ExcType], _, __) -> bool:
        if typ is None:
            return False
        excs = self.excs
        return issubclass(typ, excs)
