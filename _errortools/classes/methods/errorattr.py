class ErrorAttrMixin:
    """
    Mixin class that provides the custom magic method `__errorattr__`
    Core functionality: Automatically triggers `__errorattr__` to handle errors 
    when accessing non-existent attributes.
    """
    def __getattr__(self, name: str):
        """
        Native magic method: Automatically invoked when accessing non-existent attributes
        Serves as an entry point to forward calls to the custom `__errorattr__` method
        
        Args:
            name: Name of the non-existent attribute being accessed
        
        Returns:
            Any: Result from the custom __errorattr__ implementation
        
        Raises:
            AttributeError: Default error if `__errorattr__` is not overridden
        """
        # Call the custom `__errorattr__` method to handle non-existent attribute access
        return self.__errorattr__(name)
    
    def __errorattr__(self, name: str):
        """
        Custom magic method: Core logic for handling attribute access errors
        Users can override this method in subclasses to implement personalized error handling
        
        Args:
            name: Name of the non-existent attribute being accessed
        
        Raises:
            AttributeError: Generic error message for missing attributes
        """
        error_msg = f"Attribute '{name}' does not exist in the instance of {self.__class__.__name__}"
        raise AttributeError(error_msg)
