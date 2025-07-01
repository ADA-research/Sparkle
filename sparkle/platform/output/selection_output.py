"""Sparkle class to organise configuration output."""
from __future__ import annotations

from sparkle.selector import SelectionScenario
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
# TODO: This dependency should be removed or the functionality should be moved
from sparkle.CLI.compute_marginal_contribution import \
    compute_selector_marginal_contribution
from sparkle.platform.output.structures import SelectionPerformance, SelectionSolverData

import json
from pathlib import Path


class SelectionOutput:
    """Class that collects selection data and outputs it a JSON format."""

    def __init__(self: SelectionOutput,
                 selection_scenario: SelectionScenario,
                 feature_data: FeatureDataFrame) -> None:
        """Initialize SelectionOutput class.

        Args:
            selection_scenario: Path to selection output directory
            performance_data: The performance data used for the selector
            feature_data: The feature data used for the selector
        """
        self.training_instances = selection_scenario.training_instances
        training_instance_sets = selection_scenario.training_instance_sets
        self.training_instance_sets =\
            [(instance_set, sum(instance_set in s for s in self.training_instances))
             for instance_set in training_instance_sets]
        self.test_instances = selection_scenario.test_instances
        test_sets = selection_scenario.test_instance_sets
        self.test_sets =\
            [(instance_set, sum(instance_set in s for s in self.test_instances))
             for instance_set in test_sets]
        self.cutoff_time = selection_scenario.solver_cutoff
        self.objective = selection_scenario.objective

        solver_performance_data = selection_scenario.selector_performance_data.clone()
        solver_performance_data.remove_solver(SelectionScenario.__selector_solver_name__)

        self.solver_performance_ranking =\
            solver_performance_data.get_solver_ranking(
                instances=self.training_instances,
                objective=self.objective)

        self.solver_data = self.get_solver_data(solver_performance_data)
        self.solvers = {}
        for solver_conf in selection_scenario.performance_data.columns:
            solver, conf = solver_conf.split("_", maxsplit=1)
            if solver not in self.solvers:
                self.solvers[solver] = []
            self.solvers[solver].append(conf)

        self.sbs_performance = solver_performance_data.get_value(
            solver=self.solver_performance_ranking[0][0],
            configuration=self.solver_performance_ranking[0][1],
            instance=self.training_instances,
            objective=self.objective.name)

        # Collect marginal contribution data
        self.marginal_contribution_perfect =\
            solver_performance_data.marginal_contribution(
                selection_scenario.objective,
                instances=self.training_instances,
                sort=True)

        self.marginal_contribution_actual = \
            compute_selector_marginal_contribution(feature_data,
                                                   selection_scenario)
        # Collect performance data
        self.vbs_performance_data = solver_performance_data.best_instance_performance(
            instances=self.training_instances,
            objective=selection_scenario.objective)
        self.vbs_performance = selection_scenario.objective.instance_aggregator(
            self.vbs_performance_data)

        self.test_set_performance = {} if self.test_sets else None
        for (test_set, _) in self.test_sets:
            test_set_instances = [instance for instance in self.test_instances
                                  if test_set in instance]
            test_perf = selection_scenario.selector_performance_data.best_performance(
                exclude_solvers=[
                    s for s in selection_scenario.selector_performance_data.solvers
                    if s != SelectionScenario.__selector_solver_name__],
                instances=test_set_instances,
                objective=selection_scenario.objective
            )
            self.test_set_performance[test_set] = test_perf
        self.actual_performance_data =\
            selection_scenario.selector_performance_data.get_value(
                solver=SelectionScenario.__selector_solver_name__,
                instance=self.training_instances,
                objective=self.objective.name)
        self.actual_performance = self.objective.instance_aggregator(
            self.actual_performance_data)

    def get_solver_data(self: SelectionOutput,
                        train_data: PerformanceDataFrame) -> SelectionSolverData:
        """Initalise SelectionSolverData object."""
        num_solvers = train_data.num_solvers
        return SelectionSolverData(self.solver_performance_ranking,
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
                            instances: list[str]) -> dict:
        """Transform Instances to dictionary format."""
        instance_sets = set(Path(instance).parent.name for instance in instances)
        return {
            "number_of_instance_sets": len(instance_sets),
            "instance_sets": [
                {
                    "name": instance_set,
                    "number_of_instances": sum([1 if instance_set in instance else 0
                                               for instance in instances])
                }
                for instance_set in instance_sets
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
            "settings": {"cutoff_time": self.cutoff_time},
            "marginal_contribution": self.serialise_marginal_contribution()
        }

    def write_output(self: SelectionOutput, output: Path) -> None:
        """Write data into a JSON file."""
        output = output / "configuration.json" if output.is_dir() else output
        with output.open("w") as f:
            json.dump(self.serialise(), f, indent=4)
