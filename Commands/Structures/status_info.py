"""File containing the Status Info class."""

from __future__ import annotations

import time
from pathlib import Path
import json
import fcntl
from enum import Enum
from typing import Type
from abc import ABC

from Commands.sparkle_help import sparkle_global_help as sgh


class StatusInfoType(str, Enum):
    """An enum class for different status info types."""
    SOLVER_RUN = "SBATCH_Solver_Run_Jobs"
    CONFIGURE_SOLVER = "SBATCH_Configure_Solver_Jobs"


class StatusInfo(ABC):
    """A class to represent a status info file."""
    job_path = None
    start_time = "Start Time"
    start_timestamp = "Start Timestamp"
    status = "Status"

    def __init__(self: StatusInfo, key_str: str) -> None:
        """Constructs the data dictionary.

        Args:
            key_str: key for the statusinfo file
        """
        self.path = Path(f"{sgh.sparkle_tmp_path}/{self.job_path}/{key_str}.statusinfo")
        self.data = dict()
        self.set_status("Running")

        start_time = time.time()
        self.set_start_time(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(start_time)))
        self.set_start_timestamp(str(start_time))

    def set_status(self: SolverRunStatusInfo, status: str) -> None:
        """Sets the status attribute.

        Args:
            status: status value
        """
        self.data[self.status] = status

    def set_start_time(self: SolverRunStatusInfo, start_time: str) -> None:
        """Sets the solver attribute.

        Args:
            start_time: solver value
        """
        self.data[self.start_time] = start_time

    def set_start_timestamp(self: SolverRunStatusInfo, start_timestamp: str) -> None:
        """Sets the start timestamp attribute.

        Args:
            start_timestamp: start timestamp value
        """
        self.data[self.start_timestamp] = start_timestamp

    @classmethod
    def from_file(cls: Type[StatusInfo], path: Path) -> StatusInfo:
        """Constructs instance from existing file.

        Args:
            path: path of the statusinfo file
        """
        data = dict(json.load(open(path)))
        status_info = cls(path)
        status_info.data = data
        return status_info

    def save(self: StatusInfo) -> None:
        """Saves the data to the file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        f = self.path.open("w")
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        f.write(json.dumps(self.data))
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def delete(self: StatusInfo) -> None:
        """Deletes the statusinfo file."""
        self.path.unlink()

    def get_start_time(self: SolverRunStatusInfo) -> str:
        """Access to start time."""
        return self.data[self.start_time]

    def get_start_timestamp(self: SolverRunStatusInfo) -> str:
        """Access to start timestamp."""
        return self.data[self.start_timestamp]


class SolverRunStatusInfo(StatusInfo):
    """Status info for solver run jobs."""
    job_path = StatusInfoType.SOLVER_RUN
    solver = "Solver"
    instance = "Instance"
    cutoff_time = "Cutoff Time"

    def __init__(self: SolverRunStatusInfo, key_str: str) -> None:
        """Call the Status info superclass.

        Args:
            key_str: job specific key string
        """
        super().__init__(key_str)

    def set_solver(self: SolverRunStatusInfo, solver: str) -> None:
        """Sets the solver attribute.

        Args:
            solver: solver value
        """
        self.data[self.solver] = solver

    def set_instance(self: SolverRunStatusInfo, instance: str) -> None:
        """Sets the instance attribute.

        Args:
            instance: instance value
        """
        self.data[self.instance] = instance

    def set_cutoff_time(self: SolverRunStatusInfo, cutoff_time: str) -> None:
        """Sets the cutoff time attribute.

        Args:
            cutoff_time: cutoff time value
        """
        self.data[self.cutoff_time] = cutoff_time

    def get_status(self: SolverRunStatusInfo) -> str:
        """Access to status."""
        return self.data[self.status]

    def get_solver(self: SolverRunStatusInfo) -> str:
        """Access to solver."""
        return self.data[self.solver]

    def get_instance(self: SolverRunStatusInfo) -> str:
        """Access to instance."""
        return self.data[self.instance]

    def get_cutoff_time(self: SolverRunStatusInfo) -> str:
        """Access to cutoff time."""
        return self.data[self.cutoff_time]


class ConfigureSolverStatusInfo(StatusInfo):
    """Status info for configure solver jobs."""
    job_path = StatusInfoType.CONFIGURE_SOLVER
    solver = "Solver"
    instance_set_train = "Training Instance"
    instance_set_test = "Test Instance"

    def __init__(self: ConfigureSolverStatusInfo, key_str: str) -> None:
        """Call the Status info superclass.

        Args:
            key_str: job specific key string
        """
        super().__init__(key_str)

    def set_solver(self: ConfigureSolverStatusInfo, solver: str) -> None:
        """Sets the solver attribute.

        Args:
            solver: solver value
        """
        self.data[self.solver] = solver

    def set_instance_set_train(self: ConfigureSolverStatusInfo, instance_set_train: str)\
            -> None:
        """Sets the training set name.

        Args:
            instance_set_train: name of the training instance set
        """
        self.data[self.instance_set_train] = instance_set_train

    def set_instance_set_test(self: ConfigureSolverStatusInfo, instance_set_test: str)\
            -> None:
        """Sets the test set name.

        Args:
            instance_set_test: name of the test instance set
        """
        self.data[self.instance_set_test] = instance_set_test

    def get_instance_set_test(self: ConfigureSolverStatusInfo) -> str:
        """Access to the test instance set name."""
        return self.data[self.instance_set_test]

    def get_instance_set_train(self: ConfigureSolverStatusInfo) -> str:
        """Access to training instance set name."""
        return self.data[self.instance_set_train]

    def get_solver(self: ConfigureSolverStatusInfo) -> str:
        """Access to solver."""
        return self.data[self.solver]
