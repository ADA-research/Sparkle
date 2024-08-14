"""Class for solver status."""
from enum import Enum


class SolverStatus(str, Enum):
    """Possible return states for solver runs."""
    SUCCESS = "SUCCESS"
    CRASHED = "CRASHED"
    TIMEOUT = "TIMEOUT"
    WRONG = "WRONG"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"
    KILLED = "KILLED"

    # SAT specific status
    SAT = "SAT"
    UNSAT = "UNSAT"
