#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from pathlib import Path
import fcntl

import runrunner as rrr
from runrunner import Runner

from sparkle.configurator.configurator import Configurator
from sparkle.configurator.configuration_scenario import ConfigurationScenario
import global_variables as gv
from sparkle.platform import slurm_help as ssh
from CLI.help.command_help import CommandName
from sparkle.solver.solver import Solver
from sparkle.solver.validator import Validator


class SMACv2(Configurator):
    """Abstact class to use different configurators like SMAC."""

    def __init__(self: SMACv2):
        """Returns the default configurator, Java SMAC V2.10.03."""
        smac_path = Path("Components/smac-v2.10.03-master-778/")
        return super().__init__(
            configurator_path=smac_path,
            executable_path=smac_path / "smac",
            settings_path=Path("Settings/sparkle_smac_settings.txt"),
            result_path=smac_path / "results",
            configurator_target=smac_path / "smac_target_algorithm.py",
            tmp_path=smac_path / "tmp")

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
        self.scenario = scenario
        self.scenario.create_scenario(parent_directory=self.configurator_path)

        scenario_file = Path(self.scenario.directory.parent.name,
                             self.scenario.directory.name,
                             self.scenario.scenario_file_name)
        result_directory = self.result_path / self.scenario.name
        exec_dir_conf = self.configurator_path /\
            Path("scenarios", self.scenario.name, "tmp")
        config_class_output_path = gv.configuration_output_raw / "configuration.csv"
        output = [f"{(result_directory / self.scenario.name).absolute()}"
                  f"_seed_{seed}_smac.txt"
                  for seed in range(self.scenario.number_of_runs)]
        cmds = [f"configurator_cli.py {output[seed]} {config_class_output_path}"
                f"{self.executable_path.absolute()} "
                f"--scenario-file {(self.configurator_path / scenario_file).absolute()} "
                f"--seed {seed} "
                f"--execdir {exec_dir_conf.absolute()}"
                for seed in range(self.scenario.number_of_runs)]

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

        if validate_after and False:
            validator = Validator(out_dir=self.result_path)
            validation_run = validator.validate([scenario.solver],
                                                config_class_output_path,
                                                scenario.instance_directory.name,
                                                dependency=configuration_run,
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
        """Patching method to allow the rebuilding of configuratio scenario."""
        solver = Solver.get_solver_by_name(solver)
        self.scenario = ConfigurationScenario(solver, Path(instance_set_name))
        self.scenario._set_paths(self.configurator_path)

    def organise_output(self: SMACv2, output_source: Path, output_path: Path):
        """Cleans up irrelevant SMAC files and collects output."""
        call_key = self.configurator_target.name
        for line in output_path.open("r").readlines():
            if call_key in line:
                call_str = line.split(call_key, maxsplit=1)[1].strip()
                # The Configuration appears after the first 7 arguments
                configuration = call_str.split(" ", 8)[-1]
                with output_path.open("w") as fout:
                    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
                    current_lines = fout.readlines()
                    current_lines.append(configuration)
                    fout.writelines(current_lines)
                break
