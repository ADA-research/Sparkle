"""File containing the Status Info class."""

from __future__ import annotations

import time
from pathlib import Path
import json
import fcntl
from enum import Enum
from typing import Type
from abc import ABC, abstractmethod

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help as sbh


class StatusInfoType(str, Enum):
    """An enum class for different status info types."""
    SOLVER_RUN = "SBATCH_Solver_Run_Jobs"
    CONFIGURE_SOLVER = "SBATCH_Configure_Solver_Jobs"
    CONSTRUCT_PARALLEL_PORTFOLIO = "SBATCH_Construct_Parallel_Portfolio_Jobs"


class StatusInfo(ABC):
    """A class to represent a status info file."""
    job_path = None
    start_time_key = "Start Time"
    start_timestamp_key = "Start Timestamp"
    status_key = "Status"

    def __init__(self: StatusInfo) -> None:
        """Constructs the data dictionary."""
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
        self.data[self.status_key] = status

    def set_start_time(self: SolverRunStatusInfo, start_time: str) -> None:
        """Sets the solver attribute.

        Args:
            start_time: solver value
        """
        self.data[self.start_time_key] = start_time

    def set_start_timestamp(self: SolverRunStatusInfo, start_timestamp: str) -> None:
        """Sets the start timestamp attribute.

        Args:
            start_timestamp: start timestamp value
        """
        self.data[self.start_timestamp_key] = start_timestamp

    @classmethod
    def from_file(cls: Type[StatusInfo], path: Path) -> StatusInfo:
        """Constructs instance from existing file.

        Args:
            path: path of the statusinfo file
        """
        data = dict(json.load(open(path)))
        status_info = cls()
        status_info.data = data
        return status_info

    @abstractmethod
    def get_key_string(self: StatusInfo) -> str:
        """Method to generate key string."""
        pass

    def save(self: StatusInfo) -> None:
        """Saves the data to the file."""
        key_str = self.get_key_string()
        path = Path(f"{sgh.sparkle_tmp_path}/{self.job_path}/{key_str}.statusinfo")
        path.parent.mkdir(parents=True, exist_ok=True)
        f = path.open("w")
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        f.write(json.dumps(self.data))
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def delete(self: StatusInfo) -> None:
        """Deletes the statusinfo file."""
        self.path.unlink()

    def get_start_time(self: SolverRunStatusInfo) -> str:
        """Access to start time."""
        return self.data[self.start_time_key]

    def get_start_timestamp(self: SolverRunStatusInfo) -> str:
        """Access to start timestamp."""
        return self.data[self.start_timestamp_key]


class SolverRunStatusInfo(StatusInfo):
    """Status info for solver run jobs."""
    job_path = StatusInfoType.SOLVER_RUN
    solver_key = "Solver"
    instance_key = "Instance"
    cutoff_time_key = "Cutoff Time"

    def set_solver(self: SolverRunStatusInfo, solver: str) -> None:
        """Sets the solver attribute.

        Args:
            solver: solver value
        """
        self.data[self.solver_key] = solver

    def set_instance(self: SolverRunStatusInfo, instance: str) -> None:
        """Sets the instance attribute.

        Args:
            instance: instance value
        """
        self.data[self.instance_key] = instance

    def set_cutoff_time(self: SolverRunStatusInfo, cutoff_time: str) -> None:
        """Sets the cutoff time attribute.

        Args:
            cutoff_time: cutoff time value
        """
        self.data[self.cutoff_time_key] = cutoff_time

    def get_status(self: SolverRunStatusInfo) -> str:
        """Access to status."""
        return self.data[self.status_key]

    def get_solver(self: SolverRunStatusInfo) -> str:
        """Access to solver."""
        return self.data[self.solver_key]

    def get_instance(self: SolverRunStatusInfo) -> str:
        """Access to instance."""
        return self.data[self.instance_key]

    def get_cutoff_time(self: SolverRunStatusInfo) -> str:
        """Access to cutoff time."""
        return self.data[self.cutoff_time_key]

    def get_key_string(self: SolverRunStatusInfo) -> str:
        """Create key string."""
        return (f"{self.get_solver()}_"
                f"{self.get_instance()}_"
                f"{sbh.get_time_pid_random_string()}")


class ConfigureSolverStatusInfo(StatusInfo):
    """Status info for configure solver jobs."""
    job_path = StatusInfoType.CONFIGURE_SOLVER
    solver_key = "Solver"
    instance_set_train_key = "Training Instance"
    instance_set_test_key = "Test Instance"

    def set_solver(self: ConfigureSolverStatusInfo, solver: str) -> None:
        """Sets the solver attribute.

        Args:
            solver: solver value
        """
        self.data[self.solver_key] = solver

    def set_instance_set_train(self: ConfigureSolverStatusInfo, instance_set_train: str)\
            -> None:
        """Sets the training set name.

        Args:
            instance_set_train: name of the training instance set
        """
        self.data[self.instance_set_train_key] = instance_set_train

    def set_instance_set_test(self: ConfigureSolverStatusInfo, instance_set_test: str)\
            -> None:
        """Sets the test set name.

        Args:
            instance_set_test: name of the test instance set
        """
        self.data[self.instance_set_test_key] = instance_set_test

    def get_instance_set_test(self: ConfigureSolverStatusInfo) -> str:
        """Access to the test instance set name."""
        return self.data[self.instance_set_test_key]

    def get_instance_set_train(self: ConfigureSolverStatusInfo) -> str:
        """Access to training instance set name."""
        return self.data[self.instance_set_train_key]

    def get_solver(self: ConfigureSolverStatusInfo) -> str:
        """Access to solver."""
        return self.data[self.solver_key]

    def get_key_string(self: ConfigureSolverStatusInfo) -> str:
        """Create key string."""
        return (f"{self.get_solver()}_{self.get_instance_set_train()}"
                f"_{self.get_instance_set_test()}")


class ConstructParallelPortfolioStatusInfo(StatusInfo):
    """Status info for construction of parallel portfolios."""
    job_path = StatusInfoType.CONSTRUCT_PARALLEL_PORTFOLIO
    portfolio_name_key = "Portfolio Name"
    list_of_solvers_key = "List of Solvers"

    def set_portfolio_name(self: ConstructParallelPortfolioStatusInfo,
                           portfolio_name: str) -> None:
        """Set the portfolio name.

        Args:
            portfolio_name: name of the portfolio
        """
        self.data[self.portfolio_name_key] = portfolio_name

    def set_list_of_solvers(self: ConstructParallelPortfolioStatusInfo,
                            list_of_solvers: list[str]) -> None:
        """Set the list of solvers.

        Args:
            list_of_solvers: list of solver names
        """
        self.data[self.list_of_solvers_key] = [str(x) for x in list_of_solvers]

    def get_list_of_solvers(self: ConstructParallelPortfolioStatusInfo) -> list[str]:
        """Access to the list of solvers."""
        return self.data[self.list_of_solvers_key]

    def get_portfolio_name(self: ConstructParallelPortfolioStatusInfo) -> str:
        """Access to the portfolio name."""
        return self.data[self.portfolio_name_key]

    def get_key_string(self: ConstructParallelPortfolioStatusInfo) -> str:
        """Create key string."""
        return f"{self.get_portfolio_name()}_{sbh.get_time_pid_random_string()}"
