#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from pathlib import Path
import subprocess

from sparkle_help.configuration_scenario import ConfigurationScenario

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_job_help as sjh
from sparkle_help.sparkle_command_help import CommandName


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self, configurator_path: Path, scenario: ConfigurationScenario) -> None:
        """Initialize Configurator."""
        self.configurator_path = configurator_path
        self.scenario = scenario
        scenario.create_scenario(parent_directory=configurator_path)

        self.sbatch_filename = ""
        (self.configurator_path / "tmp").mkdir(exist_ok=True)

    def create_sbatch_script(self) -> None:
        """Create sbatch script."""
        number_of_runs = sgh.settings.get_config_number_of_runs()
        self.sbatch_filename = Path(f"{self.scenario.scenario_file}_"
                                    f"{number_of_runs}_exp_sbatch.sh")

        sbatch_options = self._get_sbatch_options()
        params_list = self._get_run_parameter_list()
        srun_command = self._get_srun_command()

        file_content = sbatch_options + params_list + srun_command

        sbatch_script = open(self.configurator_path / self.sbatch_filename, "w+")
        sbatch_script.write(file_content)
        sbatch_script.close()

    def configure(self) -> int:
        """Submit sbatch script."""
        command = ["sbatch", self.sbatch_filename]

        output = subprocess.run(command, cwd=self.configurator_path, capture_output=True,
                                text=True)
        if output.stderr != "":
            print("An error occured during the script submission:")
            print(output.stderr)
            print("Depending on the error, the configurator might still run.")
        job_id = output.stdout.split()[-1]
        sjh.write_active_job(job_id, CommandName.CONFIGURE_SOLVER)

        print(f"Job running with id {job_id}.")
        return job_id

    def _get_sbatch_options(self):
        """Get sbatch options."""
        total_jobs = sgh.settings.get_config_number_of_runs()

        maximal_parallel_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
        parallel_jobs = max(maximal_parallel_jobs, total_jobs)

        options = "#!/bin/bash\n"
        options += "###\n"
        options += f"#SBATCH --job-name={self.sbatch_filename}\n"
        options += f"#SBATCH --output=tmp/{self.sbatch_filename}.txt\n"
        options += f"#SBATCH --error=tmp/{self.sbatch_filename}.err\n"
        options += "###\n"
        options += "###\n"
        options += "#SBATCH --mem-per-cpu=3000\n"
        options += f"#SBATCH --array=0-{total_jobs}%{parallel_jobs}\n"
        options += "###\n"

        sbatch_options_list = ssh.get_slurm_options_list()
        for option in sbatch_options_list:
            options += f"#SBATCH {option}\n"

        return options

    def _get_run_parameter_list(self):
        """Get list for SBATCH script containing parameters for all configurator runs."""
        num_job_total = sgh.settings.get_config_number_of_runs()
        result_directory = Path("results", self.scenario.name)

        sl.add_output(
            f"{sgh.smac_dir}{result_directory}/{self.sbatch_filename}_seed_N_smac.txt",
            f"Configuration log for SMAC run 1 < N <= {num_job_total}")

        params = "params=( \\\n"

        scenario_file = Path(self.scenario.directory.parts[-2],
                             self.scenario.directory.parts[-1],
                             self.scenario.scenario_file)
        for i in range(0, num_job_total):
            seed = i + 1
            result_path = Path(result_directory,
                               f"{self.sbatch_filename}_seed_{seed}_smac.txt")
            smac_execdir_i = Path("scenarios", self.scenario.name, str(seed))
            sl.add_output(sgh.smac_dir + str(result_path),
                          f"Configuration log for SMAC run {num_job_total}")

            params += (f"'{scenario_file} {seed} {result_path} {smac_execdir_i}' \\\n")

        params += ")\n"
        return params

    def _get_srun_command(self):
        """Get srun command."""
        slurm_options = " ".join(ssh.get_slurm_options_list())
        cmd = (f"srun -N1 -n1 {slurm_options} ./each_smac_run_core.sh "
               + "${params[$SLURM_ARRAY_TASK_ID]}\n")
        return cmd
