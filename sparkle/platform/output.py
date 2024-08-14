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
from sparkle.types.objective import SparkleObjective

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
    def __init__(self: ValidationResults, solver: Solver, configuration: dict,
                 instance_set: str,
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
                 res_def: ValidationResults, res_conf: ValidationResults) -> None:
        """Initalize ConfigurationResults.

        Args:
            performance: The performance of the default and configured solver
            res_def: The default results
            res_conf: The configured results
        """
        self.performance = performance
        self.configured_results = res_conf
        self.default_results = res_def


class ConfigurationOutput:
    """Class that collects configuration data and outputs it a json format."""
    solver: Solver = None
    configurator: Configurator = None
    best_config: str = None
    training: ConfigurationResults = None
    test: ConfigurationResults = None

    instance_set_test: InstanceSet = None

    def __init__(self: ConfigurationOutput, path: Path, solver_dir: Path,
                 solver_name: str, configurator: Configurator,
                 instance_dir: Path,
                 penalty_multiplier: int, output: Path = None) -> None:
        """Initialize Configurator Output class.

        Args:
            path: Path to configuration output directory
            solver_dir: Path to the solver directory
            solver_name: Name of the solver that was used
            configurator: The configurator that was used
            instance_dir: Path to the instance directory
            penalty_multiplier: penalty multiplier that is applied to the par performance
            output: Path to the output directory
        """
        self.solver = resolve_object_name(solver_name,
                                          gv.solver_nickname_mapping,
                                          solver_dir, Solver)
        self.configurator = configurator
        self.penalty_multiplier = penalty_multiplier
        self.directory = path
        self.instance_dir = instance_dir

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
        self.initalise_scenario(scenario_file)
        # Retrieves validation results and best configuration
        self.training, self.best_config =\
            self.get_validation_data(self.configurator.scenario.instance_set)
        # Retrieve test validation results if they exist
        if self.instance_set_test is not None:
            self.test, _ = self.get_validation_data(self.instance_set_test)

        self.write_output()

    def initalise_scenario(self: ConfigurationOutput, scenario_file: Path) -> None:
        """Reads scenario file and initalises ConfigurationScenario."""
        config = {}
        with scenario_file.open() as file:
            for line in file:
                key, value = line.strip().split(" = ")
                config[key] = value

        instance_set_train = resolve_object_name(
            config["instance_file"],
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            self.instance_dir, InstanceSet)
        # TODO: Find out why _train.txt is added to end of name
        # Remove .txt to not cause any issues with later use of
        # name in self.configurator.scenario._set_paths()
        instance_set_train.name = instance_set_train.name.replace("_train", "")

        # Set instance_set_test to later retrieve validation results
        instance_set_test = resolve_object_name(
            config["test_instance_file"],
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            self.instance_dir, InstanceSet)
        if instance_set_test is not None:
            self.instance_set_test = instance_set_test

        # Collect relevant settings
        if "cpu_time" in config:
            cpu_time = int(config["cpu_time"])
        else:
            cpu_time = None

        if "wallclock-limit" in config:
            wallclock_limit = int(config["wallclock-limit"])
        else:
            wallclock_limit = None

        if "runcount-limit" in config:
            solver_calls = int(config["runcount-limit"])
        else:
            solver_calls = None

        if "feature_file" in config:
            use_features = bool(config["feature_file"])
        else:
            use_features = None

        # TODO: Add METRIC to objective
        objective = SparkleObjective(f"{config['run_obj']}:UNKNOWN")

        # TODO: Number_of_runs isn't part of the scenario file
        self.configurator.scenario = ConfigurationScenario(self.solver,
                                                           instance_set_train,
                                                           None,
                                                           solver_calls,
                                                           cpu_time,
                                                           wallclock_limit,
                                                           int(config["cutoffTime"]),
                                                           config["cutoff_length"],
                                                           objective,
                                                           use_features)
        self.configurator.scenario._set_paths(self.configurator.output_path)

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
        results_default = ValidationResults(self.solver, val_default[0][1],
                                            val_default[0][2], results)

        results = []
        # Form: 0: solver, 1: config, 2: set, 3: instance, 4: status,
        # 5: quality, 6: runtime
        for res in val_conf:
            # TODO: status to enum
            results.append([res[3], res[4], res[5], res[6]])
        results_conf = ValidationResults(self.solver, val_conf[0][1],
                                         val_conf[0][2], results)

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
                    "instance_set": cr.configured_results.instance_set,
                    "result_header": cr.configured_results.result_header,
                    "result_vals": cr.configured_results.result_vals,
                },
                "default_results": {
                    "solver": cr.default_results.solver.name,
                    "configuration": cr.default_results.configuration,
                    "instance_set": cr.default_results.instance_set,
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
    solver_dir = gv.settings.DEFAULT_solver_dir
    instance_dir = gv.settings.DEFAULT_instance_dir
    configurator = gv.settings.get_general_sparkle_configurator()
    penalty_multiplier = gv.settings.get_general_penalty_multiplier()
    ConfigurationOutput(path, solver_dir, "PbO-CCSAT-Generic", configurator,
                        instance_dir, penalty_multiplier)
