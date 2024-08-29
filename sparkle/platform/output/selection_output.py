#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

from __future__ import annotations

from sparkle.CLI.help import global_variables as gv
from sparkle.platform.settings_objects import Settings
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.platform import generate_report_for_selection as sgfs
from sparkle.types.objective import SparkleObjective
from sparkle.instance import InstanceSet
from sparkle.platform.output.structures import SelectionPerformance, SelectionSolverData

import json
from pathlib import Path, PurePath


class SelectionOutput:
    """Class that collects selection data and outputs it a JSON format."""

    def __init__(self: SelectionOutput, selection_scenario: Path,
                 train_data: PerformanceDataFrame,
                 feature_data: FeatureDataFrame,
                 training_instances: list[InstanceSet],
                 test_instances: list[InstanceSet],
                 cutoff_time: int, penalised_time: int,
                 output: Path) -> None:
        """Initialize SelectionOutput class.

        Args:
            selection_scenario: Path to selection output directory
            train_data: The performance input data for the selector
            feature_data: Feature data created by extractor
            training_instances: The set of training instances
            test_instances: The set of test instances
            cutoff_time: The cutoff time
            penalised_time: The penalised time
            output: Path to the output directory
        """
        if output.is_dir():
            self.output = output / "selection.json"
        else:
            self.output = output

        self.training_instances = training_instances
        self.test_instances = test_instances
        self.cutoff_time = cutoff_time
        self.penalised_time = penalised_time

        self.objective = SparkleObjective(train_data.objective_names[0])
        self.solver_data = self.get_solver_data(train_data)

        # Collect marginal contribution data
        self.marginal_contribution_perfect = train_data.marginal_contribution(sort=True)
        self.marginal_contribution_actual = \
            sgfs.compute_selector_marginal_contribution(train_data,
                                                        feature_data,
                                                        selection_scenario)

        # Collect performance data
        portfolio_selector_performance_path = selection_scenario / "performance.csv"
        vbs_performance = train_data.best_instance_performance().mean()
        metric = self.objective.metric
        self.performance_data = SelectionPerformance(portfolio_selector_performance_path,
                                                     vbs_performance, metric)

    def get_solver_data(self: SelectionOutput,
                        train_data: PerformanceDataFrame) -> SelectionSolverData:
        """Initalise SelectionSolverData object."""
        solver_performance_ranking = train_data.get_solver_ranking()
        num_solvers = train_data.num_solvers
        return SelectionSolverData(solver_performance_ranking,
                                   num_solvers)

    def serialize_solvers(self: SelectionOutput,
                          sd: SelectionSolverData) -> dict:
        """Transform SelectionSolverData to dictionary format."""
        return {
            "number_of_solvers": sd.num_solvers,
            "single_best_solver": sd.single_best_solver,
            "solver_ranking": [
                {
                    "solver_name": solver[0],
                    "performance": solver[1]
                }
                for solver in sd.solver_performance_ranking
            ]
        }

    def serialize_performance(self: SelectionOutput,
                              sp: SelectionPerformance) -> dict:
        """Transform SelectionPerformance to dictionary format."""
        return {
            "vbs_performance": sp.vbs_performance,
            "actual_PAR": sp.actual_PAR,
            "objective": self.objective.name,
            "metric": sp.metric
        }

    def serialize_instances(self: SelectionOutput,
                            instances: list[InstanceSet]) -> dict:
        """Transform Instances to dictionary format."""
        return {
            "number_of_instance_sets": len(instances),
            "instance_sets": [
                {
                    "name": instance.name,
                    "number_of_instances": instance.size
                }
                for instance in instances
            ]
        }

    def serialize_contribution(self: SelectionOutput) -> dict:
        """Transform marginal contribution ranking to dictionary format."""
        return {
            "marginal_contribution_actual": [
                {
                    "solver_name": ranking[0],
                    "marginal_contribution": ranking[1],
                    "best_performance": ranking[2]
                }
                for ranking in self.marginal_contribution_actual
            ],
            "marginal_contribution_perfect": [
                {
                    "solver_name": ranking[0],
                    "marginal_contribution": ranking[1],
                    "best_performance": ranking[2]
                }
                for ranking in self.marginal_contribution_perfect
            ]
        }

    def serialize_settings(self: SelectionOutput) -> dict:
        """Transform settings to dictionary format."""
        return {
            "cutoff_time": self.cutoff_time,
            "penalised_time": self.penalised_time
        }

    def write_output(self: SelectionOutput) -> None:
        """Write data into a JSON file."""
        output_data = {
            "solvers": self.serialize_solvers(self.solver_data),
            "training_instances": self.serialize_instances(self.training_instances),
            "test_instances": self.serialize_instances(self.test_instances),
            "performance": self.serialize_performance(self.performance_data),
            "settings": self.serialize_settings(),
            "marginal_contribution": self.serialize_contribution()
        }

        self.output.parent.mkdir(parents=True, exist_ok=True)
        with self.output.open("w") as f:
            json.dump(output_data, f, indent=4)
        print("Analysis of selection can be found here: ", self.output)


if __name__ == "__main__":
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    path = Path("Output/Selection/autofolio/CSCCSat_MiniSAT_PbO-CCSAT-Generic")
    train_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
    train_data.penalise(gv.settings().get_general_target_cutoff_time(),
                        gv.settings().get_penalised_time())
    cutoff_time = gv.settings().get_general_target_cutoff_time()
    penalised_time = gv.settings().get_penalised_time()

    train_instances = \
        PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path).instances
    parent_folders = set(Path(instance).parent for instance in train_instances)
    instance_sets = []
    for dir in parent_folders:
        set = InstanceSet(dir)
        instance_sets.append(set)

    test_case_dir = gv.latest_scenario().get_selection_test_case_directory()
    test_set = InstanceSet(Path(test_case_dir))

    output = path / "Analysis" / "selection.json"

    output = SelectionOutput(path, train_data, feature_data, instance_sets,
                             [test_set], cutoff_time, penalised_time, output)
    output.write_output()
