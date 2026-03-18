class ErrorAttrDeletionMixin:
    """
    Mixin class for handling non-existent attribute deletion via `__errordelattr__`
    
    Core functionality: Triggers `__errordelattr__` when trying to delete
    attributes that do not exist (via Python's native `__delattr__`).
    """
    def __delattr__(self, name: str):
        """
        Native magic method: Entry point for attribute deletion
        Checks if attribute exists before deletion (triggers `__errordelattr__` if not).
        
        Args:
            name: Name of the attribute to delete
        """
        if not hasattr(self, name):
            self.__errordelattr__(name)
        else:
            super().__delattr__(name)
    
    def __errordelattr__(self, name: str):
        """
        Custom magic method: Handle deletion of non-existent attributes
        
        Override this method in subclasses to implement custom logic for
        deleting missing attributes (log warnings, raise custom errors, etc.).
        
        Args:
            name: Name of the missing attribute
        Raises:
            AttributeError: Generic missing attribute deletion error
        """
        error_msg = f"Cannot delete non-existent attribute '{name}' from {self.__class__.__name__} instance"
        raise AttributeError(error_msg)
