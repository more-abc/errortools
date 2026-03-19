class ErrorSetAttrMixin:
    """
    Mixin class for handling forbidden attribute assignment via `__errorsetattr__`
    
    Core functionality: Triggers `__errorsetattr__` when trying to assign values
    to attributes in the `_forbidden_attrs` list.
    """
    # Define forbidden attributes in subclasses (list of attribute names)
    _forbidden_attrs: list[str] = []
    
    def __setattr__(self, name: str, value):
        """
        Native magic method: Entry point for attribute assignment
        Blocks assignment to forbidden attributes (triggers `__errorsetattr__`).
        
        Args:
            name: Name of the attribute to assign
            value: Value to assign
        """
        if name in self._forbidden_attrs:
            self.__errorsetattr__(name, value)
        else:
            super().__setattr__(name, value)
    
    def __errorsetattr__(self, name: str, value):
        """
        Custom magic method: Handle forbidden attribute assignment
        
        Override this method in subclasses to implement custom logic for
        forbidden assignments (log warnings, raise custom errors, etc.).
        
        Args:
            name: Name of the forbidden attribute
            value: Value attempted to be assigned
        Raises:
            AttributeError: Generic forbidden assignment error
        """
        error_msg = f"Cannot assign to forbidden attribute '{name}' in {self.__class__.__name__} instance"
        raise AttributeError(error_msg)
