"""Helper types for command line interface."""
from enum import Enum
from typing import Type


class VerbosityLevel(Enum):
    """Enum of possible verbosity states."""

    QUIET = 0
    STANDARD = 1

    @staticmethod
    def from_string(name: str) -> "VerbosityLevel":
        """Converts string to VerbosityLevel."""
        return VerbosityLevel[name]


class TEXT(Enum):
    """Class for ANSI text formatting."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # BG = Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @classmethod
    def format_text(cls: Type["TEXT"], formats: list[str], text: str) -> str:
        """Styles the string based on the provided formats."""
        start_format = "".join(format_.value for format_ in formats)
        end_format = cls.RESET.value
        return f"{start_format}{text}{end_format}"
