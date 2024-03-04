#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from pathlib import Path
import sys

from Commands.sparkle_help.configuration_scenario import ConfigurationScenario
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help.sparkle_command_help import CommandName

import runrunner as rrr
from runrunner import Runner
from sparkle.slurm_parsing import SlurmBatch


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self: Configurator, configurator_path: Path) -> None:
        """Initialize Configurator.

        Args:
            configurator_path: Path to the configurator
        """
        self.configurator_path = configurator_path

        if not self.configurator_path.is_dir():
            print(f"The given configurator path '{self.configurator_path}' is not a "
                  "valid directory. Abort")
            sys.exit(-1)

        self.scenario = None

        self.sbatch_filename = ""
        (self.configurator_path / "tmp").mkdir(exist_ok=True)

        self.multiobjective = True
        if configurator_path == sgh.smac_dir:
            self.multiobjective = False

        objectives = sgh.settings.get_general_sparkle_objectives()
        if len(objectives) > 1 and not self.multiobjective:
            print("Warning: Multiple objectives specified but current configurator "
                  f"{self.configurator_path.name} only supports single objective. "
                  f"Defaulted to first specified objective: {objectives[0].name}")

    def create_sbatch_script(self: Configurator,
                             scenario: ConfigurationScenario) -> None:
        """Create sbatch script.

        Args:
            scenario: ConfiguraitonScenario object
        """
        self.scenario = scenario
        self.scenario.create_scenario(parent_directory=self.configurator_path)

        number_of_runs = self.scenario.number_of_runs
        self.sbatch_filename = Path(f"{self.scenario.scenario_file_name}_"
                                    f"{number_of_runs}_exp_sbatch.sh")

        sbatch_options = self._get_sbatch_options()
        params_list = self._get_run_parameter_list()
        srun_command = self._get_srun_command()

        file_content = sbatch_options + params_list + srun_command

        with (self.configurator_path / self.sbatch_filename).open("w+") as sbatch_script:
            sbatch_script.write(file_content)

    def configure(self: Configurator,
                  run_on: Runner = Runner.SLURM) -> int | rrr.slurm.SlurmJob:
        """Submit sbatch script.

        Returns:
            ID of the submitted job. In case of running on RunRunner Slurm, a SlurmJob.
        """
        if run_on == Runner.SLURM:
            return ssh.submit_sbatch_script(self.sbatch_filename,
                                            CommandName.CONFIGURE_SOLVER,
                                            self.configurator_path)
        else:
            jobid = None
            # Remove when RunRunner works satisfactorily
            if run_on == Runner.SLURM_RR:
                run_on = Runner.SLURM

            # code to run through run runner
            sbatch_script_path = self.configurator_path / self.sbatch_filename
            batch = SlurmBatch(sbatch_script_path)
            cmd = batch.cmd + " " + " ".join(batch.cmd_params)
            run = rrr.add_to_queue(
                runner=run_on,
                cmd=cmd,
                name=CommandName.CONFIGURE_SOLVER,
                base_dir=sgh.sparkle_tmp_path,
                path=sgh.smac_dir,
                sbatch_options=batch.sbatch_options,
                srun_options=batch.srun_options)

            if run_on == Runner.SLURM:
                jobid = run
            elif run_on == Runner.LOCAL:
                run.wait()

            # Remove when RunRunner works satisfactorily
            if run_on == Runner.SLURM:
                run_on = Runner.SLURM_RR

            return jobid

    def configuration_callback(self: Configurator,
                               dependency_jobid: str,
                               run_on: Runner = Runner.SLURM) -> str:
        """Callback to be run once configurator is done.

        Returns:
            str: Job id of the callback
        """
        jobid = ""
        cmd = "rm -rf"
        dir_list = self.scenario._clean_up_scenario_dirs()
        for dir in dir_list:
            cmd += " " + str(dir)
        if run_on == Runner.SLURM:
            ssh.generate_generic_callback_slurm_script("configuration_callback",
                                                       self.scenario.solver,
                                                       self.scenario.instance_file_path,
                                                       None,
                                                       dependency_jobid,
                                                       cmd,
                                                       CommandName.CONFIGURE_SOLVER)
        else:
            # Remove once Runrunner is satisfactory
            if run_on == Runner.SLURM_RR:
                run_on = Runner.SLURM

            run = rrr.add_to_queue(
                runner=run_on,
                cmd=cmd,
                name="configuration_callback",
                dependencies=dependency_jobid)

            if run_on == Runner.SLURM:
                jobid = run.run_id
                run_on = Runner.SLURM_RR
            elif run_on == Runner.LOCAL:
                run.wait()

        return jobid

    def _get_sbatch_options(self: Configurator) -> str:
        """Get sbatch options.

        Returns:
            String containing the sbatch options.
        """
        total_jobs = self.scenario.number_of_runs
        maximal_parallel_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
        parallel_jobs = max(maximal_parallel_jobs, total_jobs)

        options = "#!/bin/bash\n"\
                  "###\n"\
                  f"#SBATCH --job-name={self.sbatch_filename}\n"\
                  f"#SBATCH --output=tmp/{self.sbatch_filename}.txt\n"\
                  f"#SBATCH --error=tmp/{self.sbatch_filename}.err\n"\
                  "###\n"\
                  "###\n"\
                  f"#SBATCH --array=0-{total_jobs-1}%{parallel_jobs}\n"\
                  "###\n"

        sbatch_options_list = ssh.get_slurm_options_list()
        for option in sbatch_options_list:
            options += f"#SBATCH {option}\n"
        return options

    def _get_run_parameter_list(self: Configurator) -> str:
        """Get list for SBATCH script containing parameters for all configurator runs.

        Returns:
            String containing the run parameters.
        """
        total_jobs = self.scenario.number_of_runs
        result_directory = Path("results", self.scenario.name)

        sl.add_output(
            f"{sgh.smac_dir}{result_directory}/{self.sbatch_filename}_seed_N_smac.txt",
            f"Configuration log for SMAC run 1 < N <= {total_jobs}")

        params = "params=( \\\n"

        # Use scenario_file_name and two parent directories of it
        scenario_file = Path(self.scenario.directory.parent.name,
                             self.scenario.directory.name,
                             self.scenario.scenario_file_name)
        for seed in range(1, total_jobs + 1):
            result_path = Path(result_directory,
                               f"{self.sbatch_filename}_seed_{seed}_smac.txt")
            smac_execdir_i = Path("scenarios", self.scenario.name, str(seed))
            sl.add_output(sgh.smac_dir + str(result_path),
                          f"Configuration log for SMAC run {seed}")

            params += (f"'{scenario_file} {seed} {result_path} {smac_execdir_i}' \\\n")

        params += ")\n"
        return params

    def _get_srun_command(self: Configurator) -> str:
        """Get srun command.

        Returns:
            String containing the srun command.
        """
        slurm_options = " ".join(ssh.get_slurm_options_list())
        cmd = (f"srun -N1 -n1 {slurm_options} ./each_smac_run_core.sh "
               + "${params[$SLURM_ARRAY_TASK_ID]}\n")
        return cmd
