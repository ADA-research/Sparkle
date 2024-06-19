#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from abc import abstractmethod
from pathlib import Path

import runrunner as rrr
from runrunner import Runner

from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.solver.solver import Solver
from sparkle.solver.validator import Validator
from sparkle.types.objective import PerformanceMeasure, SparkleObjective


class Configurator:
    """Abstact class to use different configurators like SMAC."""
    configurator_cli_path = Path("sparkle/configurator/configurator_cli.py")

    def __init__(self: Configurator, validator: Validator, output_path: Path,
                 executable_path: Path, settings_path: Path, configurator_target: Path,
                 objectives: list[SparkleObjective], tmp_path: Path = None,
                 multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            validator: Validator object to validate configurations runs
            output_path: Output directory of the Configurator.
            executable_path: Executable of the configurator for Sparkle to call
            settings_path: Path to the settings file for the configurator
            configurator_target: The wrapper algorithm to standardize configurator
                input/output towards solver wrappers.
            objectives: The list of Sparkle Objectives the configurator has to
                optimize.
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.validator = validator
        self.output_path = output_path
        self.executable_path = executable_path
        self.settings_path = settings_path
        self.configurator_target = configurator_target
        self.objectives = objectives
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
                  validator: Validator = None,
                  run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario to execute.
            validator: The validator to run validation with after. If none,
                no validation is performed afterwards.
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        raise NotImplementedError

    @abstractmethod
    def get_optimal_configuration(self: Configurator,
                                  solver: Solver,
                                  instance_set: str,
                                  performance: PerformanceMeasure = None) -> str:
        """Returns the optimal configuration string for a solver of an instance set."""
        raise NotImplementedError

    @staticmethod
    def organise_output(output_source: Path, output_path: Path) -> None:
        """Method to restructure and clean up after a single configurator call."""
        raise NotImplementedError

    def set_scenario_dirs(self: Configurator,
                          solver: str | Solver, instance_set_name: str) -> None:
        """Patching method to allow the rebuilding of configuration scenario."""
        raise NotImplementedError

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError
