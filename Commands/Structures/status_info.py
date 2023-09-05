"""File containing the Status Info class."""


from pathlib import Path
import json
import fcntl
from enum import Enum

from Commands.sparkle_help import sparkle_global_help as sgh


class StatusInfoType(str, Enum):
    SOLVER_RUN = "SBATCH_Solver_Run_Jobs"


class StatusInfo:
    """A class to represent a status info file."""

    def __init__(self, path: Path):
        """Constructs the data dictionary.

        Args:
            path: path for the statusinfo file
        """
        self.path = path
        self.data = dict()

    @classmethod
    def from_file(cls, path: Path):
        """Constructs instance from existing file.

        Args:
            path: path of the statusinfo file
        """
        data = dict(json.load(open(path)))
        status_info = cls(path)
        status_info.data = data
        return status_info

    def save(self):
        """Saves the data to the file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        f = self.path.open("w")
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        f.write(json.dumps(self.data))
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def delete(self):
        """Deletes the statusinfo file"""
        self.path.unlink()


class SolverRunStatusInfo(StatusInfo):

    status = "Status"
    solver = "Solver"
    instance = "Instance"
    start_time = "Start Time"
    start_timestamp = "Start Timestamp"
    cutoff_time = "Cutoff Time"

    def __init__(self, key_str: str):
        job_path = StatusInfoType.SOLVER_RUN
        path = Path(f"{sgh.sparkle_tmp_path}/{job_path}/{key_str}.statusinfo")
        super().__init__(path)

    def set_status(self, status: str):
        """Sets the status attribute.

        Args:
            status: status value
        """
        self.data[self.status] = status

    def set_solver(self, solver: str):
        """Sets the solver attribute.

        Args:
            solver: solver value
        """
        self.data[self.solver] = solver

    def set_instance(self, instance: str):
        """Sets the instance attribute.

        Args:
            instance: instance value
        """
        self.data[self.instance] = instance

    def set_start_time(self, start_time: str):
        """Sets the solver attribute.

        Args:
            start_time: solver value
        """
        self.data[self.start_time] = start_time

    def set_start_timestamp(self, start_timestamp: str):
        """Sets the start timestamp attribute.

        Args:
            start_timestamp: start timestamp value
        """
        self.data[self.start_timestamp] = start_timestamp

    def set_cutoff_time(self, cutoff_time: str):
        """Sets the cutoff time attribute.

        Args:
            cutoff_time: cutoff time value
        """
        self.data[self.cutoff_time] = cutoff_time

    def get_status(self) -> str:
        """Access to status."""
        return self.data[self.status]

    def get_solver(self) -> str:
        """Access to solver."""
        return self.data[self.solver]

    def get_instance(self) -> str:
        """Access to instance."""
        return self.data[self.instance]

    def get_start_time(self) -> str:
        """Access to start time."""
        return self.data[self.start_time]

    def get_start_timestamp(self) -> str:
        """Access to start timestamp."""
        return self.data[self.start_timestamp]

    def get_cutoff_time(self) -> str:
        """Access to cutoff time."""
        return self.data[self.cutoff_time]

