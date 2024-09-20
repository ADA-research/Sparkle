#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

from __future__ import annotations

from sparkle.platform import \
    generate_report_for_configuration as sgrfch
from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver.validator import Validator
from sparkle.platform.output.structures import ValidationResults, ConfigurationResults
from sparkle.types import SolverStatus

import json
from pathlib import Path


class ConfigurationOutput:
    """Class that collects configuration data and outputs it a JSON format."""

    def __init__(self: ConfigurationOutput, path: Path, solver: Solver,
                 configurator: Configurator, instance_set_train: InstanceSet,
                 instance_set_test: InstanceSet, output: Path) -> None:
        """Initialize Configurator Output class.

        Args:
            path: Path to configuration output directory
            solver: Solver object
            configurator: The configurator that was used
            instance_set_train: Instance set used for training
            instance_set_test: Instance set used for testing
            output: Path to the output directory
        """
        self.solver = solver
        self.configurator = configurator
        self.instance_set_train = instance_set_train
        self.instance_set_test = instance_set_test
        self.directory = path
        self.output = output / "configuration.json" if not output.is_file() else output

        solver_dir_name = path.name
        scenario_file = path / f"{solver_dir_name}_scenario.txt"
        if not scenario_file.is_file():
            raise Exception("Can't find scenario file")

        # Sets scenario on configurator object
        self.configurator.scenario = \
            configurator.scenario_class.from_file(scenario_file, self.solver,
                                                  self.instance_set_train)
        self.configurator.scenario._set_paths(self.configurator.output_path)

        # Retrieve all configurations
        config_path = path / "validation" / "configurations.csv"
        self.configurations = self.get_configurations(config_path)

        # Retrieve best found configuration
        objective = self.configurator.scenario.sparkle_objective
        _, self.best_config = self.configurator.get_optimal_configuration(
            self.solver, self.instance_set_train, objective)

        # Retrieves validation results for all configurations
        self.validation_results = []
        for config in self.configurations:
            val_res = self.get_validation_data(self.instance_set_train,
                                               config)
            self.validation_results.append(val_res)

        # Retrieve test validation results if they exist
        if self.instance_set_test is not None:
            self.validation_results_test = []
            for config in self.configurations:
                val_res = self.get_validation_data(self.instance_set_test,
                                                   config)
                self.validation_results_test.append(val_res)

    def get_configurations(self: ConfigurationOutput, config_path: Path) -> list[dict]:
        """Read all configurations and transform them to dictionaries."""
        configs = []
        # Check if the path exists and is a file
        if config_path.exists() and config_path.is_file():
            with config_path.open("r") as file:
                for line in file:
                    config = Solver.config_str_to_dict(line.strip())
                    if config not in configs:
                        configs.append(config)
        return configs

    def get_validation_data(self: ConfigurationOutput, instance_set: InstanceSet,
                            config: dict) -> ConfigurationResults:
        """Returns best config and ConfigurationResults for instance set."""
        objective = self.configurator.scenario.sparkle_objective

        # Retrieve found configuration
        _, best_config = self.configurator.get_optimal_configuration(
            self.solver, instance_set, objective)

        # Retrieve validation results
        validator = Validator(self.directory)
        val_results = validator.get_validation_results(
            self.solver, instance_set, config=best_config,
            source_dir=self.directory, subdir="validation")
        header = val_results[0]
        results = []
        value_column = header.index(objective.name)
        instance_column = header.index("Instance")
        status_column = header.index("Status")
        cpu_time_column = header.index("CPU Time")
        wall_time_column = header.index("Wallclock Time")
        for res in val_results[1:]:
            results.append([res[instance_column], SolverStatus(res[status_column]),
                            res[value_column], res[cpu_time_column],
                            res[wall_time_column]])
        final_results = ValidationResults(self.solver, config,
                                          instance_set, results)
        perf_par = sgrfch.get_average_performance(val_results,
                                                  objective)
        return ConfigurationResults(perf_par,
                                    final_results)

    def serialize_configuration_results(self: ConfigurationOutput,
                                        cr: ConfigurationResults) -> dict:
        """Transform ConfigurationResults to dictionary format."""
        return {
            "performance": cr.performance,
            "results": {
                "solver": cr.results.solver.name,
                "configuration": cr.results.configuration,
                "instance_set": cr.results.instance_set.name,
                "result_header": cr.results.result_header,
                "result_values": cr.results.result_vals,
            },
        }

    def serialize_scenario(self: ConfigurationOutput,
                           scenario: ConfigurationScenario) -> dict:
        """Transform ConfigurationScenario to dictionary format."""
        return {
            "number_of_runs": scenario.number_of_runs,
            "solver_calls": scenario.solver_calls,
            "cpu_time": scenario.cpu_time,
            "wallclock_time": scenario.wallclock_time,
            "cutoff_time": scenario.cutoff_time,
            "cutoff_length": scenario.cutoff_length,
            "sparkle_objective": scenario.sparkle_objective.name,
            "use_features": scenario.use_features,
            "configurator_target": scenario.configurator_target,
            "feature_data": scenario.feature_data,
        }

    def write_output(self: ConfigurationOutput) -> None:
        """Write data into a JSON file."""
        output_data = {
            "solver": self.solver.name if self.solver else None,
            "configurator": (
                str(self.configurator.executable_path) if self.configurator else None
            ),
            "best_configuration": Solver.config_str_to_dict(self.best_config),
            "configurations": self.configurations,
            "scenario": self.serialize_scenario(self.configurator.scenario)
            if self.configurator.scenario else None,
            "training_results": [
                self.serialize_configuration_results(validation_result)
                for validation_result in self.validation_results
            ],
            "test_set": (
                [
                    self.serialize_configuration_results(validation_result)
                    for validation_result in self.validation_results_test
                ]
                if self.instance_set_test else None
            ),
        }

        self.output.parent.mkdir(parents=True, exist_ok=True)
        with self.output.open("w") as f:
            json.dump(output_data, f, indent=4)
