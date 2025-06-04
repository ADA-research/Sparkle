#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

from __future__ import annotations

from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.platform import generate_report_for_selection as sgfs
from sparkle.types.objective import SparkleObjective
from sparkle.instance import InstanceSet
from sparkle.platform.output.structures import SelectionPerformance, SelectionSolverData

import json
from pathlib import Path


class SelectionOutput:
    """Class that collects selection data and outputs it a JSON format."""

    def __init__(self: SelectionOutput, selection_scenario: Path,
                 train_data: PerformanceDataFrame,
                 feature_data: FeatureDataFrame,
                 training_instances: list[InstanceSet],
                 test_instances: list[InstanceSet],
                 objective: SparkleObjective,
                 cutoff_time: int) -> None:
        """Initialize SelectionOutput class.

        Args:
            selection_scenario: Path to selection output directory
            train_data: The performance input data for the selector
            feature_data: Feature data created by extractor
            training_instances: The set of training instances
            test_instances: The set of test instances
            objective: The objective of the selector
            cutoff_time: The cutoff time
            penalised_time: The penalised time
        """
        if test_instances is not None and not isinstance(test_instances, list):
            test_instances = [test_instances]

        self.training_instances = training_instances
        self.test_instances = test_instances
        self.cutoff_time = cutoff_time

        self.objective = objective
        self.solver_data = self.get_solver_data(train_data, self.objective)
        # Collect marginal contribution data
        self.marginal_contribution_perfect = train_data.marginal_contribution(objective,
                                                                              sort=True)
        self.marginal_contribution_actual = \
            sgfs.compute_selector_marginal_contribution(train_data,
                                                        feature_data,
                                                        selection_scenario,
                                                        objective)

        # Collect performance data
        portfolio_selector_performance_path = selection_scenario / "performance.csv"
        vbs_performance = objective.instance_aggregator(
            train_data.best_instance_performance(objective=objective.name))
        self.performance_data = SelectionPerformance(
            portfolio_selector_performance_path, vbs_performance, self.objective)

    def get_solver_data(self: SelectionOutput,
                        train_data: PerformanceDataFrame,
                        objective: SparkleObjective) -> SelectionSolverData:
        """Initalise SelectionSolverData object."""
        solver_performance_ranking = train_data.get_solver_ranking(objective=objective)
        num_solvers = train_data.num_solvers
        return SelectionSolverData(solver_performance_ranking,
                                   num_solvers)

    def serialise_solvers(self: SelectionOutput,
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

    def serialise_performance(self: SelectionOutput,
                              sp: SelectionPerformance) -> dict:
        """Transform SelectionPerformance to dictionary format."""
        return {
            "vbs_performance": sp.vbs_performance,
            "actual_performance": sp.actual_performance,
            "objective": self.objective.name,
            "metric": sp.metric
        }

    def serialise_instances(self: SelectionOutput,
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

    def serialise_marginal_contribution(self: SelectionOutput) -> dict:
        """Transform performance ranking to dictionary format."""
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

    def serialise(self: SelectionOutput) -> dict:
        """Serialise the selection output."""
        test_data = self.serialise_instances(self.test_instances) if self.test_instances\
            else None
        return {
            "solvers": self.serialise_solvers(self.solver_data),
            "training_instances": self.serialise_instances(self.training_instances),
            "test_instances": test_data,
            "performance": self.serialise_performance(self.performance_data),
            "settings": {"cutoff_time": self.cutoff_time},
            "marginal_contribution": self.serialise_marginal_contribution()
        }

    def write_output(self: SelectionOutput, output: Path) -> None:
        """Write data into a JSON file."""
        output = output / "configuration.json" if output.is_dir() else output
        with output.open("w") as f:
            json.dump(self.serialise(), f, indent=4)
