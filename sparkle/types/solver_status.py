"""Class for solver status."""
from enum import Enum


class SolverStatus(str, Enum):
    """Possible return states for solver runs."""
    SUCCESS = "SUCCESS"
    CRASHED = "CRASHED"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"
    KILLED = "KILLED"


def get_status_from_str(status: str) -> SolverStatus:
    """Get SolverStatus object from string."""
    return SolverStatus(status.upper())
