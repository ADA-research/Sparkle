#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different algorithm configurators like SMAC."""
from __future__ import annotations
from abc import abstractmethod
from pathlib import Path

from runrunner import Runner, Run
from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective


class Configurator:
    """Abstact class to use different configurators like SMAC."""
    configurator_cli_path = Path(__file__).parent.resolve() / "configurator_cli.py"

    def __init__(self: Configurator, output_path: Path,
                 base_dir: Path, tmp_path: Path,
                 multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            output_path: Output directory of the Configurator.
            objectives: The list of Sparkle Objectives the configurator has to
                optimize.
            base_dir: Where to execute the configuration
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.output_path = output_path
        self.base_dir = base_dir
        self.tmp_path = tmp_path
        self.multiobjective = multi_objective_support
        self.scenario = None

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Return the scenario class of the configurator."""
        return ConfigurationScenario

    @abstractmethod
    def configure(self: Configurator,
                  scenario: ConfigurationScenario,
                  validate_after: bool = True,
                  sbatch_options: list[str] = [],
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> Run:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario to execute.
            validate_after: Whether to validate the configuration on the training set
                afterwards or not.
            sbatch_options: List of slurm batch options to use
            num_parallel_jobs: The maximum number of jobs to run in parallel
            base_dir: The base_dir of RunRunner where the sbatch scripts will be placed
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        raise NotImplementedError

    @staticmethod
    def organise_output(output_source: Path,
                        output_target: Path,
                        scenario: ConfigurationScenario,
                        run_id: int) -> None | str:
        """Method to restructure and clean up after a single configurator call.

        Args:
            output_source: Path to the output file of the configurator run.
            output_target: Path to the Performance DataFrame to store result.
            scenario: ConfigurationScenario of the configuration.
            run_id: ID of the run of the configuration.
        """
        raise NotImplementedError

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError


class ConfigurationScenario:
    """Template class to handle a configuration scenarios."""
    def __init__(self: ConfigurationScenario,
                 solver: Solver,
                 instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective],
                 parent_directory: Path) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            sparkle_objectives: Sparkle Objectives to optimize.
            parent_directory: Directory in which the scenario should be placed.
        """
        self.solver = solver
        self.instance_set = instance_set
        self.sparkle_objectives = sparkle_objectives
        self.name = f"{self.solver.name}_{self.instance_set.name}"

        if self.instance_set.size == 0:
            raise Exception("Cannot configure on an empty instance set "
                            f"('{instance_set.name}').")

        self.directory = parent_directory / self.name
        self.scenario_file_path = self.directory / f"{self.name}_scenario.txt"
        self.validation: Path = self.directory / "validation"
        self.tmp: Path = self.directory / "tmp"
        self.results_directory: Path = self.directory / "results"

    def create_scenario(self: ConfigurationScenario, parent_directory: Path) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        raise NotImplementedError

    def create_scenario_file(self: ConfigurationScenario) -> Path:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        raise NotImplementedError

    def serialize(self: ConfigurationScenario) -> dict:
        """Serialize the configuration scenario."""
        raise NotImplementedError

    @classmethod
    def find_scenario(cls: ConfigurationScenario,
                      directory: Path,
                      solver: Solver,
                      instance_set: InstanceSet) -> ConfigurationScenario:
        """Resolve a scenario from a directory and Solver / Training set."""
        scenario_name = f"{solver.name}_{instance_set.name}"
        path = directory / f"{scenario_name}" / f"{scenario_name}_scenario.txt"
        if not path.exists():
            return None
        return cls.from_file(path)

    @staticmethod
    def from_file(scenario_file: Path) -> ConfigurationScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        raise NotImplementedError
