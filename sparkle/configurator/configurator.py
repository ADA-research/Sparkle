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
from sparkle.platform import slurm_help as ssh
from CLI.help.command_help import CommandName
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
                  validate_after: bool = True,
                  run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario object
            validate_after: Whether the Validator will be called after the configuration
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        raise NotImplementedError
        self.scenario = scenario
        self.scenario.create_scenario(parent_directory=self.configurator_path)

        scenario_file = Path(self.scenario.directory.parent.name,
                             self.scenario.directory.name,
                             self.scenario.scenario_file_name)
        result_directory = self.result_path / self.scenario.name
        exec_dir_conf = self.configurator_path /\
            Path("scenarios", self.scenario.name, "tmp")
        cmds = [f"{self.executable_path.absolute()} "
                f"--scenario-file {(self.configurator_path / scenario_file).absolute()} "
                f"--seed {seed} "
                f"--execdir {exec_dir_conf.absolute()}"
                for seed in range(1, self.scenario.number_of_runs + 1)]
        output = [f"{(result_directory / self.scenario.name).absolute()}"
                  f"_seed_{seed}_smac.txt"
                  for seed in range(1, self.scenario.number_of_runs + 1)]

        parallel_jobs = max(gv.settings.get_slurm_number_of_runs_in_parallel(),
                            self.scenario.number_of_runs)
        sbatch_options = ssh.get_slurm_options_list()

        configuration_run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name=CommandName.CONFIGURE_SOLVER,
            base_dir=gv.sparkle_tmp_path,
            output_path=output,
            path=self.configurator_path,
            parallel_jobs=parallel_jobs,
            sbatch_options=sbatch_options,
            srun_options=["-N1", "-n1"])

        if validate_after:
            validator = Validator(out_dir=self.result_path)
            validation_run = validator.validate([scenario.solver],
                                                [], #We need to extract the configurations once config run is done
                                                scenario.instance_directory.name,
                                                run_on=run_on)
        elif run_on == Runner.LOCAL:
            configuration_run.wait()

        return configuration_run

    def configuration_callback(self: Configurator,
                               dependency_job: rrr.SlurmRun | rrr.LocalRun,
                               run_on: Runner = Runner.SLURM)\
            -> rrr.SlurmRun | rrr.LocalRun:
        """Callback to clean up once configurator is done.

        Returns:
            rrr.SlurmRun | rrr.LocalRun: Run object of the callback
        """
        raise NotImplementedError
        dir_list = self.scenario._clean_up_scenario_dirs(self.configurator_path)
        cmd = "rm -rf " + " ".join([str(p) for p in dir_list])
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            base_dir=gv.sparkle_tmp_path,
            name=CommandName.CONFIGURE_SOLVER_CALLBACK,
            dependencies=dependency_job,
            sbatch_options=ssh.get_slurm_options_list())

        if run_on == Runner.LOCAL:
            run.wait()

        return run

    def set_scenario_dirs(self: Configurator,
                          solver: str, instance_set_name: str) -> None:
        """Patching method to allow the rebuilding of configuration scenario."""
        raise NotImplementedError
        solver = Solver.get_solver_by_name(solver)
        self.scenario = ConfigurationScenario(solver, Path(instance_set_name))
        self.scenario._set_paths(self.configurator_path)
