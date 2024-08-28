"""Class for solver status."""
from __future__ import annotations
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

    @staticmethod
    def from_str(solver_status: str) -> SolverStatus:
        """Return a given str as PerformanceMeasure."""
        if solver_status == "SUCCESS":
            return SolverStatus.SUCCESS
        if solver_status == "CRASHED":
            return SolverStatus.CRASHED
        if solver_status == "TIMEOUT":
            return SolverStatus.TIMEOUT
        if solver_status == "WRONG":
            return SolverStatus.WRONG
        if solver_status == "ERROR":
            return SolverStatus.ERROR
        if solver_status == "KILLED":
            return SolverStatus.KILLED
        if solver_status == "SAT":
            return SolverStatus.SAT
        if solver_status == "UNSAT":
            return SolverStatus.UNSAT
        return SolverStatus.UNKNOWN
