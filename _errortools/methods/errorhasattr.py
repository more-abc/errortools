class ErrorAttrCheckMixin:
    """
    Mixin class for batch attribute existence checks via `__errorhasattr__`
    
    Core functionality: Batch check if attributes exist with custom warnings
    (no native magic method trigger - call directly).
    """
    def __errorhasattr__(self, *names: str):
        """
        Custom magic method: Batch check attribute existence
        
        Args:
            *names: Variable length list of attribute names to check
        Returns:
            dict: {attribute_name: bool} (True = exists, False = missing)
        Raises:
            ValueError: If no attribute names are provided
        """
        if not names:
            raise ValueError("At least one attribute name must be provided")
        
        result = {}
        for name in names:
            exists = hasattr(self, name)
            result[name] = exists
        return result

