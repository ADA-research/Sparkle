#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from pathlib import Path
import sys

import runrunner as rrr
from runrunner import Runner

from Commands.structures.configuration_scenario import ConfigurationScenario
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help import sparkle_job_help as sjh
from Commands.sparkle_help.sparkle_command_help import CommandName


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self: Configurator, configurator_path: Path, executable_path: Path,
                 settings_path: Path, result_path: Path, tmp_path: Path = None,
                 multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            configurator_path: Path to the configurator directory
            executable_path: Executable of the configurator for Sparkle to call
            settings_path: Path to the settings file for the configurator
            result_path: Path for the result files of the configurator
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.configurator_path = configurator_path
        self.settings_path = settings_path
        self.result_path = result_path
        self.tmp_path = tmp_path
        self.executable_path = executable_path
        self.multiobjective = multi_objective_support

        if not self.configurator_path.is_dir():
            print(f"The given configurator path '{self.configurator_path}' is not a "
                  "valid directory. Abort")
            sys.exit(-1)

        self.scenario = None
        self.sbatch_filename = ""
        (self.configurator_path / "tmp").mkdir(exist_ok=True)

        self.objectives = sgh.settings.get_general_sparkle_objectives()
        if len(self.objectives) > 1 and not self.multiobjective:
            print("Warning: Multiple objectives specified but current configurator "
                  f"{self.configurator_path.name} only supports single objective. "
                  f"Defaulted to first specified objective: {self.objectives[0].name}")

    def configure(self: Configurator,
                  scenario: ConfigurationScenario,
                  run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario object
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        self.scenario = scenario
        self.scenario.create_scenario(parent_directory=self.configurator_path)

        scenario_file = Path(self.scenario.directory.parent.name,
                             self.scenario.directory.name,
                             self.scenario.scenario_file_name)
        result_directory = Path("results", self.scenario.name)
        cmds = [f"./each_smac_run_core.sh {scenario_file} {seed} "
                f"{result_directory / f'{self.sbatch_filename}_seed_{seed}_smac.txt'} "
                f"{Path('scenarios', self.scenario.name, str(seed) )}"
                for seed in range(1, self.scenario.number_of_runs + 1)]

        parallel_jobs = max(sgh.settings.get_slurm_number_of_runs_in_parallel(),
                            self.scenario.number_of_runs)
        sbatch_options = ssh.get_slurm_options_list()
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name=CommandName.CONFIGURE_SOLVER,
            base_dir=sgh.sparkle_tmp_path,
            path=sgh.smac_dir,
            parallel_jobs=parallel_jobs,
            sbatch_options=sbatch_options,
            srun_options=["-N1", "-n1"])
        if run_on == Runner.LOCAL:
            run.wait()
        else:
            sjh.write_active_job(run.run_id, CommandName.CONFIGURE_SOLVER)
        return run

    def configuration_callback(self: Configurator,
                               dependency_job: rrr.SlurmRun | rrr.LocalRun,
                               run_on: Runner = Runner.SLURM)\
            -> rrr.SlurmRun | rrr.LocalRun:
        """Callback to be run once configurator is done.

        Returns:
            rrr.SlurmRun | rrr.LocalRun: Run object of the callback
        """
        dir_list = self.scenario._clean_up_scenario_dirs()
        cmd = "rm -rf " + " ".join([str(p) for p in dir_list])
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            base_dir=sgh.sparkle_tmp_path,
            name=CommandName.CONFIGURE_SOLVER_CALLBACK,
            dependencies=dependency_job,
            sbatch_options=ssh.get_slurm_options_list())

        if run_on == Runner.LOCAL:
            run.wait()
        else:
            sjh.write_active_job(run.run_id, CommandName.CONFIGURE_SOLVER_CALLBACK)
        return run

    @staticmethod
    def smac_v2() -> Configurator:
        """Returns the default configurator, Java SMAC V2.10.03."""
        smac_path = Path("Components/smac-v2.10.03-master-778/")
        return Configurator(
            configurator_path=smac_path,
            executable_path=smac_path / "smac_target_algorithm.py",
            settings_path=Path("Settings/sparkle_smac_settings.txt"),
            result_path=smac_path / "results",
            tmp_path=smac_path / "tmp")
