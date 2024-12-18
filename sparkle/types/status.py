"""Class for solver status."""
from __future__ import annotations
from enum import Enum


class SolverStatus(str, Enum):
    """Possible return states for solver runs."""
    def __str__(self):
        return str(self.value)
    
    SUCCESS = "SUCCESS"  # Positive status
    UNKNOWN = "UNKNOWN"  # Semi positive status
    SAT = "SAT"  # SAT specific positive status
    UNSAT = "UNSAT"  # SAT specific positive status

    # Negative status
    CRASHED = "CRASHED"
    TIMEOUT = "TIMEOUT"
    WRONG = "WRONG"
    ERROR = "ERROR"
    KILLED = "KILLED"
