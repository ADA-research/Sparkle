from enum import Enum

class VerbosityLevel(Enum):
    """Possible setting states."""

    REDUCED = 0
    STANDARD = 1
    EXTENSIVE = 2

    @staticmethod
    def from_string(name):
        try:
            return VerbosityLevel[name]
        except KeyError:
            raise ValueError(f"'{name}' is not a valid VerbosityLevel")