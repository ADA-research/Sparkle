#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

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
from sparkle.output.structures import ValidationResults, ConfigurationResults

from sparkle.CLI.help.nicknames import resolve_object_name

import json
from pathlib import Path


class ConfigurationOutput:
    """Class that collects configuration data and outputs it a JSON format."""

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
                [To be Removed]
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

        scenario_dir = scenario_dir.parent
        # Sets scenario on configurator object
        self.configurator.scenario = \
            ConfigurationScenario.from_file(scenario_file, self.solver,
                                            self.instance_set_train,
                                            scenario_dir)
        self.configurator.scenario._set_paths(self.configurator.output_path)

        # Retrieve all configurations
        self.configurations = self.get_configurations(path)

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

    def get_configurations(self: ConfigurationOutput, path: Path) -> list[dict]:
        """Read all configurations and transform them to dictionaries."""
        config_path = path / "validation" / "configurations.csv"
        configs = []

        # TODO: Should we check if the configurations are unique?
        # Check if the path exists and is a file
        if config_path.exists() and config_path.is_file():
            with config_path.open("r") as file:
                for line in file:
                    config = self.parse_string_to_dict(line.strip())
                    configs.append(config)

        else:
            print("Can't find configurations")

        return configs

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
        results = ConfigurationResults(perf_par_def, perf_par_conf,
                                       results_default, results_conf)
        best_config = self.parse_string_to_dict(best_config)
        return results, best_config

    def serialize_configuration_results(self: ConfigurationOutput,
                                        cr: ConfigurationResults) -> dict:
        """Transform ConfigurationResults to dictionary format."""
        return {
            "performance": {
                "configured_metrics": cr.performance["default_metrics"],
                "default_metrics": cr.performance["configured_metrics"],
            },
            "configured_results": {
                "solver": cr.configured_results.solver.name,
                "configuration": cr.configured_results.configuration,
                "instance_set": cr.configured_results.instance_set.name,
                "result_header": cr.configured_results.result_header,
                "result_values": cr.configured_results.result_vals,
            },
            "default_results": {
                "solver": cr.default_results.solver.name,
                "configuration": cr.default_results.configuration,
                "instance_set": cr.default_results.instance_set.name,
                "result_header": cr.default_results.result_header,
                "result_values": cr.default_results.result_vals,
            }
        }

    def serialize_scenario(self: ConfigurationOutput,
                           cs: ConfigurationScenario) -> dict:
        """Transform ConfigurationScenario to dictionary format."""
        return {
            "number_of_runs": cs.number_of_runs,
            "solver_calls": cs.solver_calls,
            "cpu_time": cs.cpu_time,
            "wallclock_time": cs.wallclock_time,
            "cutoff_time": cs.cutoff_time,
            "cutoff_length": cs.cutoff_length,
            "sparkle_objective": cs.sparkle_objective.name,
            "use_features": cs.use_features,
            "configurator_target": cs.configurator_target,
            "feature_data": cs.feature_data,
        }

    def write_output(self: ConfigurationOutput) -> None:
        """Write data into a JSON file."""
        output_data = {
            "solver": self.solver.name if self.solver else None,
            "configurator": (
                str(self.configurator.executable_path) if self.configurator else None
            ),
            "best_configuration": self.best_config,
            "configurations": self.configurations,
            "scenario": self.serialize_scenario(self.configurator.scenario)
            if self.configurator.scenario else None,
            "training_set": (
                self.serialize_configuration_results(self.training)
                if self.training else None
            ),
            "test_set": (
                self.serialize_configuration_results(self.test) if self.test else None
            ),
        }

        self.output.parent.mkdir(parents=True, exist_ok=True)
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
