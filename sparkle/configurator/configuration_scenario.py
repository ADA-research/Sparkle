#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Class to handle all activities around configuration scenarios."""


from __future__ import annotations
import shutil
from pathlib import Path

import pandas as pd

from sparkle.types.objective import SparkleObjective, PerformanceMeasure
from sparkle.solver.solver import Solver


class ConfigurationScenario:
    """Class to handle all activities around configuration scenarios."""
    def __init__(self: ConfigurationScenario, solver: Solver, instance_directory: Path,
                 number_of_runs: int = None, time_budget: int = None,
                 cutoff_time: int = None, cutoff_length: int = None,
                 sparkle_objective: SparkleObjective = None, use_features: bool = None,
                 configurator_target: Path = None, feature_data_df: pd.DataFrame = None)\
            -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_directory: Original directory of instances.
            number_of_runs: The number of configurator runs to perform
                for configuring the solver.
            time_budget: The time budget allocated for each configuration run.
            cutoff_time: The maximum time allowed for each individual run during
                configuration.
            cutoff_length: The maximum number of iterations allowed for each
                individual run during configuration.
            sparkle_objective: SparkleObjective used for each run of the configuration.
            use_features: Boolean indicating if features should be used.
            configurator_target: The target Python script to be called.
                This script standardises Configurator I/O for solver wrappers.
            feature_data_df: If features are used, this contains the feature data.
                Defaults to None.
        """
        self.solver = solver
        self.instance_directory = instance_directory
        self.name = f"{self.solver.name}_{self.instance_directory.name}"

        self.number_of_runs = number_of_runs
        self.time_budget = time_budget
        self.cutoff_time = cutoff_time
        self.cutoff_length = cutoff_length
        self.sparkle_objective = sparkle_objective
        self.use_features = use_features
        self.configurator_target = configurator_target
        self.feature_data = feature_data_df

        self.parent_directory = Path()
        self.directory = Path()
        self.result_directory = Path()
        self.scenario_file_name = ""
        self.feature_file_path = Path()
        self.instance_file_path = Path()

    def create_scenario(self: ConfigurationScenario, parent_directory: Path) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        self._set_paths(parent_directory)

        self._prepare_scenario_directory()
        self._prepare_result_directory()
        self._prepare_instances()

        if self.use_features:
            self._create_feature_file()

        self._create_scenario_file()

    def _set_paths(self: ConfigurationScenario, parent_directory: Path) -> None:
        self.parent_directory = parent_directory
        self.directory = self.parent_directory / "scenarios" / self.name
        self.result_directory = self.parent_directory / "results" / self.name
        self.instance_file_path = (
            Path(self.parent_directory / "scenarios"
                 / "instances" / self.instance_directory.name)
            / Path(str(self.instance_directory.name + "_train.txt")))

    def _prepare_scenario_directory(self: ConfigurationScenario) -> None:
        """Delete old scenario dir, recreate it, create empty dirs inside."""
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)

        # Create empty directories as needed
        (self.directory / "outdir_train_configuration").mkdir()
        (self.directory / "tmp").mkdir()

        shutil.copy(self.solver.get_pcs_file(), self.directory)

    def _prepare_result_directory(self: ConfigurationScenario) -> None:
        """Delete possible files in result directory."""
        shutil.rmtree(self.result_directory, ignore_errors=True)
        self.result_directory.mkdir(parents=True)

    def _create_scenario_file(self: ConfigurationScenario) -> None:
        """Create a file with the configuration scenario."""
        inner_directory = Path("scenarios", self.name)

        performance_measure = self._get_performance_measure()
        solver_param_file_path = inner_directory / self.solver.get_pcs_file().name
        config_output_directory = inner_directory / "outdir_train_configuration"

        scenario_file_path = (self.directory
                              / f"{self.name}_scenario.txt")
        self.scenario_file_name = scenario_file_path.name
        with scenario_file_path.open("w") as file:
            file.write(f"algo = {self.configurator_target.absolute()} "
                       f"{self.solver.directory.absolute()}\n"
                       f"execdir = {inner_directory}/\n"
                       f"deterministic = {self.solver.is_deterministic()}\n"
                       f"run_obj = {performance_measure}\n"
                       f"wallclock-limit = {self.time_budget}\n"
                       f"cutoffTime = {self.cutoff_time}\n"
                       f"cutoff_length = {self.cutoff_length}\n"
                       f"paramfile = {solver_param_file_path}\n"
                       f"outdir = {config_output_directory}\n"
                       f"instance_file = {self.instance_file_path.absolute()}\n"
                       f"test_instance_file = {self.instance_file_path.absolute()}\n")
            if self.use_features:
                file.write(f"feature_file = {self.feature_file_path}\n")
            file.write("validation = true" + "\n")

    def _prepare_instances(self: ConfigurationScenario) -> None:
        """Create instance list file."""
        source_instance_list = (
            [f for f in self.instance_directory.rglob("*") if f.is_file()])

        self.instance_file_path.parent.mkdir(exist_ok=True, parents=True)
        with self.instance_file_path.open("w+") as file:
            for instance_path in source_instance_list:
                file.write(f"{instance_path.absolute()}\n")

    def _get_performance_measure(self: ConfigurationScenario) -> str:
        """Retrieve the performance measure of the SparkleObjective.

        Returns:
            Performance measure of the sparkle objective
        """
        run_performance_measure = self.sparkle_objective.PerformanceMeasure

        if run_performance_measure == PerformanceMeasure.RUNTIME:
            run_performance_measure = run_performance_measure.name
        elif run_performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
            run_performance_measure = "QUALITY"
        else:
            print("Warning: Unknown performance measure", run_performance_measure,
                  "! This is a bug in Sparkle.")

        return run_performance_measure

    def _create_feature_file(self: ConfigurationScenario) -> None:
        """Create CSV file from feature data."""
        self.feature_file_path = Path(self.directory
                                      / f"{self.instance_directory.name}_features.csv")
        self.feature_data.to_csv(self.directory
                                 / self.feature_file_path, index_label="INSTANCE_NAME")

    def _clean_up_scenario_dirs(self: ConfigurationScenario,
                                configurator_path: Path) -> list[Path]:
        """Yield directories to clean up after configuration scenario is done.

        Returns:
            list[str]: Full paths to directories that can be removed
        """
        result = []
        configurator_solver_path = configurator_path / "scenarios"\
            / f"{self.solver.name}_{self.instance_directory.name}"

        for index in range(self.number_of_runs):
            dir = configurator_solver_path / str(index + 1)
            result.append(dir)
        return result
