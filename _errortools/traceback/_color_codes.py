from enum import Enum

class ColorCodes(Enum):
    """ANSI escape sequence enumeration for terminal text styling/colorization.
    
    This enum centralizes all common ANSI escape codes for text formatting (styles, 
    foreground colors, background colors) and provides helper methods to construct 
    valid escape sequences.
    
    Key Features:
        - Encapsulates ANSI codes as enum members (no **magic numbers** in code)
        - Static methods to build combined style sequences
        - Convenience method to reset all styles
    
    ANSI Escape Sequence Format:
        `\\033[<style_code>;<foreground_code>;<background_code>m`
        Always terminate styled text with the RESET code to avoid persistent styling.
    
    Example Usage:
        >>> # Single color/style
        >>> red_text = ColorCodes.get_code(ColorCodes.RED)
        >>> print(f"{red_text}This is red text{ColorCodes.reset()}")
        >>> 
        >>> # Combined styles (bold + green)
        >>> bold_green = ColorCodes.get_code(ColorCodes.BOLD, ColorCodes.GREEN)
        >>> print(f"{bold_green}Bold green text{ColorCodes.reset()}")
        >>> 
        >>> # Complex style (underline + blue text + yellow background)
        >>> complex_style = ColorCodes.get_code(
        ...     ColorCodes.UNDERLINE, ColorCodes.BLUE, ColorCodes.BG_YELLOW
        ... )
        >>> print(f"{complex_style}Underlined blue text on yellow background{ColorCodes.reset()}")
    """
    RESET = 0          # Reset all styles to default (MUST be used to terminate styling)
    BOLD = 1           # Bold/bright text
    UNDERLINE = 4      # Underlined text
    BLINK = 5          # Blinking text (unsupported by some terminals)
    REVERSE = 7        # Reverse video (swap foreground/background colors)

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36
    WHITE = 37

    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_PURPLE = 45
    BG_CYAN = 46
    BG_WHITE = 47

    @staticmethod
    def get_code(*codes) -> str:
        """Construct a complete ANSI escape prefix from multiple style/color codes.
        
        Combines arbitrary numbers of enum members (styles/colors) into a valid 
        ANSI escape sequence prefix for terminal text formatting.
        
        Args:
            *codes: One or more ColorCodes enum members (e.g., BOLD, RED, BG_YELLOW)
        
        Returns:
            str: Full ANSI escape sequence (e.g., "\033[1;31m" for bold red)
        
        Example:
            >>> ColorCodes.get_code(ColorCodes.BOLD, ColorCodes.BLUE)
            '\\033[1;34m'
        """
        # Extract numeric values from enum members and join with semicolons
        code_nums = [str(code.value) for code in codes]
        return f"\033[{';'.join(code_nums)}m"

    @staticmethod
    def reset() -> str:
        """Convenience method to return the ANSI reset sequence.
        
        Shorthand for ColorCodes.get_code(ColorCodes.RESET) — ensures consistent
        reset behavior across codebase.
        
        Returns:
            str: ANSI reset sequence ("\033[0m")
        
        Example:
            >>> print(f"{ColorCodes.get_code(ColorCodes.GREEN)}Success!{ColorCodes.reset()}")
            Success!  # Printed in green, then reset to default
        """
        return ColorCodes.get_code(ColorCodes.RESET)