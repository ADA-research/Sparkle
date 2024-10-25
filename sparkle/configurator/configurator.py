#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different algorithm configurators like SMAC."""
from __future__ import annotations
from abc import abstractmethod
from typing import Callable
import ast
from statistics import mean
import operator
from pathlib import Path

from runrunner import Runner, Run
from sparkle.solver import Solver
from sparkle.solver.validator import Validator
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective


class Configurator:
    """Abstact class to use different configurators like SMAC."""
    configurator_cli_path = Path(__file__).parent.resolve() / "configurator_cli.py"

    def __init__(self: Configurator, validator: Validator, output_path: Path,
                 base_dir: Path, tmp_path: Path,
                 multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            validator: Validator object to validate configurations runs
            output_path: Output directory of the Configurator.
            objectives: The list of Sparkle Objectives the configurator has to
                optimize.
            base_dir: Where to execute the configuration
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.validator = validator
        self.output_path = output_path
        self.base_dir = base_dir
        self.tmp_path = tmp_path
        self.multiobjective = multi_objective_support
        self.scenario = None

    @property
    def scenario_class(self: Configurator) -> ConfigurationScenario:
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

    def get_optimal_configuration(
            self: Configurator,
            scenario: ConfigurationScenario,
            aggregate_config: Callable = mean) -> tuple[float, str]:
        """Returns optimal value and configuration string of solver on instance set."""
        self.validator.out_dir = scenario.validation
        results = self.validator.get_validation_results(
            scenario.solver,
            scenario.instance_set,
            source_dir=scenario.validation,
            subdir=Path())
        # Group the results per configuration
        objective = scenario.sparkle_objective
        value_column = results[0].index(objective.name)
        config_column = results[0].index("Configuration")
        configurations = list(set(row[config_column] for row in results[1:]))
        config_scores = []
        for config in configurations:
            values = [float(row[value_column])
                      for row in results[1:] if row[1] == config]
            config_scores.append(aggregate_config(values))

        comparison = operator.lt if objective.minimise else operator.gt

        # Return optimal value
        min_index = 0
        current_optimal = config_scores[min_index]
        for i, score in enumerate(config_scores):
            if comparison(score, current_optimal):
                min_index, current_optimal = i, score

        # Return the optimal configuration dictionary as commandline args
        config_str = configurations[min_index].strip(" ")
        if config_str.startswith("{"):
            config = ast.literal_eval(config_str)
            config_str = " ".join([f"-{key} '{config[key]}'" for key in config])
        return current_optimal, config_str

    @staticmethod
    def organise_output(output_source: Path, output_target: Path) -> None | str:
        """Method to restructure and clean up after a single configurator call."""
        raise NotImplementedError

    def set_scenario_dirs(self: Configurator,
                          solver: Solver, instance_set: InstanceSet) -> None:
        """Patching method to allow the rebuilding of configuration scenario."""
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
                 parent_directory: Path)\
            -> None:
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

        self.directory = parent_directory / self.name
        self.scenario_file_path = self.directory / f"{self.name}_scenario.txt"
        self.validation: Path = None
        self.tmp: Path = None
        self.results_directory: Path = None

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
                      instance_set: InstanceSet) -> ConfigurationScenario | None:
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
