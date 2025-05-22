"""Sparkle class to organise configuration output."""
from __future__ import annotations
import json
from pathlib import Path

from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.configurator.configurator import Configurator, ConfigurationScenario


class ConfigurationOutput:
    """Class that collects configuration data and outputs it a JSON format."""

    def __init__(self: ConfigurationOutput,
                 path: Path,
                 configurator: Configurator,
                 config_scenario: ConfigurationScenario,
                 performance_data: PerformanceDataFrame,
                 instance_set_test: InstanceSet,
                 output: Path) -> None:
        """Initialize Configurator Output class.

        Args:
            path: Path to configuration output directory
            configurator: The configurator that was used
            config_scenario: The scenario to output
            performance_data: Performance data
            instance_set_test: Instance set used for testing
            output: Path to the output directory
        """
        self.solver = config_scenario.solver
        self.configurator = configurator
        self.instance_set_train = config_scenario.instance_set
        self.instance_set_test = instance_set_test
        self.directory = path
        self.config_scenario = config_scenario
        self.output = output / "configuration.json" if not output.is_file() else output

        # Fix relative path
        if Path.cwd() in self.solver.directory.parents:
            self.solver = Solver(
                self.solver.directory.relative_to(Path.cwd()),
            )
        if Path.cwd() in self.instance_set_train.directory.parents:
            self.instance_set_train = Instance_Set(
                self.instance_set_train.directory.relative_to(Path.cwd())
            )
        if (self.instance_set_test
                and Path.cwd() in self.instance_set_test.directory.parents):
            self.instance_set_test = Instance_Set(
                self.instance_set_test.directory.relative_to(Path.cwd())
            )
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
            objective=self.config_scenario.sparkle_objective,
            instances=train_instances)

        _, self.default_performance_per_instance_train =\
            performance_data.configuration_performance(
                solver_key, PerformanceDataFrame.default_configuration,
                objective=self.config_scenario.sparkle_objective,
                instances=train_instances,
                per_instance=True)

        self.configurations_performances = [performance_data.configuration_performance(
            solver_key, config,
            objective=self.config_scenario.sparkle_objective,
            instances=train_instances) for config in config_keys]

        # Retrieve best found configuration
        self.best_configuration_key, self.best_performance_train =\
            performance_data.best_configuration(
                solver_key,
                objective=self.config_scenario.sparkle_objective,
                instances=train_instances)
        self.best_configuration = self.all_configurations[config_keys.index(
            self.best_configuration_key)]

        # Retrieve best configuration per instance performances
        _, self.best_conf_performance_per_instance_train =\
            performance_data.configuration_performance(
                solver_key, self.best_configuration_key,
                objective=self.config_scenario.sparkle_objective,
                instances=train_instances,
                per_instance=True)

        if instance_set_test:
            test_instances = [str(p) for p in self.instance_set_test.instance_paths]
            # Retrieve default performance on the test set
            _, self.default_performance_test =\
                performance_data.configuration_performance(
                    solver_key, PerformanceDataFrame.default_configuration,
                    objective=self.config_scenario.sparkle_objective,
                    instances=test_instances)
            _, self.default_performance_per_instance_test =\
                performance_data.configuration_performance(
                    solver_key, PerformanceDataFrame.default_configuration,
                    objective=self.config_scenario.sparkle_objective,
                    instances=test_instances,
                    per_instance=True)
            # Retrieve the best configuration test set performance
            _, self.best_performance_test = performance_data.configuration_performance(
                solver_key, self.best_configuration_key,
                objective=self.config_scenario.sparkle_objective,
                instances=test_instances,
            )
            _, self.best_conf_performance_per_instance_test =\
                performance_data.configuration_performance(
                    solver_key, self.best_configuration_key,
                    objective=self.config_scenario.sparkle_objective,
                    instances=test_instances,
                    per_instance=True)
        self.performance_data = performance_data

    def write_output(self: ConfigurationOutput) -> None:
        """Write data into a JSON file."""
        output_data = {
            "solver": self.solver.name,
            "configurator": self.configurator.name,
            "best_configuration": self.best_configuration,
            "best_performance_train": self.best_performance_train,
            "scenario": self.config_scenario.serialize()
            if self.configurator.scenario else None,
            "train_set_results": self.performance_data[self.performance_data.index.isin(
                [str(p) for p in self.instance_set_train.instance_paths],
                level=PerformanceDataFrame.index_instance)].to_json(),
            "test_set_results": (self.performance_data[self.performance_data.index.isin(
                [str(p) for p in self.instance_set_test.instance_paths],
                level=PerformanceDataFrame.index_instance)].to_json()
                if self.instance_set_test else None),
        }
        self.output.parent.mkdir(parents=True, exist_ok=True)
        with self.output.open("w") as f:
            json.dump(output_data, f, indent=4)
