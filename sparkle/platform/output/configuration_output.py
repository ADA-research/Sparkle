"""Sparkle class to organise configuration output."""
from __future__ import annotations
import json
from pathlib import Path

from sparkle.structures import PerformanceDataFrame
from sparkle.instance import Instance_Set
from sparkle.configurator.configurator import ConfigurationScenario
from sparkle.types import SparkleObjective, SolverStatus


class ConfigurationResult:
    """Class that represents result of configuration on an instance set."""

    def __init__(self: ConfigurationResult,
                 instance_set: str,
                 default_instance_performance: list[float],
                 best_instance_performance: list[float],
                 instance_status_default: dict[str, SolverStatus],
                 instance_status_best: dict[str, SolverStatus],
                 objective: SparkleObjective) -> None:
        """Initialize a configuration result.

        All input sequences are the results per instance.

        Args:
            instance_set: The name of the instance set
            default_instance_performance: The default instance performance
            best_instance_performance: The best instance performance
            performance: The performance of the configuration
            instance_status_default: The status of the default configuration
            instance_status_best: The status of the best configuration
            objective: The objective
        """
        self.default_instance_performance = default_instance_performance
        self.default_performance: float = objective.instance_aggregator(
            default_instance_performance)
        self.best_instance_performance = best_instance_performance
        self.best_performance: float = objective.instance_aggregator(
            best_instance_performance)
        self.instance_status_default = instance_status_default
        self.instance_status_best = instance_status_best
        self.instance_set_name = instance_set

    def serialise(self: ConfigurationResult) -> dict[str, float | list[float]]:
        """Serialise the data."""
        return {
            "instance_set": self.instance_set_name,
            "default_performance": self.default_performance,
            "best_performance": self.best_performance,
            "default_instance_performance": self.default_instance_performance,
            "best_instance_performance": self.best_instance_performance,
            "instance_status_default": self.instance_status_default,
            "instance_status_best": self.instance_status_best
        }


class ConfigurationOutput:
    """Class that collects configuration data and outputs it a JSON format."""

    def __init__(self: ConfigurationOutput,
                 config_scenario: ConfigurationScenario,
                 performance_data: PerformanceDataFrame) -> None:
        """Initialize Configurator Output class.

        Args:
            config_scenario: The scenario to output
            performance_data: Performance data
            instance_set_test: Instance set used for testing
        """
        self.solver = config_scenario.solver
        self.configurator = config_scenario.configurator
        self.instance_set_train = config_scenario.instance_set

        # Filter data on this scenario
        performance_data_config = performance_data.clone()
        performance_data.remove_solver([s for s in performance_data.solvers
                                        if s != str(self.solver.directory)])
        used_configs = config_scenario.configuration_ids + [
            PerformanceDataFrame.default_configuration]
        removable = [c for c in performance_data_config.configuration_ids
                     if c not in used_configs]
        performance_data.remove_configuration(str(self.solver.directory), removable)
        test_sets = set(
            Path(i).parent for i in performance_data.instances
            if self.instance_set_train.name not in i
            and not performance_data.is_missing(str(self.solver.directory), i))
        # NOTE: If we only have one instance from a set, it could lead to problems
        # resolving them like this
        self.test_instance_sets = [Instance_Set(set) for set in test_sets]
        self.directory = config_scenario.directory
        self.config_scenario = config_scenario

        # Retrieve all configurations
        solver_key = str(self.solver.directory)
        config_keys = performance_data.get_configurations(solver_key)
        self.all_configurations = performance_data.get_full_configuration(
            solver_key, config_keys)

        # Retrieve configuration performances
        train_instances = [str(p) for p in self.instance_set_train.instance_paths]
        # Retrieve Default (No configuration) performance
        _, self.default_performance_train = performance_data.configuration_performance(
            solver_key, PerformanceDataFrame.default_configuration,
            objective=self.config_scenario.sparkle_objectives[0],
            instances=train_instances)

        _, self.default_performance_per_instance_train =\
            performance_data.configuration_performance(
                solver_key, PerformanceDataFrame.default_configuration,
                objective=self.config_scenario.sparkle_objectives[0],
                instances=train_instances,
                per_instance=True)

        # Retrieve best found configuration
        self.best_configuration_key, self.best_performance_train =\
            performance_data.best_configuration(
                solver_key,
                objective=self.config_scenario.sparkle_objective,
                instances=train_instances)
        self.best_configuration = self.all_configurations[config_keys.index(
            self.best_configuration_key)]

        # TODO keep all instance set performance data together in a dictionary instead
        # of variables for train and test
        # Shitty hack to get status objective
        status_objective = [o for o in performance_data.objective_names
                            if o.lower().startswith("status")][0]
        self.instance_set_results: dict[str, ConfigurationResult] = {}
        for instance_set in self.test_instance_sets + [self.instance_set_train]:
            instances = [str(p) for p in instance_set.instance_paths]
            _, default_performance_per_instance =\
                performance_data.configuration_performance(
                    solver_key, PerformanceDataFrame.default_configuration,
                    objective=self.config_scenario.sparkle_objective,
                    instances=instances,
                    per_instance=True)
            _, best_conf_performance_per_instance =\
                performance_data.configuration_performance(
                    solver_key, self.best_configuration_key,
                    objective=self.config_scenario.sparkle_objective,
                    instances=instances,
                    per_instance=True)
            instance_status_default = {str(i): performance_data.get_value(
                solver_key,
                configuration=PerformanceDataFrame.default_configuration,
                objective=status_objective,
                instance=[i]) for i in instances}
            instance_status_best_conf = {str(i): performance_data.get_value(
                solver_key,
                configuration=self.best_configuration_key,
                objective=status_objective,
                instance=[i]) for i in instances}
            self.instance_set_results[instance_set.name] = ConfigurationResult(
                instance_set.name,
                default_performance_per_instance,
                best_conf_performance_per_instance,
                instance_status_default,
                instance_status_best_conf,
                self.config_scenario.sparkle_objectives[0]
            )

    def serialise(self: ConfigurationOutput) -> dict:
        """Serialise the configuration output."""
        return {
            "solver": self.solver.name,
            "configurator": self.configurator.name,
            "best_configuration": self.best_configuration,
            "best_performance_train": self.best_performance_train,
            "scenario": self.config_scenario.serialise()
            if self.configurator.scenario else None,
            "train_set_results": self.performance_data[self.performance_data.index.isin(
                [str(p) for p in self.instance_set_train.instance_paths],
                level=PerformanceDataFrame.index_instance)].to_json(),
            "test_set_results": (self.performance_data[self.performance_data.index.isin(
                [str(p) for p in self.test_instance_sets.instance_paths],
                level=PerformanceDataFrame.index_instance)].to_json()
                if self.test_instance_sets else None),
        }

    def write_output(self: ConfigurationOutput, output: Path) -> None:
        """Write data into a JSON file."""
        output = output / "configuration.json" if output.is_dir() else output
        with output.open("w") as f:
            json.dump(self.serialise(), f, indent=4)
