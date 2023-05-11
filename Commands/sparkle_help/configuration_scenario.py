#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Class to handle all activities around configuration scenarios."""

import shutil
from pathlib import Path

import pandas as pd

from sparkle_help import sparkle_global_help as sgh
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.solver import Solver
from sparkle_help import sparkle_settings


class ConfigurationScenario:
    """Class to handle all activities around configuration scenarios."""
    def __init__(self, solver: Solver, instance_directory: Path,
                 number_of_runs: int, use_features: bool,
                 feature_data_df: pd.DataFrame = None,) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_directory: Original directory of instances.
            number_of_runs: Number of runs used for configuration.
            use_features: Boolean indicating if features should be used.
            feature_data_df: If features are used, this contains the feature data.
                Defaults to None.
        """
        global settings
        sgh.settings = sparkle_settings.Settings()

        self.solver = solver
        self.parent_directory = Path()
        self.instance_directory = instance_directory
        self.number_of_runs = number_of_runs
        self.use_features = use_features
        self.feature_data = feature_data_df
        self.name = f"{self.solver.name}_{self.instance_directory.name}"

        self.directory = Path()
        self.result_directory = Path()
        self.scenario_file_name = ""
        self.feature_file = Path()
        self.instance_file = Path()

    def create_scenario(self, parent_directory: Path) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        self.parent_directory = parent_directory.absolute()
        self.directory = self.parent_directory / "scenarios" / self.name
        self.result_directory = self.parent_directory / "results" / self.name
        self.instance_directory = Path(self.parent_directory / "scenarios" / "instances"
                                       / self.instance_directory.name)
        self.instance_file = (
            self.instance_directory / Path(str(self.instance_directory.name
                                               + "_train.txt")))
        self._prepare_scenario_directory()
        self._prepare_result_directory()

        self._prepare_run_directories()

        self.instance_directory.mkdir(parents=True, exist_ok=True)
        self._prepare_instances()

        if self.use_features:
            self._create_feature_file()

        self._create_scenario_file()

    def _prepare_scenario_directory(self) -> None:
        """Recreate scenario directory and create empty directories inside."""
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)

        # Create empty directories as needed
        (self.directory / "outdir_train_configuration").mkdir()
        (self.directory / "tmp").mkdir()

        shutil.copy(self.solver.get_pcs_file(), self.directory)

    def _prepare_result_directory(self) -> None:
        """Delete possible files in result directory."""
        shutil.rmtree(self.result_directory, ignore_errors=True)
        self.result_directory.mkdir(parents=True)

    def _prepare_run_directories(self) -> None:
        """Create directories for each configurator run and copy solver files to them."""
        for i in range(self.number_of_runs):
            run_path = self.directory / str(i + 1)

            shutil.copytree(self.solver.directory, run_path)
            (run_path / "tmp").mkdir()

    def _create_scenario_file(self) -> None:
        """Create a file with the configuration scenario."""
        inner_directory = Path("scenarios", self.name)

        run_objective = self._get_run_objective()
        time_budget = sgh.settings.get_config_budget_per_run()
        cutoff_time = sgh.settings.get_general_target_cutoff_time()
        cutoff_length = sgh.settings.get_smac_target_cutoff_length()
        solver_param_file_path = inner_directory / self.solver.get_pcs_file().name
        config_output_directory = inner_directory / "outdir_train_configuration"
        instance_file = inner_directory / self.instance_file.name

        scenario_file = (self.directory
                         / f"{self.name}_scenario.txt")
        self.scenario_file_name = scenario_file.name
        file = open(scenario_file, "w")
        file.write(f"algo = ./{sgh.sparkle_smac_wrapper}\n")
        file.write(f"execdir = {inner_directory}/\n")
        file.write(f"deterministic = {self.solver.is_deterministic()}\n")
        file.write(f"run_obj = {run_objective}\n")
        file.write(f"wallclock-limit = {time_budget}\n")
        file.write(f"cutoffTime = {cutoff_time}\n")
        file.write(f"cutoff_length = {cutoff_length}\n")
        file.write(f"paramfile = {solver_param_file_path}\n")
        file.write(f"outdir = {config_output_directory}\n")
        file.write(f"instance_file = {instance_file}\n")
        file.write(f"test_instance_file = {instance_file}\n")
        if self.use_features:
            file.write(f"feature_file = {self.feature_file}\n")
        file.write("validation = true" + "\n")
        file.close()

    def _prepare_instances(self) -> None:
        """Copy problem instances and create instance list file."""
        source_instance_list = (
            [f for f in self.instance_directory.rglob("*") if f.is_file()])

        instance_list_path = self.instance_file

        with instance_list_path.open("w+") as file:
            for original_instance_path in source_instance_list:
                file.write(f"../../instances/"
                           f"{original_instance_path.parts[-2]}/"
                           f"{original_instance_path.name}\n")

    def _get_run_objective(self) -> str:
        """Return the SMAC run objective.

        Returns:
            The run objective from global settings.
        """
        # Get run_obj from general settings
        run_objective = sgh.settings.get_general_performance_measure()

        # Convert to SMAC format
        if run_objective == PerformanceMeasure.RUNTIME:
            run_objective = run_objective.name
        elif run_objective == PerformanceMeasure.QUALITY_ABSOLUTE:
            run_objective = "QUALITY"
        else:
            print("Warning: Unknown performance measure", run_objective,
                  "! This is a bug in Sparkle.")

        return run_objective

    def _create_feature_file(self) -> None:
        """Create CSV file from feature data."""
        self.feature_file = Path(self.directory
                                 / f"{self.instance_directory.name}_features.csv")
        self.feature_data.to_csv(self.directory
                                 / self.feature_file, index_label="INSTANCE_NAME")
