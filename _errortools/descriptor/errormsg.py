from typing import Optional, NoReturn


# NOTE: The attribute returns the preset message when accessed.
# Any attempt to modify or delete it raises an ``AttributeError``.
class ErrorMsg:
    """Descriptor that creates a read-only attribute with a fixed message.

    Args:
        message: The fixed string returned when the attribute is accessed.

    Example:

        >>> class MyClass:
        ...     status = ErrorMsg("This attribute is read-only")
        >>> obj = MyClass()
        >>> obj.status
        'This attribute is read-only'
        >>> obj.status = "new"  # doctest: +SKIP
        AttributeError: Modification of this attribute is not allowed!
        >>> del obj.status  # doctest: +SKIP
        AttributeError: Deletion of this attribute is not allowed!
    """

    __slots__ = ("_message",)

    def __init__(self, message: str) -> None:
        self._message = message

    def __get__(self, instance: Optional[object], owner: type[object]) -> str:
        return self._message

    def __set__(self, instance: object, value: object) -> NoReturn:
        raise AttributeError("Modification of this attribute is not allowed!")

    def __delete__(self, instance: object) -> NoReturn:
        raise AttributeError("Deletion of this attribute is not allowed!")
