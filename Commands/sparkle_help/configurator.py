#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

import shutil
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self, configurator_path: Path) -> None:
        """Initialize Configurator."""
        self.configurator_path = configurator_path
        self.scenario_directory = ""
        return

    def create_scenario(self, solver: Path, source_instance_directory: Path,
                        use_features: bool) -> None:
        """Create scenario with solver and instances."""
        self.scenario_directory = (self.configurator_path / "scenarios"
                                   / f"{solver.name}_{source_instance_directory.name}")
        self._prepare_scenario_directory(solver)

        instance_directory = (self.configurator_path / "instances"
                              / source_instance_directory.name)
        instance_directory.mkdir(parents=True, exist_ok=True)
        self._prepare_instances(source_instance_directory, instance_directory)

        self._copy_instance_file_to_scenario(instance_directory)

        self._create_scenario_file(solver.name, source_instance_directory.name,
                                   use_features)
        return

    def create_slurm_script(self, solver_name: str, instance_set_train: str,
                            use_features: bool) -> None:
        """Create sbatch script."""
        # Add SBTACH options
        sbatch_options = self._get_sbatch_options__()

        # Add params list
        params_list = self._get_params_list__()

        # Add srun command
        srun_command = self._get_srun_command__()

        file_content = sbatch_options + params_list + srun_command

        return file_content

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

        scenario_file = Path()
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
        return

    def _prepare_scenario_directory(self, solver_directory: Path) -> None:
        """Delete scenario directory and create empty folders inside."""
        shutil.rmtree(self.scenario_directory, ignore_errors=True)
        self.scenario_directory.mkdir(parents=True)
        (self.scenario_directory / "outdir_train_configuration").mkdir()
        (self.scenario_directory / "tmp").mkdir()

        source_pcs_file = (solver_directory
                           / scsh.get_pcs_file_from_solver_directory(solver_directory))
        shutil.copy(source_pcs_file, self.scenario_directory)
        return

    def _prepare_instances(self, source_instance_directory: Path,
                           instance_directory: Path) -> None:
        """Copy problem instances and create instance list file."""
        source_instance_list = (
            [f for f in source_instance_directory.rglob("*") if f.is_file()])

        shutil.rmtree(instance_directory, ignore_errors=True)
        instance_directory.mkdir()

        self._copy_instances(source_instance_list, instance_directory)
        self._create_instance_list_file(source_instance_list, instance_directory)
        return

    def _copy_instances(source_instance_list: list, instance_directory: Path) -> None:
        """Copy problem instances for configuration to the solver directory."""
        for original_instance_path in source_instance_list:
            target_instance_path = instance_directory / original_instance_path.name
            shutil.copy(original_instance_path, target_instance_path)
        return

    def _create_instance_list_file(source_instance_list: list, instance_directory: Path) -> None:
        """Create file with paths to all instances."""
        instance_list_path = Path(str(instance_directory) + "_train.txt")
        instance_list_path.unlink(missing_ok=True)
        instance_list_file = instance_list_path.open("w+")

        for original_instance_path in source_instance_list:
            instance_list_file.write(f"../../instances/"
                                     f"{original_instance_path.parts[-2]}/"
                                     f"{original_instance_path.name}\n")

        instance_list_file.close()
        return

    def _copy_instance_file_to_scenario(self, instance_directory: Path) -> None:
        """."""
        instance_file_name = Path(str(instance_directory.name + "_train.txt"))
        shutil.copy(self.configurator_path / "instances" / instance_file_name,
                    self.scenario_directory / instance_file_name)
        return

    def _get_sbatch_options__(self):
        """Get sbtach options."""
        return

    def _get_params_list__(self):
        """Get parameter list."""
        return

    def _get_srun_command__(self):
        """Get srun command."""
        return
