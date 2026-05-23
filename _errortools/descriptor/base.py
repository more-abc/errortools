from typing import Optional, NoReturn


class BaseDescriptor:
    """Base class for message descriptors.

    Provides shared ``__init__`` storage and a read-only ``__delete__``.
    Subclasses must implement ``__get__`` and ``__set__``.

    .. versionadded:: 3.1
    """

    __slots__ = ("_message",)

    def __init__(self, message: str) -> None:
        self._message = message

    def __get__(self, instance: Optional[object], owner: type[object]) -> str:
        raise NotImplementedError

    def __set__(self, instance: object, value: object) -> None:
        raise NotImplementedError

    def __delete__(self, instance: object) -> NoReturn:
        raise AttributeError("Deletion of this attribute is not allowed!")
