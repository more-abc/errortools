import sys
import traceback
import os
import atexit
from typing import Any, Optional

from _errortools.traceback._config import TracebackConfig
from ._color_codes import ColorCodes

# Try to import colorama for Windows terminal color support
try:
    from colorama import init as colorama_init, deinit as colorama_deinit
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


def _traceback_init(config: Optional[TracebackConfig] = None) -> None:
    """Initialize the colored traceback formatting system.

    Installs a custom exception hook that enhances Python's native traceback output
    with semantic color highlighting, precise error position marking, full exception
    chain support, and cross-platform terminal compatibility.

    Automatically falls back to the native Python traceback if the output stream
    is not a TTY (terminal) or if color is not supported.

    Args:
        config: Optional TracebackConfig instance to override default styling
            and behavior. If None, the default TracebackConfig is used.

    Example:
        >>> _traceback_init()
        >>> # Test with a NameError
        >>> printq  # Will output a colored traceback with highlighted error position
    """
    # Initialize config with defaults if not provided (avoids mutable default arg pitfall)
    if config is None:
        config = TracebackConfig()
    
    original_excepthook = sys.excepthook
    colorama_initialized = False
    
    # Initialize colorama for Windows terminal ANSI color support
    if COLORAMA_AVAILABLE and os.name == 'nt':
        colorama_init() 
        colorama_initialized = True
        # Register cleanup to restore terminal state on program exit
        atexit.register(colorama_deinit) 
    
    def _extract_error_keyword(
        exc_type: type,
        exc_value: BaseException
    ) -> Optional[str]:
        """Extract the error keyword from an exception instance for position highlighting.

        Matches the exception type against predefined regex patterns to pull out
        the relevant keyword (e.g., undefined variable name for NameError, missing
        attribute for AttributeError).

        Args:
            exc_type: The exception type class
            exc_value: The exception instance

        Returns:
            The extracted error keyword string, or None if no match is found.
        """
        if exc_type not in config.EXCEPTION_PATTERNS:
            return None
        
        pattern = config.EXCEPTION_PATTERNS[exc_type]
        match = pattern.search(str(exc_value))
        
        if not match:
            return None
        
        # Return first capture group if available, otherwise full matched text
        return match.group(1) if match.groups() else match.group(0)
    
    def _highlight_error_position(
        text: str,
        error_keyword: Optional[str] = None,
        syntax_offset: Optional[int] = None
    ) -> None:
        """Print a line of code with a caret highlighting the exact error position.

        Renders the original code line with a position marker, then adds a colored
        caret underline to point directly at the error. Supports both syntax errors
        (with explicit offset) and runtime errors (with error keyword matching).

        Args:
            text: The raw line of source code from the traceback
            error_keyword: The keyword to match and highlight (for runtime errors)
            syntax_offset: 1-based character offset for SyntaxError position
        """
        if not config.ENABLE_HIGHLIGHT or not text:
            return
        
        # Preserve original line formatting, only strip trailing newlines
        original_text = text.rstrip('\n\r')
        prefix_indent = "    "  # Standard Python traceback indentation
        
        # Print the code line with position marker
        print(f"{prefix_indent}{original_text}   <--- here", file=sys.stderr)
        
        # Calculate highlight start position and length
        start_pos: Optional[int] = None
        highlight_length: int = 1
        
        if syntax_offset is not None:
            # Convert 1-based syntax offset to 0-based index
            start_pos = max(0, syntax_offset - 1)
        elif error_keyword and error_keyword in original_text:
            # Match first occurrence of the error keyword
            start_pos = original_text.find(error_keyword)
            highlight_length = len(error_keyword)
        
        # Render the colored caret underline
        if start_pos is not None:
            caret_indent = prefix_indent + " " * start_pos
            caret_style = ColorCodes.get_code(*config.CARET_STYLE)
            caret = "^" * highlight_length
            print(f"{caret_indent}{caret_style}{caret}{config.RESET}", file=sys.stderr)
    
    def _print_single_frame(
        frame: traceback.FrameSummary,
        error_keyword: Optional[str] = None
    ) -> None:
        """Print a single frame of the traceback with color formatting.

        Renders the file path, line number, function name, and source code line
        for a single traceback frame, with semantic color highlighting.

        Args:
            frame: A single FrameSummary object from traceback.extract_tb()
            error_keyword: Optional error keyword to highlight in the code line
        """
        filename, lineno, funcname, text = frame
        
        # Apply color formatting to file path and line number
        colored_filename = (
            f"{ColorCodes.get_code(*config.FILE_STYLE)}"
            f"{str(filename)}"
            f"{config.RESET}"
        )
        colored_lineno = (
            f"{ColorCodes.get_code(*config.LINE_STYLE)}"
            f"{lineno}"
            f"{config.RESET}"
        )
        
        # Print frame header
        print(
            f"  File: {colored_filename}, line {colored_lineno}, in {funcname}",
            file=sys.stderr
        )
        
        # Print and highlight code line if available
        if text:
            _highlight_error_position(text, error_keyword=error_keyword)
    
    def _print_exception_chain(
        exc_type: type,
        exc_value: BaseException,
        exc_tb: Any,
        is_cause: bool = False
    ) -> None:
        """Recursively print an exception and its full traceback, including exception chains.

        Handles both standalone exceptions and chained exceptions (via __cause__ or
        __context__), rendering each with full color formatting and highlighting.

        Args:
            exc_type: The type of the exception to print
            exc_value: The exception instance
            exc_tb: The traceback object for the exception
            is_cause: Whether this exception is the cause of the previous one
                (used to render the exception chain separator)
        """
        # Print exception chain separator
        if is_cause:
            print(
                "\nThe above exception was the direct cause of the following exception:\n",
                file=sys.stderr
            )
        
        # Print exception type and message (bold red by default)
        err_style = ColorCodes.get_code(*config.ERROR_STYLE)
        print(f"{err_style}{exc_type.__name__}: {exc_value}{config.RESET}", file=sys.stderr)
        
        # Special handling for SyntaxError (has built-in position information)
        if isinstance(exc_value, SyntaxError) and exc_value.text:
            filename = exc_value.filename or "<string>"
            lineno = exc_value.lineno or 0
            offset = exc_value.offset or 0
            text = exc_value.text
            
            colored_filename = (
                f"{ColorCodes.get_code(*config.FILE_STYLE)}"
                f"{filename}"
                f"{config.RESET}"
            )
            colored_lineno = (
                f"{ColorCodes.get_code(*config.LINE_STYLE)}"
                f"{lineno}"
                f"{config.RESET}"
            )
            
            print(f"  File: {colored_filename}, line {colored_lineno}", file=sys.stderr)
            _highlight_error_position(text, syntax_offset=offset)
            return
        
        # Process and print traceback frames for regular exceptions
        if exc_tb:
            frames: list[traceback.FrameSummary] = traceback.extract_tb(exc_tb)
            
            # Iterate through all frames, highlight error only on the final frame
            for index, frame in enumerate(frames):
                is_final_frame = (index == len(frames) - 1)
                error_keyword = _extract_error_keyword(exc_type, exc_value) if is_final_frame else None
                _print_single_frame(frame, error_keyword=error_keyword)
        
        # Recursively print exception chain if enabled
        if config.ENABLE_EXCEPTION_CHAIN:
            # Handle explicit __cause__ first
            if exc_value.__cause__:
                _print_exception_chain(
                    type(exc_value.__cause__),
                    exc_value.__cause__,
                    exc_value.__cause__.__traceback__,
                    is_cause=True
                )
            # Handle implicit __context__ if not suppressed
            elif exc_value.__context__ and not exc_value.__suppress_context__:
                _print_exception_chain(
                    type(exc_value.__context__),
                    exc_value.__context__,
                    exc_value.__context__.__traceback__,
                    is_cause=True
                )
    
    def colored_excepthook(
        exc_type: type,
        exc_value: BaseException,
        exc_tb: Any
    ) -> None:
        """Custom exception hook that replaces Python's native sys.excepthook.
        
        Validates terminal color support, then renders the full colored traceback.
        Falls back to the native exception hook on any internal error or if color
        is not supported.

        Args:
            exc_type: The type of the uncaught exception
            exc_value: The uncaught exception instance
            exc_tb: The traceback object for the uncaught exception
        """
        try:
            # Only use colored output if stderr is connected to a TTY terminal
            if not sys.stderr.isatty():
                original_excepthook(exc_type, exc_value, exc_tb)
            
            # Render the full exception chain with color formatting
            _print_exception_chain(exc_type, exc_value, exc_tb)
        
        except Exception:
            # Fall back to native traceback if enabled, otherwise re-raise
            if config.FALLBACK_TO_DEFAULT:
                original_excepthook(exc_type, exc_value, exc_tb)
            else:
                raise
    
    # Install the custom exception hook
    sys.excepthook = colored_excepthook