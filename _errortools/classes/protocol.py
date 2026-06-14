import sys
from types import GenericAlias
from typing import Any, Callable, Protocol, Self, Sequence, TypeVar, overload, runtime_checkable

__all__ = [
    "ExceptionLike",
    "SystemExitLike",
    "StopIterationLike",
    "OSErrorLike",
    "ImportErrorLike",
    "SyntaxErrorLike",
    "BlockingIOErrorLike",
    "UnicodeDecodeErrorLike",
    "UnicodeEncodeErrorLike",
    "UnicodeTranslateErrorLike",
    "GroupErrorsLike",
]

if sys.version_info >= (3, 11):
    __all__ += [
        "BaseExceptionGroupLike",
        "ExceptionGroupLike",
    ]
if sys.version_info >= (3, 10):
    __all__ += [
        "AttributeErrorLike",
        "NameErrorLike",
    ]


@runtime_checkable
class ExceptionLike(Protocol):
    """Protocol describing the common interface of all exceptions.

    Matches any `BaseException` subclass at runtime.

    .. versionadded:: 3.2
    """

    args: tuple[Any, ...]


@runtime_checkable
class SystemExitLike(ExceptionLike, Protocol):
    """Protocol for exceptions that carry an exit code.

    .. versionadded:: 3.2
    """

    code: int | str | None


@runtime_checkable
class StopIterationLike(ExceptionLike, Protocol):
    """Protocol for exceptions that signal the end of an iteration.

    .. versionadded:: 3.2
    """

    value: Any


@runtime_checkable
class OSErrorLike(ExceptionLike, Protocol):
    """Protocol for OS-level errors with errno / strerror metadata.

    .. versionadded:: 3.2
    """

    errno: int | None
    strerror: str | None
    filename: str | bytes | None
    filename2: str | bytes | None

    if sys.platform == "win32":
        winerror: int | None


if sys.version_info >= (3, 10):

    @runtime_checkable
    class AttributeErrorLike(ExceptionLike, Protocol):
        """Protocol for attribute access errors (Python 3.10+).

        .. versionadded:: 3.2
        """

        name: str | None
        obj: Any

    @runtime_checkable
    class NameErrorLike(ExceptionLike, Protocol):
        """Protocol for unbound name errors (Python 3.10+).

        .. versionadded:: 3.2
        """

        name: str | None


@runtime_checkable
class ImportErrorLike(ExceptionLike, Protocol):
    """Protocol for import failures carrying *name*, *path*, and *msg*.

    .. versionadded:: 3.2
    """

    def __init__(self, *args: object, name: str | None = None, path: str | None = None) -> None: ...

    name: str | None
    path: str | None
    msg: str
    if sys.version_info >= (3, 12):
        name_from: str | None


@runtime_checkable
class SyntaxErrorLike(ExceptionLike, Protocol):
    """Protocol for compile-time syntax errors with source location.

    .. versionadded:: 3.2
    """

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
class BlockingIOErrorLike(ExceptionLike, Protocol):
    """Protocol for non-blocking I/O errors reporting *characters_written*.

    .. versionadded:: 3.2
    """

    characters_written: int


@runtime_checkable
class UnicodeDecodeErrorLike(ExceptionLike, Protocol):
    """Protocol for decoding failures.

    .. versionadded:: 3.2
    """

    encoding: str
    object: bytes
    start: int
    end: int
    reason: str


@runtime_checkable
class UnicodeEncodeErrorLike(ExceptionLike, Protocol):
    """Protocol for encoding failures.

    .. versionadded:: 3.2
    """

    encoding: str
    object: bytes
    start: int
    end: int
    reason: str


@runtime_checkable
class UnicodeTranslateErrorLike(ExceptionLike, Protocol):
    """Protocol for translation failures.

    .. versionadded:: 3.2
    """

    encoding: None
    object: str
    start: int
    end: int
    reason: str


_BaseExceptionT_co = TypeVar("_BaseExceptionT_co", bound=BaseException, covariant=True, default=BaseException)
_BaseExceptionT = TypeVar("_BaseExceptionT", bound=BaseException)
_ExceptionT_co = TypeVar("_ExceptionT_co", bound=Exception, covariant=True, default=Exception)
_ExceptionT = TypeVar("_ExceptionT", bound=Exception)


@runtime_checkable
class BaseExceptionGroupLike(ExceptionLike, Protocol):
    """Protocol for `BaseExceptionGroup` (Python 3.11+).

    .. versionadded:: 3.2
    """

    def __new__(cls, message: str, exceptions: Sequence[_BaseExceptionT_co], /) -> Self: ...
    def __init__(self, message: str, exceptions: Sequence[_BaseExceptionT_co], /) -> None: ...
    @property
    def message(self) -> str: ...
    @property
    def exceptions(self) -> tuple[_BaseExceptionT_co | BaseExceptionGroup[_BaseExceptionT_co], ...]: ...

    @overload
    def subgroup(
        self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...],
        /) -> ExceptionGroup[_ExceptionT] | None: ...

    @overload
    def subgroup(
        self, matcher_value: type[_BaseExceptionT] | tuple[type[_BaseExceptionT], ...],
        /) -> BaseExceptionGroup[_BaseExceptionT] | None: ...

    @overload
    def subgroup(
        self, matcher_value: Callable[[_BaseExceptionT_co | Self], bool],
        /) -> BaseExceptionGroup[_BaseExceptionT_co] | None: ...

    @overload
    def split(
        self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...],
        /) -> tuple[ExceptionGroup[_ExceptionT] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...

    @overload
    def split(
        self, matcher_value: type[_BaseExceptionT] | tuple[type[_BaseExceptionT], ...],
        /) -> tuple[BaseExceptionGroup[_BaseExceptionT] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...

    @overload
    def split(
        self, matcher_value: Callable[[_BaseExceptionT_co | Self], bool],
        /) -> tuple[BaseExceptionGroup[_BaseExceptionT_co] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...

    # In reality it is `NonEmptySequence`:
    @overload
    def derive(self, excs: Sequence[_ExceptionT], /) -> ExceptionGroup[_ExceptionT]: ...
    @overload
    def derive(self, excs: Sequence[_BaseExceptionT], /) -> BaseExceptionGroup[_BaseExceptionT]: ...
    def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...


@runtime_checkable
class ExceptionGroupLike(ExceptionLike, Protocol):
    """Protocol for `ExceptionGroup` (Python 3.11+).

    .. versionadded:: 3.2
    """

    def __new__(cls, message: str, exceptions: Sequence[_ExceptionT_co], /) -> Self: ...
    def __init__(self, message: str, exceptions: Sequence[_ExceptionT_co], /) -> None: ...
    @property
    def exceptions(self) -> tuple[_ExceptionT_co | ExceptionGroup[_ExceptionT_co], ...]: ...

    # We accept a narrower type, but that's OK.
    @overload
    def subgroup(
        self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...],
        /) -> ExceptionGroup[_ExceptionT] | None: ...

    @overload
    def subgroup(
        self, matcher_value: Callable[[_ExceptionT_co | Self], bool],
        /) -> ExceptionGroup[_ExceptionT_co] | None: ...

    @overload
    def split(
        self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...],
        /) -> tuple[ExceptionGroup[_ExceptionT] | None, ExceptionGroup[_ExceptionT_co] | None]: ...

    @overload
    def split(
        self, matcher_value: Callable[[_ExceptionT_co | Self], bool],
        /) -> tuple[ExceptionGroup[_ExceptionT_co] | None, ExceptionGroup[_ExceptionT_co] | None]: ...


if sys.version_info < (3, 11):
    del BaseExceptionGroupLike
    del ExceptionGroupLike
    del _BaseExceptionT_co
    del _BaseExceptionT
    del _ExceptionT_co
    del _ExceptionT


@runtime_checkable
class GroupErrorsLike(Protocol):
    """Protocol for exception-group helpers that collect and raise grouped errors.

    .. versionadded:: 3.2
    """

    def __init__(self, group_msg: str) -> None: ...

    @property
    def errors(self) -> list[Exception]: ...

    def clear(self) -> None: ...

    def raise_group(self) -> None: ...
