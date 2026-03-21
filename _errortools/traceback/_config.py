from _errortools.traceback._color_codes import ColorCodes

import re
from typing import Pattern


class TracebackConfig:
    """Configuration class for customizing colored traceback behavior and appearance.

    This class centralizes all configurable settings for the colored traceback system,
    including color styles, feature toggles, and error keyword extraction rules. It
    serves as a single source of truth for traceback formatting and can be subclassed
    to create reusable custom configurations.

    All class attributes are designed to be overridden either by subclassing or by
    creating an instance with modified attributes (instance-level overrides take
    precedence over class-level defaults).

    Attributes:
        ERROR_STYLE: Tuple of ColorCodes members defining the style for exception names
            and messages (default: bold red).
        FILE_STYLE: Tuple of ColorCodes members for file path formatting (default: blue).
        LINE_STYLE: Tuple of ColorCodes members for line number formatting (default: yellow).
        CARET_STYLE: Tuple of ColorCodes members for error position caret (default: red).
        RESET: ANSI reset sequence to restore default terminal style (auto-generated
            from ColorCodes.reset()).
        ENABLE_HIGHLIGHT: If True, show a caret (^) under the exact error position in
            the source code line (default: True).
        ENABLE_EXCEPTION_CHAIN: If True, display chained exceptions (`__cause__`/`__context__`)
            with tracebacks (default: True).
        FALLBACK_TO_DEFAULT: If True, revert to Python's native traceback if the colored
            formatter encounters an error (default: True).
        EXCEPTION_PATTERNS: Mapping of exception types to regex patterns for extracting
            error keywords (e.g., undefined variable names for NameError). Patterns
            should capture the relevant keyword in the first regex group where possible.

    Examples:
        Basic usage with default configuration:
            >>> config = TracebackConfig()
            >>> use_traceback(config=config)

        Custom color scheme (purple errors, green line numbers):
            >>> class PurpleErrorConfig(TracebackConfig):
            ...     ERROR_STYLE = (ColorCodes.BOLD, ColorCodes.PURPLE)
            ...     LINE_STYLE = (ColorCodes.GREEN,)
            >>> use_traceback(config=PurpleErrorConfig())

        Add support for custom exception type:
            >>> class ExtendedConfig(TracebackConfig):
            ...     EXCEPTION_PATTERNS = {
            ...         **TracebackConfig.EXCEPTION_PATTERNS,
            ...         ValueError: re.compile(r"invalid literal for '([^']+)'")
            ...     }
            >>> use_traceback(config=ExtendedConfig())

        Disable exception chain display:
            >>> class MinimalConfig(TracebackConfig):
            ...     ENABLE_EXCEPTION_CHAIN = False
            >>> use_traceback(config=MinimalConfig())

    Notes:
        - All color style attributes accept tuples of ColorCodes members (e.g., (BOLD, RED))
          to combine multiple styles.
        - Regex patterns in EXCEPTION_PATTERNS should be designed to extract the most
          relevant keyword for error position highlighting (e.g., variable/attribute names).
        - For Windows terminal support, install `colorama` (automatically detected).
    """

    # Color style definitions (use ColorCodes enum members)
    ERROR_STYLE: tuple[ColorCodes, ...] = (ColorCodes.BOLD, ColorCodes.RED)
    FILE_STYLE: tuple[ColorCodes, ...] = (ColorCodes.BLUE,)
    LINE_STYLE: tuple[ColorCodes, ...] = (ColorCodes.YELLOW,)
    CARET_STYLE: tuple[ColorCodes, ...] = (ColorCodes.RED,)
    RESET: str = ColorCodes.reset()

    # Feature toggles
    ENABLE_HIGHLIGHT: bool = True  # Enable error position caret highlighting
    ENABLE_EXCEPTION_CHAIN: bool = True  # Show exception chain (__cause__/__context__)
    FALLBACK_TO_DEFAULT: bool = True  # Fall back to native traceback on internal error

    # Regex patterns to extract error keywords from common exception types
    EXCEPTION_PATTERNS: dict[type, Pattern[str]] = {
        NameError: re.compile(r"'([^']+)'"),
        AttributeError: re.compile(r"attribute '([^']+)'"),
        KeyError: re.compile(r"'([^']+)'"),
        TypeError: re.compile(r"'([^']+)'"),
        IndexError: re.compile(r"index out of range"),  # Marker for IndexError handling
    }