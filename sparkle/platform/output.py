#!/usr/bin/env python3
"""Sparkle class to organise output."""

from __future__ import annotations

from sparkle.CLI.help import global_variables as gv
from sparkle.platform import \
    generate_report_for_configuration as sgrfch
from sparkle.platform.settings_objects import Settings
from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.configurator.configurator import Configurator
from sparkle.solver.validator import Validator

from sparkle.CLI.help.nicknames import resolve_object_name

import os
import json
from pathlib import Path
from runrunner.base import Status


class ConfigurationPerformance:
    """Class that stores performance results."""
    def __init__(self: ConfigurationPerformance, configured_metrics: float,
                 default_metrics: float) -> None:
        """Initalize ConfigurationPerformance.

        Args:
            configured_metrics: The performance of the configured solver
            default_metrics: The performance result of the default solver
        """
        self.configured_metrics = configured_metrics
        self.default_metrics = default_metrics


class ValidationResults:
    """Class that stores validation information and results."""
    def __init__(self: ValidationResults, solver: Solver,
                 configuration: dict, instance_set: InstanceSet,
                 results: list[list[str, Status, float, float]]) -> None:
        """Initalize ValidationResults.

        Args:
            solver: The name of the solver
            configuration: The configuration being used
            instance_set: The set of instances
            results: Validation results in the format:
                [["instance", "status", "quality", "runtime"]]
        """
        self.solver = solver
        self.configuration = configuration
        self.instance_set = instance_set
        self.result_header = ["instance", "status", "quality", "runtime"]
        self.result_vals = results


class ConfigurationResults:
    """Class that aggregates configuration results."""
    def __init__(self: ConfigurationResults, performance: ConfigurationPerformance,
                 results_default: ValidationResults,
                 results_configured: ValidationResults) -> None:
        """Initalize ConfigurationResults.

        Args:
            performance: The performance of the default and configured solver
            results_default: The default results
            results_configured: The configured results
        """
        self.performance = performance
        self.configured_results = results_configured
        self.default_results = results_default


class ConfigurationOutput:
    """Class that collects configuration data and outputs it a json format."""
    solver: Solver = None
    configurator: Configurator = None
    best_config: dict = None
    training: ConfigurationResults = None
    test: ConfigurationResults = None

    def __init__(self: ConfigurationOutput, path: Path, solver: Solver,
                 configurator: Configurator, instance_set_train: InstanceSet,
                 instance_set_test: InstanceSet,
                 penalty_multiplier: int, output: Path = None) -> None:
        """Initialize Configurator Output class.

        Args:
            path: Path to configuration output directory
            solver: Solver object
            configurator: The configurator that was used
            instance_set_train: Instance set used for training
            instance_set_test: Instance set used for testing
            penalty_multiplier: penalty multiplier that is applied to the par performance
            output: Path to the output directory
        """
        self.solver = solver
        self.configurator = configurator
        self.instance_set_train = instance_set_train
        self.instance_set_test = instance_set_test
        self.penalty_multiplier = penalty_multiplier
        self.directory = path

        if output is None:
            output = path / "Analysis" / "configuration.json"
        self.output = output

        # TODO: Fix this spaghetti code to find the scenario file
        solver_dir_name = path.name
        scenario_dir = path / "outdir_train_configuration" / \
            f"{solver_dir_name}_scenario" / "state-run0"
        if scenario_dir.is_dir():
            scenario_file = scenario_dir / "scenario.txt"
            if not scenario_file.is_file():
                print("Can't find scenario file")
                return
        else:
            print("Can't find scenario file")
            return

        # Sets scenario on configurator object
        self.configurator.scenario = \
            ConfigurationScenario.from_file(scenario_file, self.solver,
                                            self.instance_set_train)
        self.configurator.scenario._set_paths(self.configurator.output_path)

        # Retrieves validation results and best configuration
        self.training, self.best_config =\
            self.get_validation_data(self.instance_set_train)

        # Retrieve test validation results if they exist
        if self.instance_set_test is not None:
            self.test, _ = self.get_validation_data(self.instance_set_test)

    def parse_string_to_dict(self: ConfigurationOutput, input_string: str) -> dict:
        """Convert a configuration string to a dictionary."""
        result_dict = {}
        input_string = input_string.replace("'", "")
        input_string = input_string.replace(",", "")
        input_string = input_string.replace(":", "")
        input_string = input_string.replace("{", "")
        input_string = input_string.replace("}", "")
        tokens = input_string.split()

        for i in range(0, len(tokens), 2):
            key = tokens[i]
            value = tokens[i + 1]
            result_dict[key] = value

        return result_dict

    def get_validation_data(self: ConfigurationOutput, instance_set: InstanceSet) -> \
            tuple[ConfigurationResults, str]:
        """Returns best config and ConfigurationResults for instance set."""
        objective = self.configurator.scenario.sparkle_objective

        # Retrieve found configuration
        _, best_config = self.configurator.get_optimal_configuration(
            self.solver, instance_set, objective.PerformanceMeasure)

        # Retrieve validation results
        validator = Validator(self.directory)
        val_default = validator.get_validation_results(
            self.solver, instance_set,
            source_dir=self.directory, subdir="validation")
        val_conf = validator.get_validation_results(
            self.solver, instance_set, config=best_config,
            source_dir=self.directory, subdir="validation")

        results = []
        # Form: 0: solver, 1: config, 2: set, 3: instance, 4: status,
        # 5: quality, 6: runtime
        for res in val_default:
            # TODO: status to enum
            results.append([res[3], res[4], res[5], res[6]])
        configuration = self.parse_string_to_dict(val_default[0][1])
        results_default = ValidationResults(self.solver, configuration,
                                            instance_set, results)

        results = []
        # Form: 0: solver, 1: config, 2: set, 3: instance, 4: status,
        # 5: quality, 6: runtime
        for res in val_conf:
            # TODO: status to enum
            results.append([res[3], res[4], res[5], res[6]])
        configuration = self.parse_string_to_dict(val_conf[0][1])
        results_conf = ValidationResults(self.solver, configuration,
                                         instance_set, results)

        cutoff_time = self.configurator.scenario.cutoff_time
        penalty = penalty_multiplier * \
            self.configurator.scenario.cutoff_time
        perf_par_conf = sgrfch.get_par_performance(val_default,
                                                   cutoff_time,
                                                   penalty,
                                                   objective)
        perf_par_def = sgrfch.get_par_performance(val_conf,
                                                  cutoff_time,
                                                  penalty,
                                                  objective)
        performance = ConfigurationPerformance(perf_par_conf, perf_par_def)

        results = ConfigurationResults(performance, results_default, results_conf)
        best_config = self.parse_string_to_dict(best_config)
        return results, best_config

    def write_output(self: ConfigurationOutput) -> None:
        """Write data into a json file."""
        def serialize_configuration_results(cr: ConfigurationResults) -> None:
            return {
                "performance": {
                    "configured_metrics": cr.performance.configured_metrics,
                    "default_metrics": cr.performance.default_metrics,
                },
                "configured_results": {
                    "solver": cr.configured_results.solver.name,
                    "configuration": cr.configured_results.configuration,
                    "instance_set": cr.configured_results.instance_set.name,
                    "result_header": cr.configured_results.result_header,
                    "result_vals": cr.configured_results.result_vals,
                },
                "default_results": {
                    "solver": cr.default_results.solver.name,
                    "configuration": cr.default_results.configuration,
                    "instance_set": cr.default_results.instance_set.name,
                    "result_header": cr.default_results.result_header,
                    "result_vals": cr.default_results.result_vals,
                }
            }

        output_data = {
            "solver": self.solver.name if self.solver else None,
            "configurator": (
                str(self.configurator.executable_path) if self.configurator else None
            ),
            "best_config": self.best_config,
            "training_set": (
                serialize_configuration_results(self.training) if self.training else None
            ),
            "test_set": (
                serialize_configuration_results(self.test) if self.test else None
            ),
        }

        Path(os.path.dirname(self.output)).mkdir(exist_ok=True)
        with self.output.open("w") as f:
            json.dump(output_data, f, indent=4)
        print("Analysis of configuration can be found here: ", self.output)


if __name__ == "__main__":
    global settings
    gv.settings = Settings()

    path = Path("Output/Configuration/Raw_Data/SMAC2/scenarios/PbO-CCSAT-Generic_PTN")
    solver_name = "PbO-CCSAT-Generic"
    solver_dir = gv.settings.DEFAULT_solver_dir
    solver = resolve_object_name(solver_name,
                                 gv.solver_nickname_mapping,
                                 solver_dir, Solver)
    configurator = gv.settings.get_general_sparkle_configurator()
    instance_set_train = gv.latest_scenario().get_config_instance_set_train()
    instance_set_test = gv.latest_scenario().get_config_instance_set_test()
    penalty_multiplier = gv.settings.get_general_penalty_multiplier()
    output = ConfigurationOutput(path, solver, configurator, instance_set_train,
                                 instance_set_test, penalty_multiplier)
    output.write_output()
