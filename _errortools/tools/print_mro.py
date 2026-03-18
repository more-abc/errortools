"""A helper tool for print the class's `__mro__`. (Base class)"""

from typing import TypeVar

objectT = TypeVar('objectT', bound=object)

def print_mro(cls: type[objectT], indent: int = 0) -> None:
    """
    Print the method resolution order (MRO) of 
    the specified class and format the output for better readability.

    Args:
        cls: The class object whose MRO is to be printed.
        indent: The number of indent spaces for formatted output, default 0.
    """
    if not isinstance(cls, type):
        raise TypeError(f"Expected a class type, got {type(cls).__name__} instead")
    
    indent_str = " " * indent
    
    print(f"{indent_str}Class: {cls.__name__}")
    
    print(f"{indent_str}MRO (Method Resolution Order):")
    for idx, class_in_mro in enumerate(cls.__mro__):
        print(f"{indent_str}  [{idx}] {class_in_mro.__module__}.{class_in_mro.__name__}")
    
    print()