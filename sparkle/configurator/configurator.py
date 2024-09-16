#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different algorithm configurators like SMAC."""

from __future__ import annotations
from abc import abstractmethod
from pathlib import Path

from runrunner import Runner, Run

from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.solver import Solver
from sparkle.solver.validator import Validator
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective


class Configurator:
    """Abstact class to use different configurators like SMAC."""
    configurator_cli_path = Path(__file__).parent.resolve() / "configurator_cli.py"

    def __init__(self: Configurator, validator: Validator, output_path: Path,
                 executable_path: Path, configurator_target: Path,
                 objectives: list[SparkleObjective], base_dir: Path, tmp_path: Path,
                 multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            validator: Validator object to validate configurations runs
            output_path: Output directory of the Configurator.
            executable_path: Executable of the configurator for Sparkle to call
            configurator_target: The wrapper algorithm to standardize configurator
                input/output towards solver wrappers.
            objectives: The list of Sparkle Objectives the configurator has to
                optimize.
            base_dir: Where to execute the configuration
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.validator = validator
        self.output_path = output_path
        self.executable_path = executable_path
        self.configurator_target = configurator_target
        self.objectives = objectives
        self.base_dir = base_dir
        self.tmp_path = tmp_path
        self.multiobjective = multi_objective_support
        self.scenario = None
        if len(self.objectives) > 1 and not self.multiobjective:
            print("Warning: Multiple objectives specified but current configurator "
                  f"{self.configurator_path.name} only supports single objective. "
                  f"Defaulted to first specified objective: {self.objectives[0].name}")

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

    @abstractmethod
    def get_optimal_configuration(self: Configurator,
                                  solver: Solver,
                                  instance_set: InstanceSet,
                                  objective: SparkleObjective) -> tuple[float, str]:
        """Returns the optimal configuration string for a solver of an instance set."""
        raise NotImplementedError

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
