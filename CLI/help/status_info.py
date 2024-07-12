"""File containing the Status Info class."""
from __future__ import annotations

import time
from pathlib import Path
import json
import fcntl
from enum import Enum
from typing import Type
from abc import ABC, abstractmethod

import global_variables as gv
import tools.general as tg
from sparkle.platform import tex_help as th


class StatusInfoType(str, Enum):
    """An enum class for different status info types."""
    SOLVER_RUN = "SBATCH_Solver_Run_Jobs"
    CONFIGURE_SOLVER = "SBATCH_Configure_Solver_Jobs"
    CONSTRUCT_PARALLEL_PORTFOLIO = "SBATCH_Construct_Parallel_Portfolio_Jobs"
    CONSTRUCT_PORTFOLIO_SELECTOR = "SBATCH_Construct_Portfolio_Selector_Jobs"
    GENERATE_REPORT = "SBATCH_Generate_Report_Jobs"


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
        self.path = None

    @classmethod
    def from_file(cls: Type[StatusInfo], path: Path) -> StatusInfo:
        """Constructs instance from existing file.

        Args:
            path: path of the statusinfo file
        """
        data = dict(json.load(open(path)))
        status_info = cls()
        status_info.data = data
        status_info.path = path
        return status_info

    @abstractmethod
    def get_key_string(self: StatusInfo) -> str:
        """Method to generate key string."""
        pass

    def save(self: StatusInfo) -> None:
        """Saves the data to the file."""
        key_str = self.get_key_string()
        if self.path is None:
            self.path = Path(f"{gv.sparkle_tmp_path}/"
                             f"{self.job_path}/{key_str}.statusinfo")
            self.path.parent.mkdir(parents=True, exist_ok=True)
        f = self.path.open("w")
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        f.write(json.dumps(self.data))
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def delete(self: StatusInfo) -> None:
        """Deletes the status info file."""
        self.path.unlink()


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


class ConstructPortfolioSelectorStatusInfo(StatusInfo):
    """Status info for construction of portfolio selectors."""
    job_path = StatusInfoType.CONSTRUCT_PORTFOLIO_SELECTOR
    algorithm_selector_path_key = "Algorithm selector path"
    feature_data_csv_path_key = "Feature data csv path"
    performance_data_csv_path_key = "Performance data csv path"

    def set_algorithm_selector_path(self: ConstructPortfolioSelectorStatusInfo,
                                    algorithm_selector_path: str) -> None:
        """Set algorithm selector path."""
        self.data[self.algorithm_selector_path_key] = algorithm_selector_path

    def set_feature_data_csv_path(self: ConstructPortfolioSelectorStatusInfo,
                                  feature_data_csv_path: str) -> None:
        """Set feature data csv path."""
        self.data[self.feature_data_csv_path_key] = feature_data_csv_path

    def set_performance_data_csv_path(self: ConstructPortfolioSelectorStatusInfo,
                                      performance_data_csv_path: str) -> None:
        """Set performance data csv path."""
        self.data[self.performance_data_csv_path_key] = performance_data_csv_path

    def get_performance_data_csv_path(self: ConstructPortfolioSelectorStatusInfo) -> str:
        """"Access to performance data csv path."""
        return self.data[self.performance_data_csv_path_key]

    def get_feature_data_csv_path(self: ConstructPortfolioSelectorStatusInfo) -> str:
        """Access to feature data csv path."""
        return self.data[self.feature_data_csv_path_key]

    def get_algorithm_selector_path(self: ConstructPortfolioSelectorStatusInfo) -> str:
        """Access to algorithm selector path."""
        return self.data[self.algorithm_selector_path_key]

    def get_key_string(self: ConstructPortfolioSelectorStatusInfo) -> str:
        """Create key string."""
        algorithm_selector = self.get_algorithm_selector_path().split("/")[-1]
        feature_data = self.get_feature_data_csv_path().split("/")[-1]
        performance_data = self.get_performance_data_csv_path().split("/")[-1]
        random_string = tg.get_time_pid_random_string()

        return f"{algorithm_selector}_{feature_data}_{performance_data}_{random_string}"


class GenerateReportStatusInfo(StatusInfo):
    """Status info for generation of reports."""
    job_path = StatusInfoType.GENERATE_REPORT
    report_type_key = "Report Type"

    def set_report_type(self: GenerateReportStatusInfo, report_type: th.ReportType)\
            -> None:
        """Set the report type."""
        self.data[self.report_type_key] = report_type

    def get_report_type(self: GenerateReportStatusInfo) -> str:
        """Access to the report type."""
        return self.data[self.report_type_key]

    def get_key_string(self: GenerateReportStatusInfo) -> str:
        """Create key string."""
        return f"{self.get_report_type()}_{tg.get_time_pid_random_string()}"
