from typing import Any, Literal, Union
from abc import ABC, abstractmethod
import copy
import shutil
import csv
import configparser

from typing_extensions import disjoint_base  # I use 3.14.3
from ..methods import (
    ErrorAttrMixin,
    ErrorAttrCheckMixin,
    ErrorAttrDeletionMixin,
    ErrorSetAttrMixin,
)


def _check_methods(C: type[Any], *methods: str) -> Union[bool, Literal[NotImplemented]]:  # type: ignore
    """Check methods in `C`. If has, return `True`, else `NotImplemented`."""
    # from `_collections_abc.py`.
    # Copyright 2007 Google, Inc. All Rights Reserved.
    # Licensed to PSF under a Contributor Agreement.
    mro: tuple[type[Any], ...] = C.__mro__  # Added type hints for mro var
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True


@disjoint_base
class ErrorAttrable(ABC):
    """
    Abstract Base Class (ABC) for classes supporting custom attribute error handling.

    This class follows the design pattern of `collections.abc` (e.g., Iterable, Mapping):
    - Uses `__subclasshook__` + `_check_methods` to validate subclass compliance
    - Enforces implementation of attribute error handling methods via abstract methods
    - Implements native attribute magic methods to forward errors to custom handlers

    Core behavior:
        When attribute operations (get/delete/check/set) fail, the corresponding native
        magic methods automatically invoke custom error handling methods implemented by subclasses.
    """

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, C: type[Any]) -> Union[bool, Literal[NotImplemented]]:  # type: ignore
        """
        Check if a class is a subclass of ErrorAttrable (per `collections.abc` style).

        This method enables `issubclass()` to recognize classes that implement the core
        __errorattr__ method (base requirement), matching the behavior of standard ABCs.

        Args:
            C: The class to check for compliance with ErrorAttrable interface

        Returns:
            True if C implements __errorattr__, NotImplemented otherwise
        """
        if cls is ErrorAttrable:
            return _check_methods(C, "__errorattr__")
        return NotImplemented

    def __getattr__(self, name: str) -> Any:
        """
        Native magic method: Automatically invoked for missing attribute access.

        Forwards the attribute lookup failure to the custom `__errorattr__` method.
        """
        return self.__errorattr__(name)

    @abstractmethod
    def __errorattr__(self, name: str) -> Any:
        """
        Abstract method for custom missing attribute handling (MUST be implemented).

        Args:
            name: Name of the missing attribute being accessed

        Raises:
            NotImplementedError: If not overridden
            AttributeError: Recommended error type for missing attributes
        """
        raise NotImplementedError(
            "Subclasses of ErrorAttrable must implement __errorattr__(self, name: str).\n"
            "See `collections.abc` for similar abstract method requirements (e.g., __iter__ for Iterable)."
        )

    def __delattr__(self, name: str) -> None:
        """
        Native magic method: Automatically invoked for attribute deletion errors.

        Forwards to __errordelattr__ if implemented, else raises standard error.
        """
        if hasattr(self, "__errordelattr__"):
            self.__errordelattr__(name)
        else:
            super().__delattr__(name)

    def __errordelattr__(self, name: str) -> None:
        """
        Custom handler for attribute deletion errors (OPTIONAL to implement).

        Args:
            name: Name of the attribute being deleted
        """
        raise NotImplementedError(
            "Subclasses of ErrorAttrable must implement __errordelattr__(self, name: str).\n"
            "See `collections.abc` for similar abstract method requirements (e.g., __iter__ for Iterable)."
        )

    def __contains__(self, name: str) -> bool:
        """
        Alternative to __hasattr__: Check if attribute exists (customizable).

        Forwards to __errorhasattr__ if implemented, else uses standard check.
        """
        if hasattr(self, "__errorhasattr__"):
            return self.__errorhasattr__(name)
        else:
            return hasattr(super(), name)

    def __errorhasattr__(self, name: str) -> bool:
        """
        Custom handler for attribute existence checks (OPTIONAL to implement).

        Args:
            name: Name of the attribute to check

        Returns:
            bool: True if attribute exists (custom logic), False otherwise
        """
        raise NotImplementedError(
            "Subclasses of ErrorAttrable must implement __errorhasattr__(self, name: str).\n"
            "See `collections.abc` for similar abstract method requirements (e.g., __iter__ for Iterable)."
        )

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Native magic method: Automatically invoked for attribute setting errors.

        Forwards to __errorsetattr__ if implemented, else uses standard setting.
        """
        if hasattr(self, "__errorsetattr__"):
            self.__errorsetattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __errorsetattr__(self, name: str, value: Any) -> None:
        """
        Custom handler for attribute setting errors (OPTIONAL to implement).

        Args:
            name: Name of the attribute to set
            value: Value to assign to the attribute
        """
        raise NotImplementedError(
            "Subclasses of ErrorAttrable must implement __errorsetattr__(self, name: str, value: Any).\n"
            "See `collections.abc` for similar abstract method requirements (e.g., __iter__ for Iterable)."
        )


# register four Mixin's
ErrorAttrable.register(ErrorAttrMixin)
ErrorAttrable.register(ErrorAttrDeletionMixin)
ErrorAttrable.register(ErrorAttrCheckMixin)
ErrorAttrable.register(ErrorSetAttrMixin)


# ----------------------------------------------------------------------
# ErrorCodeable
# ----------------------------------------------------------------------


@disjoint_base
class ErrorCodeable(ABC):
    """Abstract Base Class for exceptions that carry a machine-readable error code.

    Follows the ``collections.abc`` pattern: any class that exposes both a
    ``code`` class attribute (``int``) and a ``default_detail`` class attribute
    (``str``) is recognised as a virtual subclass automatically, without
    explicit inheritance.

    Concrete subclasses **must** implement:
        - ``code``         — integer error code (class variable)
        - ``default_detail`` — fallback human-readable message (class variable)

    Example:

        >>> class PaymentError(ErrorCodeable, Exception):
        ...     code = 6001
        ...     default_detail = "Payment failed."
        >>> issubclass(PaymentError, ErrorCodeable)
        True
    """

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, C: type[Any]) -> Union[bool, Literal[NotImplemented]]:  # type: ignore
        """Recognise any class that defines ``code`` and ``default_detail``."""
        if cls is ErrorCodeable:
            return _check_methods(C, "code", "default_detail")
        return NotImplemented

    @property
    @abstractmethod
    def code(self) -> int:
        """Integer error code identifying this exception type."""
        pass

    @property
    @abstractmethod
    def default_detail(self) -> str:
        """Fallback human-readable message used when no detail is provided."""
        pass


# ----------------------------------------------------------------------
# Warnable
# ----------------------------------------------------------------------


class Warnable(ABC):
    """Abstract Base Class for warning classes that can emit themselves.

    Any class that exposes an ``emit`` classmethod is recognised as a
    virtual subclass automatically via ``__subclasshook__``.

    Concrete subclasses **must** implement:
        - ``emit(cls, detail, stacklevel)`` — issue the warning via ``warnings.warn``

    Example:

        >>> class SlowWarning(Warnable, Warning):
        ...     default_detail = "This operation is slow."
        ...     @classmethod
        ...     def emit(cls, detail=None, stacklevel=2):
        ...         import warnings
        ...         warnings.warn(cls(detail), stacklevel=stacklevel)
        >>> issubclass(SlowWarning, Warnable)
        True
    """

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, C: type[Any]) -> Union[bool, Literal[NotImplemented]]:  # type: ignore
        """Recognise any class that defines an ``emit`` classmethod."""
        if cls is Warnable:
            return _check_methods(C, "emit")
        return NotImplemented

    @classmethod
    @abstractmethod
    def emit(cls, detail: str | None = None, stacklevel: int = 2) -> None:
        """Issue this warning via ``warnings.warn``.

        Args:
            detail: Optional message override.
            stacklevel: Passed to ``warnings.warn``; ``2`` points at the
                caller of ``emit``.
        """
        pass


# ----------------------------------------------------------------------
# Raiseable
# ----------------------------------------------------------------------


class Raiseable(ABC):
    """Abstract Base Class for objects that know how to raise themselves.

    Concrete subclasses **must** implement ``raise_it()``, which should
    raise ``self`` (or a derived exception).  Any class that exposes a
    ``raise_it`` method is recognised as a virtual subclass automatically.

    Example:

        >>> class MyError(Raiseable, Exception):
        ...     def raise_it(self):
        ...         raise self
        >>> e = MyError("oops")
        >>> e.raise_it()
        Traceback (most recent call last):
            ...
        MyError: oops
    """

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, C: type[Any]) -> Union[bool, Literal[NotImplemented]]:  # type: ignore
        """Recognise any class that defines a ``raise_it`` method."""
        if cls is Raiseable:
            return _check_methods(C, "raise_it")
        return NotImplemented

    @abstractmethod
    def raise_it(self) -> None:
        """Raise this object as an exception.

        Raises:
            self: Or a derived exception wrapping this object.
        """
        pass


# ----------------------------------------------------------------------
# Error
# ----------------------------------------------------------------------


class Error(Exception, ABC):
    """Abstract Base Class for module-level Error exceptions.

    Any class named **"Error"** (like copy.Error, shutil.Error, csv.Error)
    is automatically recognised as a virtual subclass of this ABC.

    Virtual subclasses do NOT need to explicitly inherit from this class.

    Example:

        >>> import copy
        >>> import shutil
        >>> isinstance(copy.Error(), Error)
        True
        >>> isinstance(shutil.Error(), Error)
        True
        >>> class MyError:
        ...     __name__ = "Error"
        >>> isinstance(MyError(), Error)
        True
    """

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, subclass: type[Any]) -> bool:
        if cls is Error:
            return subclass.__name__ == "Error"
        return False


Error.register(copy.Error)
Error.register(shutil.Error)
Error.register(csv.Error)
Error.register(configparser.Error)
