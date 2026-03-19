from typing import Any, Literal, Union, Type
from abc import ABC, abstractmethod

from .tools.error_msg import ErrorAttrableRaiseNotImplementedErrorMessage as ErrorAttrNotImplementedMsg
from .methods import ErrorAttrMixin

def check_methods(C: Type[Any], *methods: str) -> Union[bool, Literal[NotImplemented]]:  # type: ignore
    """Check methods in `C`. If has, return `True`, else `NotImplemented`.
    
    from `_collections_abc.py`. 
    Copyright 2007 Google, Inc. All Rights Reserved.
    Licensed to PSF under a Contributor Agreement.
    """
    mro: tuple[type[Any], ...] = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True

class ErrorAttrable(ABC):
    """
    Abstract Base Class (ABC) for classes supporting custom attribute error handling.
    
    This class follows the design pattern of `collections.abc` (e.g., Iterable, Mapping):
    - Uses `__subclasshook__` + `check_methods` to validate subclass compliance
    - Enforces implementation of `__errorattr__` via abstract method
    - Implements `__getattr__` to forward missing attribute access to `__errorattr__`
    
    Core behavior:
        When accessing a non-existent attribute, `__getattr__` automatically invokes
        the custom `__errorattr__` method (implemented by subclasses) to handle the error.
    """
    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, C: type[Any]) -> Union[bool, Literal[NotImplemented]]: # type: ignore
        """
        Check if a class is a subclass of ErrorAttrable (per `collections.abc` style).
        
        This method enables `issubclass()` to recognize classes that implement `__errorattr__`
        (even if they don't explicitly inherit from ErrorAttrable), matching the behavior of
        standard ABCs like `collections.abc.Iterable`.
        
        Args:
            C: The class to check for compliance with ErrorAttrable interface
        
        Returns:
            True if C implements __errorattr__, NotImplemented otherwise
        """
        if cls is ErrorAttrable:
            return check_methods(C, "__errorattr__")
        return NotImplemented

    def __getattr__(self, name: str) -> Any:
        """
        Native magic method: Automatically invoked for missing attribute access.
        
        Forwards the attribute lookup failure to the custom `__errorattr__` method,
        which must be implemented by subclasses (enforced by abstractmethod).
        
        Args:
            name: Name of the missing attribute being accessed
        
        Returns:
            Any: Result from the subclass's __errorattr__ implementation
        
        Raises:
            NotImplementedError: If __errorattr__ is not implemented (fallback)
        """
        return self.__errorattr__(name)

    @abstractmethod
    def __errorattr__(self, name: str) -> Any:
        """
        Abstract method for custom missing attribute handling (MUST be implemented by subclasses).
        
        Subclasses should override this method to define personalized behavior for
        missing attribute access (e.g., return default values, raise descriptive errors).
        
        Args:
            name: Name of the missing attribute being accessed
        
        Raises:
            NotImplementedError: If not overridden (enforced by @abstractmethod)
            AttributeError: Recommended error type for missing attributes (standard practice)
        """
        raise NotImplementedError(ErrorAttrNotImplementedMsg)
    
# first one!
ErrorAttrable.register(ErrorAttrMixin)
