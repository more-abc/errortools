from typing import Any, Optional


class NonBlankErrorMsg:
    """Descriptor that validates an attribute is a non-blank string after stripping whitespace.

    Validates the value is a string and not empty after trimming leading/trailing whitespace.
    Stores the cleaned (stripped) value on the instance.

    Args:
        message: Name/label used in error messages for validation failures.

    Example:
        >>> class ApiError:
        ...     message = NonBlankErrorMsg("Error message")
        ...     def __init__(self, msg: str):
        ...         self.message = msg
        >>> err = ApiError("Invalid token")
        >>> err.message
        'Invalid token'
        >>> err = ApiError("   ")  # doctest: +SKIP
        ValueError: Error message can't be blank, must provide a valid error message
    """
    __slots__ = ("_message",)

    def __init__(self, message: str) -> None:
        self._message = message

    def __get__(
        self, instance: Optional[object], owner: type[object]
    ) -> str:
        if instance is None:
            return self._message
        return instance.__dict__[self._message]  # type: ignore

    def __set__(self, instance: object, value: Any) -> None:
        validated_value = self.validate(self._message, value)
        instance.__dict__[self._message] = validated_value

    def __delete__(self, instance: object) -> None:
        raise AttributeError("Deletion of this attribute is not allowed!")

    def validate(self, name: str, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string type")

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError(f"{name} can't be blank, must provide a valid error message")

        return stripped_value
