"""Base and concrete group classes for collecting and raising exceptions together."""

from abc import abstractmethod, ABC
import sys

__all__ = [
    "BaseGroup",
    "GroupErrors",
]


class BaseGroup(Exception, ABC):
    """Abstract base for exception collector groups.

    Defines the interface that all group implementations must satisfy:
    `collect`, `raise_group`, `clear`, and the
    `errors` property.  Concrete subclasses decide the storage
    strategy and the type of group they raise.

    Attributes:
        group_msg: The message attached to the raised group.
    """

    def __init__(self, group_msg: str = "multiple errors") -> None:
        """Initialise the group with a message.

        Args:
            group_msg: Message for the raised group.
                Defaults to ``"multiple errors"``.
        """
        self.group_msg = group_msg

    @property
    @abstractmethod
    def errors(self) -> list[Exception]:
        """A copy of the collected exceptions."""

    @abstractmethod
    def collect(self, exc: Exception) -> None:
        """Add *exc* to the group without raising it.

        Args:
            exc: The exception instance to collect.
        """

    @abstractmethod
    def clear(self) -> None:
        """Remove all collected exceptions."""

    @abstractmethod
    def raise_group(self) -> None:
        """Raise all collected exceptions as a group.

        Does nothing if no exceptions have been collected.
        """

    def __len__(self) -> int:
        """Return the number of collected exceptions."""
        return len(self.errors)

    def __bool__(self) -> bool:
        """Return ``True`` if any exceptions have been collected."""
        return bool(self.errors)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(group_msg={self.group_msg!r}, errors={len(self)})"
        )


class GroupErrors(BaseGroup):
    """A collector that accumulates exceptions and raises them as an ExceptionGroup.

    Call `collect` to add exceptions one by one, then `raise_group`
    to raise them all at once.  Use `errors` to inspect what has been
    collected without raising.

    Example:

        >>> g = GroupErrors("validation failed")
        >>> g.collect(TypeError("expected str"))
        >>> g.collect(ValueError("value out of range"))
        >>> g.raise_group()
        Traceback (most recent call last):
            ...
        ExceptionGroup: validation failed (2 sub-exceptions)
    """

    def __init__(self, group_msg: str = "multiple errors") -> None:
        super().__init__(group_msg)
        self._errors: list[Exception] = []

    @property
    def errors(self) -> list[Exception]:
        """A copy of the collected exceptions."""
        return list(self._errors)

    def collect(self, exc: Exception) -> None:
        """Add *exc* to the group without raising it.

        Args:
            exc: The exception instance to collect.
        """
        self._errors.append(exc)

    def clear(self) -> None:
        """Remove all collected exceptions."""
        self._errors.clear()

    def raise_group(self) -> None:
        """Raise all collected exceptions as an `ExceptionGroup`.

        Does nothing if no exceptions have been collected.

        Raises:
            ExceptionGroup: Containing every exception added via `collect`.
        """
        if self._errors:
            raise ExceptionGroup(self.group_msg, self._errors)


if sys.version_info <= (3, 10):
    del GroupErrors
