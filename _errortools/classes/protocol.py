import sys
from types import GenericAlias
from typing import Any, Callable, Protocol, Self, Sequence, TypeVar, overload, runtime_checkable

__all__ = [
    "ExceptionLike",
    "SystemExitLike",
    "StopIterationLike",
    "OSErrorLike",
    "AttributeErrorLike",
    "NameErrorLike",
    "ImportErrorLike",
    "SyntaxErrorLike",
    "BlockingIOErrorLike",
    "UnicodeDecodeErrorLike",
    "UnicodeEncodeErrorLike",
    "UnicodeTranslateErrorLike",
    "BaseExceptionGroupLike",
    "ExceptionGroupLike",
    "GroupErrorsLike",
]


@runtime_checkable
class ExceptionLike(Protocol):
    """.. versionadded:: 3.2"""

    args: tuple[Any, ...]
    # __cause__: BaseException | None
    # __context__: BaseException | None
    # __suppress_context__: bool
    # __traceback__: TracebackType | None

    # if sys.version_info >= (3, 11):
    #     __notes__: list[str]


@runtime_checkable
class SystemExitLike(Protocol):
    """.. versionadded:: 3.2"""

    code: int | str | None


@runtime_checkable
class StopIterationLike(Protocol):
    """.. versionadded:: 3.2"""

    value: Any


@runtime_checkable
class OSErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    errno: int | None
    strerror: str | None
    # filename, filename2 are actually str | bytes | None
    filename: str | bytes | None
    filename2: str | bytes | None

    if sys.platform == "win32":
        winerror: int | None


if sys.version_info >= (3, 10):

    @runtime_checkable
    class AttributeErrorLike(Protocol):
        """.. versionadded:: 3.2"""

        name: str | None
        obj: Any

    @runtime_checkable
    class NameErrorLike(Protocol):
        """.. versionadded:: 3.2"""

        name: str | None

else:
    pass


@runtime_checkable
class ImportErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    def __init__(self, *args: object, name: str | None = None, path: str | None = None) -> None: ...

    name: str | None
    path: str | None
    msg: str
    if sys.version_info >= (3, 12):
        name_from: str | None


@runtime_checkable
class SyntaxErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    msg: str
    filename: str | None
    lineno: int | None
    offset: int | None
    text: str | None
    print_file_and_line: None

    if sys.version_info >= (3, 10):
        end_lineno: int | None
        end_offset: int | None


@runtime_checkable
class BlockingIOErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    characters_written: int


@runtime_checkable
class UnicodeDecodeErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    encoding: str
    object: bytes
    start: int
    end: int
    reason: str


@runtime_checkable
class UnicodeEncodeErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    encoding: str
    object: bytes
    start: int
    end: int
    reason: str


@runtime_checkable
class UnicodeTranslateErrorLike(Protocol):
    """.. versionadded:: 3.2"""

    encoding: None
    object: str
    start: int
    end: int
    reason: str


if sys.version_info >= (3, 11):
    _BaseExceptionT_co = TypeVar("_BaseExceptionT_co", bound=BaseException, covariant=True, default=BaseException)
    _BaseExceptionT = TypeVar("_BaseExceptionT", bound=BaseException)
    _ExceptionT_co = TypeVar("_ExceptionT_co", bound=Exception, covariant=True, default=Exception)
    _ExceptionT = TypeVar("_ExceptionT", bound=Exception)

    @runtime_checkable
    class BaseExceptionGroupLike(Protocol):
        """.. versionadded:: 3.2"""

        def __new__(cls, message: str, exceptions: Sequence[_BaseExceptionT_co], /) -> Self: ...
        def __init__(self, message: str, exceptions: Sequence[_BaseExceptionT_co], /) -> None: ...
        @property
        def message(self) -> str: ...
        @property
        def exceptions(self) -> tuple[_BaseExceptionT_co | BaseExceptionGroup[_BaseExceptionT_co], ...]: ...
        @overload
        def subgroup(
            self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
        ) -> ExceptionGroup[_ExceptionT] | None: ...
        @overload
        def subgroup(
            self, matcher_value: type[_BaseExceptionT] | tuple[type[_BaseExceptionT], ...], /
        ) -> BaseExceptionGroup[_BaseExceptionT] | None: ...
        @overload
        def subgroup(
            self, matcher_value: Callable[[_BaseExceptionT_co | Self], bool], /
        ) -> BaseExceptionGroup[_BaseExceptionT_co] | None: ...
        @overload
        def split(
            self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
        ) -> tuple[ExceptionGroup[_ExceptionT] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...
        @overload
        def split(
            self, matcher_value: type[_BaseExceptionT] | tuple[type[_BaseExceptionT], ...], /
        ) -> tuple[BaseExceptionGroup[_BaseExceptionT] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...
        @overload
        def split(
            self, matcher_value: Callable[[_BaseExceptionT_co | Self], bool], /
        ) -> tuple[BaseExceptionGroup[_BaseExceptionT_co] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...

        # In reality it is `NonEmptySequence`:
        @overload
        def derive(self, excs: Sequence[_ExceptionT], /) -> ExceptionGroup[_ExceptionT]: ...
        @overload
        def derive(self, excs: Sequence[_BaseExceptionT], /) -> BaseExceptionGroup[_BaseExceptionT]: ...
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

    @runtime_checkable
    class ExceptionGroupLike(Protocol):
        """.. versionadded:: 3.2"""

        def __new__(cls, message: str, exceptions: Sequence[_ExceptionT_co], /) -> Self: ...
        def __init__(self, message: str, exceptions: Sequence[_ExceptionT_co], /) -> None: ...
        @property
        def exceptions(self) -> tuple[_ExceptionT_co | ExceptionGroup[_ExceptionT_co], ...]: ...

        # We accept a narrower type, but that's OK.
        @overload
        def subgroup(
            self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
        ) -> ExceptionGroup[_ExceptionT] | None: ...
        @overload
        def subgroup(
            self, matcher_value: Callable[[_ExceptionT_co | Self], bool], /
        ) -> ExceptionGroup[_ExceptionT_co] | None: ...
        @overload
        def split(
            self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
        ) -> tuple[ExceptionGroup[_ExceptionT] | None, ExceptionGroup[_ExceptionT_co] | None]: ...
        @overload
        def split(
            self, matcher_value: Callable[[_ExceptionT_co | Self], bool], /
        ) -> tuple[ExceptionGroup[_ExceptionT_co] | None, ExceptionGroup[_ExceptionT_co] | None]: ...


@runtime_checkable
class GroupErrorsLike(Protocol):
    """.. versionadded:: 3.2"""

    def __init__(self, group_msg: str) -> None: ...

    @property
    def errors(self) -> list[Exception]: ...

    def clear(self) -> None: ...

    def raise_group(self) -> None: ...
