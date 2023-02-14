#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

import shutil
from pathlib import Path

from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_slurm_help as ssh


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self, configurator_path: Path) -> None:
        """Initialize Configurator."""
        self.configurator_path = configurator_path
        self.scenario_directory = ""
        self.result_directory = ""
        self.scenario_file = ""

    def create_scenario(self, solver: Path, source_instance_directory: Path,
                        use_features: bool) -> None:
        """Create scenario with solver and instances."""
        self.scenario_directory = (self.configurator_path / "scenarios"
                                   / f"{solver.name}_{source_instance_directory.name}")
        self.result_directory = (self.configurator_path / "results" 
                                 / f"{solver.name}_{source_instance_directory.name}")
        self._prepare_scenario_directory(solver)
        self._prepare_result_directory()

        self._prepare_run_folders(solver)

        instance_directory = (self.configurator_path / "instances"
                              / source_instance_directory.name)
        instance_directory.mkdir(parents=True, exist_ok=True)
        self._prepare_instances(source_instance_directory, instance_directory)

        self._copy_instance_file_to_scenario(instance_directory)

        self._create_scenario_file(solver.name, source_instance_directory.name,
                                   use_features)

    def create_sbatch_script(self) -> None:
        """Create sbatch script."""
        number_of_runs = sgh.settings.get_config_number_of_runs()
        sbatch_filename = Path(f"{self.scenario_file}_{number_of_runs}_exp_sbatch.sh")

        sbatch_options = self._get_sbatch_options()
        params_list = self._get_run_parameter_list()
        srun_command = self._get_srun_command()

        file_content = sbatch_options + params_list + srun_command

        sbatch_script = open(self.configurator_path / sbatch_filename, "w+")
        sbatch_script.write(file_content)
        sbatch_script.close()

    def configure(self) -> None:
        """Run sbatch script."""
        # Submit SBATCH script
        return

    def _create_scenario_file(self, solver_name: str, instance_set_name: str,
                              use_features: bool) -> None:
        """Create a file with the configuration scenario."""
        is_deterministic = scsh.get_solver_deterministic(solver_name)
        run_objective = ""
        time_budget = sgh.settings.get_config_budget_per_run()
        cutoff_time = sgh.settings.get_general_target_cutoff_time()
        cutoff_length = sgh.settings.get_smac_target_cutoff_length()
        solver_param_file = (
            scsh.get_pcs_file_from_solver_directory(self.scenario_directory))
        solver_param_file_path = self.scenario_directory / solver_param_file
        config_output_directory = self.scenario_directory / "outdir_train_configuration"
        instance_file = self.scenario_directory / f"{instance_set_name}_train.txt"

        scenario_file = (self.scenario_directory
                         / f"{solver_name}_{instance_set_name}_scenario.txt")
        self.scenario_file = scenario_file.name
        file = open(scenario_file, "w")
        file.write(f"algo = ./{sgh.sparkle_smac_wrapper}\n")
        file.write(f"execdir = {self.scenario_directory}/\n")
        file.write(f"deterministic = {is_deterministic}\n")
        file.write(f"run_obj = {run_objective}\n")
        file.write(f"wallclock-limit = {time_budget}\n")
        file.write(f"cutoffTime = {cutoff_time}\n")
        file.write(f"cutoff_length = {cutoff_length}\n")
        file.write(f"paramfile = {solver_param_file_path}\n")
        file.write(f"outdir = {config_output_directory}\n")
        file.write(f"instance_file = {instance_file}\n")
        file.write(f"test_instance_file = {instance_file}\n")
        if use_features:
            feature_file = self.scenario_directory / f"{instance_set_name}_features.csv"
            file.write(f"feature_file = {feature_file}\n")
        file.write("validation = true" + "\n")
        file.close()

    def _prepare_scenario_directory(self, solver_directory: Path) -> None:
        """Delete scenario directory and create empty folders inside."""
        shutil.rmtree(self.scenario_directory, ignore_errors=True)
        self.scenario_directory.mkdir(parents=True)

        # Create empty folders as needed
        (self.scenario_directory / "outdir_train_configuration").mkdir()
        (self.scenario_directory / "tmp").mkdir()

        source_pcs_file = (solver_directory
                           / scsh.get_pcs_file_from_solver_directory(solver_directory))
        shutil.copy(source_pcs_file, self.scenario_directory)

    def _prepare_result_directory(self) -> None:
        """Delete possible files in result directory"""
        shutil.rmtree(self.result_directory, ignore_errors=True)
        self.result_directory.mkdir(parents=True)

    def _prepare_run_folders(self, solver_directory: Path) -> None:
        """Create folders for each configurator run and copy solver files to them."""
        configurator_run_number = sgh.settings.get_config_number_of_runs()
        for i in range(configurator_run_number):
            run_path = self.scenario_directory / str(i+1)

            shutil.copytree(solver_directory, run_path)
            (run_path / "tmp").mkdir(parents=True)

    def _prepare_instances(self, source_instance_directory: Path,
                           instance_directory: Path) -> None:
        """Copy problem instances and create instance list file."""
        source_instance_list = (
            [f for f in source_instance_directory.rglob("*") if f.is_file()])

        shutil.rmtree(instance_directory, ignore_errors=True)
        instance_directory.mkdir()

        self._copy_instances(source_instance_list=source_instance_list,
                             instance_directory=instance_directory)
        self._create_instance_list_file(source_instance_list, instance_directory)

    def _copy_instances(self, source_instance_list: list,
                        instance_directory: Path) -> None:
        """Copy problem instances for configuration to the solver directory."""
        for original_instance_path in source_instance_list:
            target_instance_path = instance_directory / original_instance_path.name
            shutil.copy(original_instance_path, target_instance_path)

    def _create_instance_list_file(self, source_instance_list: list,
                                   instance_directory: Path) -> None:
        """Create file with paths to all instances."""
        instance_list_path = Path(str(instance_directory) + "_train.txt")
        instance_list_path.unlink(missing_ok=True)
        instance_list_file = instance_list_path.open("w+")

        for original_instance_path in source_instance_list:
            instance_list_file.write(f"../../instances/"
                                     f"{original_instance_path.parts[-2]}/"
                                     f"{original_instance_path.name}\n")

        instance_list_file.close()

    def _copy_instance_file_to_scenario(self, instance_directory: Path) -> None:
        """."""
        instance_file_name = Path(str(instance_directory.name + "_train.txt"))
        shutil.copy(self.configurator_path / "instances" / instance_file_name,
                    self.scenario_directory / instance_file_name)

    def _get_sbatch_options(self):
        """Get sbatch options."""
        total_jobs = sgh.settings.get_config_number_of_runs()
        sbatch_script_path = f"{self.scenario_file}_{total_jobs}_exp_sbatch.sh"
        
        maximal_parallel_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
        parallel_jobs = max(maximal_parallel_jobs, total_jobs)

        options = "#!/bin/bash\n"
        options += "###\n"
        options += f"#SBATCH --job-name={sbatch_script_path}\n"
        options += f"#SBATCH --output=tmp/{sbatch_script_path}.txt\n"
        options += f"#SBATCH --error=tmp/{sbatch_script_path}.err\n"
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
        result_directory = Path("results", self.scenario_directory.name)
        sbatch_script_path = f"{self.scenario_file}_{num_job_total}_exp_sbatch.sh"

        sl.add_output(
            f"{sgh.smac_dir}{result_directory}/{sbatch_script_path}_seed_N_smac.txt",
            f"Configuration log for SMAC run 1 < N <= {num_job_total}")

        params = "params=( \\\n"
        for i in range(0, num_job_total):
            seed = i + 1
            result_path = f"{result_directory}/{sbatch_script_path}_seed_{seed}_smac.txt"
            smac_execdir_i = self.scenario_directory / str(seed)
            sl.add_output(sgh.smac_dir + result_path,
                          f"Configuration log for SMAC run {num_job_total}")

            params += (f"'{self.scenario_directory / self.scenario_file} {seed} "
                       f"{result_path} {smac_execdir_i}' \\\n")

        params += ")\n"
        return params

    def _get_srun_command(self):
        """Get srun command."""
        slurm_options = " ".join(ssh.get_slurm_options_list())
        cmd = (f"srun -N1 -n1 {slurm_options} ./each_smac_run_core.sh "
               + "${params[$SLURM_ARRAY_TASK_ID]}\n")
        return cmd
