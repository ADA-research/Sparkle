from enum import Enum

class VerbosityLevel(Enum):
    """Possible setting states."""

    QUIET = 0
    STANDARD = 1

    @staticmethod
    def from_string(name):
        try:
            return VerbosityLevel[name]
        except KeyError:
            raise ValueError(f"'{name}' is not a valid VerbosityLevel")