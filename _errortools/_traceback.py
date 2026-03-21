from typing import Optional
from .traceback._init import _traceback_init, TracebackConfig


def use_traceback(config: Optional[TracebackConfig] = None) -> None:
    """Initialize and enable the colored traceback system with optional custom configuration.
    
    Args:
        config: Optional custom TracebackConfig instance to customize traceback
            appearance (colors, highlighting) and behavior (exception chain display,
            fallback logic). If None, default configuration is used.

    Raises:
        TypeError: If the provided config is not a TracebackConfig instance
        RuntimeError: If the traceback system fails to initialize (rare)

    Example:
        >>> # Basic usage (default config)
        >>> use_traceback()
        >>> 
        >>> # Custom config (e.g., yellow bold error highlights)
        >>> class CustomConfig(TracebackConfig):
        ...     ERROR_STYLE = (ColorCodes.BOLD, ColorCodes.YELLOW)
        >>> use_traceback(config=CustomConfig())
    """
    try:
        # Validate config type if provided
        if config is not None and not isinstance(config, TracebackConfig):
            raise TypeError(
                f"config must be a TracebackConfig instance, got {type(config).__name__}"
            )
        
        # Initialize the colored traceback system
        _traceback_init(config=config)
    
    except TypeError as e:
        # Re-raise type errors with clearer context
        raise TypeError(f"Failed to validate traceback config: {str(e)}") from e
    
    except Exception as e:
        # Catch-all for unexpected initialization errors
        raise RuntimeError(f"Failed to initialize colored traceback system: {str(e)}") from e