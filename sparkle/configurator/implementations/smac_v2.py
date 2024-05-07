#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from pathlib import Path
import fcntl
import shutil

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
    configurator_path = Path("Components/smac-v2.10.03-master-778/")
    target_algorithm = "smac_target_algorithm.py"

    def __init__(self: SMACv2) -> None:
        """Returns the SMAC configurator, Java SMAC V2.10.03."""
        self.config_class_output_path = gv.configuration_output_raw / SMACv2.__name__
        validator = Validator(out_dir=self.config_class_output_path)
        return super().__init__(
            validator=validator,
            executable_path=SMACv2.configurator_path / "smac",
            settings_path=Path("Settings/sparkle_smac_settings.txt"),
            configurator_target=SMACv2.configurator_path / SMACv2.target_algorithm,
            tmp_path=SMACv2.configurator_path / "tmp")

    def configure(self: Configurator,
                  scenario: ConfigurationScenario,
                  validate_after: bool = True,
                  run_on: Runner = Runner.SLURM) -> list[rrr.SlurmRun | rrr.LocalRun]:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario object
            validate_after: Whether the Validator will be called after the configuration
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        if self.config_class_output_path.exists():
            # Clear the output dir
            shutil.rmtree(self.config_class_output_path)
        self.config_class_output_path.mkdir(parents=True)
        self.scenario = scenario
        self.scenario.create_scenario(parent_directory=self.config_class_output_path)
        output_csv = self.scenario.directory / "validation" / "validation.csv"
        output_csv.parent.mkdir(exist_ok=True, parents=True)
        output = [f"{(self.scenario.result_directory).absolute()}"
                  f"_seed_{seed}_smac.txt"
                  for seed in range(self.scenario.number_of_runs)]
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{SMACv2.__name__} {output[seed]} {output_csv.absolute()}"
                f" {self.executable_path.absolute()} "
                f"--scenario-file {(self.scenario.scenario_file_path).absolute()} "
                f"--seed {seed} "
                f"--execdir {self.scenario.tmp.absolute()}"
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
            path=SMACv2.configurator_path,
            parallel_jobs=parallel_jobs,
            sbatch_options=sbatch_options,
            srun_options=["-N1", "-n1"])
        jobs = [configuration_run]
        if validate_after:
            self.validator.out_dir = output_csv.parent
            validate_jobs = self.validator.validate([scenario.solver],
                                                    output_csv,
                                                    [scenario.instance_directory],
                                                    dependency=configuration_run,
                                                    run_on=run_on)
            jobs += validate_jobs
        if run_on == Runner.LOCAL:
            for job in jobs:
                job.wait()
        return jobs

    def set_scenario_dirs(self: Configurator,
                          solver: str, instance_set_name: str) -> None:
        """Patching method to allow the rebuilding of configuratio scenario."""
        solver = Solver.get_solver_by_name(solver)
        self.scenario = ConfigurationScenario(solver, Path(instance_set_name))
        self.scenario._set_paths(self.config_class_output_path)

    @staticmethod
    def organise_output(output_source: Path, output_target: Path) -> None:
        """Cleans up irrelevant SMAC files and collects output."""
        call_key = SMACv2.target_algorithm
        # Last line describing a call is the best found configuration
        for line in reversed(output_source.open("r").readlines()):
            if call_key in line:
                call_str = line.split(call_key, maxsplit=1)[1].strip()
                # The Configuration appears after the first 7 arguments
                configuration = call_str.split(" ", 8)[-1]
                break
        with output_target.open("a") as fout:
            fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
            fout.write(configuration + "\n")
        # Extract the solver, dataset and seed from output file name
        solver, instanceset, _, seed, _ = output_source.split("_")
        # Clean up the scenario files, reconstructed from the result file
        #NOTE: This could be done in a cleaner way.
        scenario = ConfigurationScenario(solver, Path(instanceset))
        scenario._set_paths(gv.configuration_output_raw / SMACv2.__name__)
        #for clean_path in scenario._clean_up_scenario_dirs(SMACv2.configurator_path):
        #    shutil.rmtree(clean_path)
