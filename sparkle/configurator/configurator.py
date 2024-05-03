#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from pathlib import Path
import sys

import runrunner as rrr
from runrunner import Runner

from sparkle.configurator.configuration_scenario import ConfigurationScenario
import global_variables as gv
from sparkle.solver.solver import Solver
from sparkle.solver.validator import Validator


class Configurator:
    """Abstact class to use different configurators like SMAC."""

    def __init__(self: Configurator, configurator_path: Path, executable_path: Path,
                 settings_path: Path, result_path: Path, configurator_target: Path,
                 tmp_path: Path = None, multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            configurator_path: Path to the configurator directory
            executable_path: Executable of the configurator for Sparkle to call
            settings_path: Path to the settings file for the configurator
            result_path: Path for the result files of the configurator
            configurator_target: The wrapper algorithm to standardize configurator
                input/output towards solver wrappers.
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.configurator_path = configurator_path
        self.executable_path = executable_path
        self.settings_path = settings_path
        self.result_path = result_path
        self.configurator_target = configurator_target
        self.tmp_path = tmp_path
        self.multiobjective = multi_objective_support

        self.scenarios_path = self.configurator_path / "scenarios"
        self.instances_path = self.scenarios_path / "instances"

        if not self.configurator_path.is_dir():
            print(f"The given configurator path '{self.configurator_path}' is not a "
                  "valid directory. Abort")
            sys.exit(-1)

        self.scenario = None
        self.sbatch_filename = ""
        (self.configurator_path / "tmp").mkdir(exist_ok=True)

        self.objectives = gv.settings.get_general_sparkle_objectives()
        if len(self.objectives) > 1 and not self.multiobjective:
            print("Warning: Multiple objectives specified but current configurator "
                  f"{self.configurator_path.name} only supports single objective. "
                  f"Defaulted to first specified objective: {self.objectives[0].name}")

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

    def configuration_callback(self: Configurator,
                               dependency_job: rrr.SlurmRun | rrr.LocalRun,
                               run_on: Runner = Runner.SLURM)\
            -> rrr.SlurmRun | rrr.LocalRun:
        """Callback to clean up once configurator is done.

        Returns:
            rrr.SlurmRun | rrr.LocalRun: Run object of the callback
        """
        raise NotImplementedError

    def organise_output(output_source: Path, output_path: Path):
        """Method to clean up after a single configurator call."""
        raise NotImplementedError

    def set_scenario_dirs(self: Configurator,
                          solver: str | Solver, instance_set_name: str) -> None:
        """Patching method to allow the rebuilding of configuration scenario."""
        raise NotImplementedError
    
