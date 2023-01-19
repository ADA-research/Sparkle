#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

import shutil
from pathlib import Path


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self, configurator_path: Path) -> None:
        """Initialize Configurator."""
        self.configurator_path = configurator_path
        self.scenario_directory = ""
        return

    def create_scenario(self, solver: Path, source_instance_directory: Path) -> None:
        """Create scenario with solver and instances."""
        self.scenario_directory = (self.configurator_path / "scenarios"
                                   / f"{solver.name}_{source_instance_directory.name}")
        self._prepare_scenario_directory(self.scenario_directory)

        instance_directory = (self.configurator_path / "instances"
                              / source_instance_directory.name)
        instance_directory.mkdir(parents=True, exist_ok=True)
        self._copy_instances(source_instance_directory, instance_directory)

        self._copy_instance_file_to_scenario(instance_directory)
        return

    def create_script(self, solver_name: str, instance_set_train: str, use_features: bool) -> None:
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

    def _prepare_scenario_directory(self, scenario_directory: Path) -> None:
        """Delete scenario directory and create empty folders inside."""
        shutil.rmtree(scenario_directory, ignore_errors=True)
        scenario_directory.mkdir(parents=True)
        (scenario_directory / "outdir_train_configuration").mkdir()
        (scenario_directory / "tmp").mkdir()
        return

    def _copy_instances(self, source_instance_directory: Path,
                        instance_directory: Path) -> None:
        """Copy problem instances for configuration to the solver directory."""
        source_instance_list = (
            [f for f in source_instance_directory.rglob("*") if f.is_file()])

        shutil.rmtree(instance_directory, ignore_errors=True)
        instance_directory.mkdir()
        for original_instance_path in source_instance_list:
            target_instance_path = instance_directory / original_instance_path.name
            shutil.copy(original_instance_path, target_instance_path)

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
