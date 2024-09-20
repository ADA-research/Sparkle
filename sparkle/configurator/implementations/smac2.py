#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
from typing import Callable
from pathlib import Path
import ast
from statistics import mean
import operator
import fcntl
import glob
import shutil

import pandas as pd

import runrunner as rrr
from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.solver.validator import Validator
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective


class SMAC2(Configurator):
    """Class for SMAC2 (Java) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/smac-v2.10.03-master-778"
    target_algorithm = "smac_target_algorithm.py"

    def __init__(self: SMAC2,
                 objectives: list[SparkleObjective],
                 base_dir: Path,
                 output_path: Path) -> None:
        """Returns the SMAC configurator, Java SMAC V2.10.03.

        Args:
            objectives: The objectives to optimize. Only supports one objective.
            base_dir: The path where the configurator will be executed in.
            output_path: The path where the output will be placed.
        """
        output_path = output_path / SMAC2.__name__
        output_path.mkdir(parents=True, exist_ok=True)
        return super().__init__(
            validator=Validator(out_dir=output_path),
            output_path=output_path,
            executable_path=SMAC2.configurator_path / "smac",
            configurator_target=SMAC2.configurator_path / SMAC2.target_algorithm,
            objectives=objectives,
            base_dir=base_dir,
            tmp_path=output_path / "tmp",
            multi_objective_support=False)

    @property
    def scenario_class(self: Configurator) -> ConfigurationScenario:
        """Returns the SMAC2 scenario class."""
        return SMAC2Scenario

    def configure(self: Configurator,
                  scenario: ConfigurationScenario,
                  validate_after: bool = True,
                  sbatch_options: list[str] = [],
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> list[Run]:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario object
            validate_after: Whether the Validator will be called after the configuration
            sbatch_options: List of slurm batch options to use
            num_parallel_jobs: The maximum number of jobs to run parallel.
            base_dir: The path where the sbatch scripts will be created for Slurm.
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        self.scenario = scenario
        self.scenario.create_scenario(parent_directory=self.output_path)
        output_csv = self.scenario.validation / "configurations.csv"
        output_csv.parent.mkdir(exist_ok=True, parents=True)
        output = [f"{(self.scenario.result_directory).absolute()}/"
                  f"{self.scenario.name}_seed_{seed}_smac.txt"
                  for seed in range(self.scenario.number_of_runs)]
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{SMAC2.__name__} {output[seed]} {output_csv.absolute()} "
                f"{self.executable_path.absolute()} "
                f"--scenario-file {(self.scenario.scenario_file_path).absolute()} "
                f"--seed {seed} "
                f"--execdir {self.scenario.tmp.absolute()}"
                for seed in range(self.scenario.number_of_runs)]
        parallel_jobs = self.scenario.number_of_runs
        if num_parallel_jobs is not None:
            parallel_jobs = max(num_parallel_jobs,
                                self.scenario.number_of_runs)
        configuration_run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name="configure_solver",
            base_dir=base_dir,
            output_path=output,
            parallel_jobs=parallel_jobs,
            sbatch_options=sbatch_options,
            srun_options=["-N1", "-n1"])
        runs = [configuration_run]

        if validate_after:
            self.validator.out_dir = output_csv.parent
            self.validator.tmp_out_dir = base_dir
            validate_run = self.validator.validate(
                [scenario.solver] * self.scenario.number_of_runs,
                output_csv.absolute(),
                [scenario.instance_set],
                [self.scenario.sparkle_objective],
                scenario.cutoff_time,
                subdir=Path(),
                dependency=configuration_run,
                sbatch_options=sbatch_options,
                run_on=run_on)
            runs.append(validate_run)

        if run_on == Runner.LOCAL:
            for run in runs:
                run.wait()
        return runs

    def get_optimal_configuration(
            self: Configurator,
            solver: Solver,
            instance_set: InstanceSet,
            objective: SparkleObjective = None,
            aggregate_config: Callable = mean) -> tuple[float, str]:
        """Returns optimal value and configuration string of solver on instance set."""
        if self.scenario is None:
            self.set_scenario_dirs(solver, instance_set)
        results = self.validator.get_validation_results(
            solver,
            instance_set,
            source_dir=self.scenario.validation,
            subdir=self.scenario.validation.relative_to(self.validator.out_dir))
        # Group the results per configuration
        if objective is None:
            objective = self.objectives[0]
        value_column = results[0].index(objective.name)
        config_column = results[0].index("Configuration")
        configurations = list(set(row[config_column] for row in results[1:]))
        config_scores = []
        for config in configurations:
            values = [float(row[value_column])
                      for row in results[1:] if row[1] == config]
            config_scores.append(aggregate_config(values))

        comparison = operator.lt if objective.minimise else operator.gt

        # Return optimal value
        min_index = 0
        current_optimal = config_scores[min_index]
        for i, score in enumerate(config_scores):
            if comparison(score, current_optimal):
                min_index, current_optimal = i, score

        # Return the optimal configuration dictionary as commandline args
        config_str = configurations[min_index].strip(" ")
        if config_str.startswith("{"):
            config = ast.literal_eval(config_str)
            config_str = " ".join([f"-{key} '{config[key]}'" for key in config])
        return current_optimal, config_str

    @staticmethod
    def organise_output(output_source: Path, output_target: Path = None) -> None | str:
        """Retrieves configurations from SMAC files and places them in output."""
        call_key = SMAC2.target_algorithm
        # Last line describing a call is the best found configuration
        for line in reversed(output_source.open("r").readlines()):
            if call_key in line:
                call_str = line.split(call_key, maxsplit=1)[1].strip()
                # The Configuration appears after the first 6 arguments
                configuration = call_str.split(" ", 7)[-1]
                if output_target is None:
                    return configuration
                with output_target.open("a") as fout:
                    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
                    fout.write(configuration + "\n")
                break

    def set_scenario_dirs(self: Configurator,
                          solver: Solver, instance_set: InstanceSet) -> None:
        """Patching method to allow the rebuilding of configuratio scenario."""
        self.scenario = self.scenario_class(solver, instance_set)
        self.scenario._set_paths(self.output_path)

    @staticmethod
    def get_smac_run_obj(objective: SparkleObjective) -> str:
        """Return the SMAC run objective based on the Performance Measure.

        Returns:
            A string that represents the run objective set in the settings.
        """
        if objective.time:
            return "RUNTIME"
        return "QUALITY"

    def get_status_from_logs(self: SMAC2) -> None:
        """Method to scan the log files of the configurator for warnings."""
        base_dir = self.output_path / "scenarios"
        if not base_dir.exists():
            return
        print(f"Checking the log files of configurator {type(self).__name__} for "
              "warnings...")
        scenarios = [f for f in base_dir.iterdir() if f.is_dir()]
        for scenario in scenarios:
            log_dir = scenario / "outdir_train_configuration" \
                / (scenario.name + "_scenario")
            warn_files = glob.glob(str(log_dir) + "/log-warn*")
            non_empty = [log_file for log_file in warn_files
                         if Path(log_file).stat().st_size > 0]
            if len(non_empty) > 0:
                print(f"Scenario {scenario.name} has {len(non_empty)} warning(s), see "
                      "the following log file(s) for more information:")
                for log_file in non_empty:
                    print(f"\t-{log_file}")
            else:
                print(f"Scenario {scenario.name} has no warnings.")


class SMAC2Scenario(ConfigurationScenario):
    """Class to handle SMAC2 configuration scenarios."""
    def __init__(self: ConfigurationScenario, solver: Solver,
                 instance_set: InstanceSet, number_of_runs: int = None,
                 solver_calls: int = None, cpu_time: int = None,
                 wallclock_time: int = None, cutoff_time: int = None,
                 cutoff_length: int = None,
                 sparkle_objectives: list[SparkleObjective] = None,
                 use_features: bool = None, configurator_target: Path = None,
                 feature_data_df: pd.DataFrame = None)\
            -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            number_of_runs: The number of configurator runs to perform
                for configuring the solver.
            solver_calls: The number of times the solver is called for each
                configuration run
            cpu_time: The time budget allocated for each configuration run. (cpu)
            wallclock_time: The time budget allocated for each configuration run.
                (wallclock)
            cutoff_time: The maximum time allowed for each individual run during
                configuration.
            cutoff_length: The maximum number of iterations allowed for each
                individual run during configuration.
            sparkle_objectives: SparkleObjectives used for each run of the configuration.
                Will be simplified to the first objective.
            use_features: Boolean indicating if features should be used.
            configurator_target: The target Python script to be called.
                This script standardises Configurator I/O for solver wrappers.
            feature_data_df: If features are used, this contains the feature data.
                Defaults to None.
        """
        super().__init__(solver, instance_set, sparkle_objectives)
        self.solver = solver
        self.instance_set = instance_set
        self.name = f"{self.solver.name}_{self.instance_set.name}"
        self.sparkle_objective = sparkle_objectives[0] if sparkle_objectives else None

        self.number_of_runs = number_of_runs
        self.solver_calls = solver_calls
        self.cpu_time = cpu_time
        self.wallclock_time = wallclock_time
        self.cutoff_time = cutoff_time
        self.cutoff_length = cutoff_length
        self.use_features = use_features
        self.configurator_target = configurator_target
        self.feature_data = feature_data_df

        self.parent_directory = Path()
        self.directory = Path()
        self.result_directory = Path()
        self.scenario_file_path = Path()
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
        """Set the paths for the scenario based on the specified parent directory."""
        self.parent_directory = parent_directory
        self.directory = self.parent_directory / "scenarios" / self.name
        self.result_directory = self.directory / "results"
        self.instance_file_path = self.directory / f"{self.instance_set.name}.txt"
        self.outdir_train = self.directory / "outdir_train_configuration"
        self.tmp = self.directory / "tmp"
        self.validation = self.directory / "validation"

    def _prepare_scenario_directory(self: ConfigurationScenario) -> None:
        """Delete old scenario dir, recreate it, create empty dirs inside."""
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)

        # Create empty directories as needed
        self.outdir_train.mkdir()
        self.tmp.mkdir()

    def _prepare_result_directory(self: ConfigurationScenario) -> None:
        """Delete possible files in result directory."""
        shutil.rmtree(self.result_directory, ignore_errors=True)
        self.result_directory.mkdir(parents=True)

    def _create_scenario_file(self: ConfigurationScenario) -> None:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        self.scenario_file_path = self.directory / f"{self.name}_scenario.txt"
        with self.scenario_file_path.open("w") as file:
            file.write(f"algo = {self.configurator_target.absolute()} "
                       f"{self.solver.directory.absolute()} {self.sparkle_objective} \n"
                       f"execdir = {self.tmp.absolute()}/\n"
                       f"deterministic = {1 if self.solver.deterministic else 0}\n"
                       f"run_obj = {self._get_performance_measure()}\n"
                       f"cutoffTime = {self.cutoff_time}\n"
                       f"cutoff_length = {self.cutoff_length}\n"
                       f"paramfile = {self.solver.get_pcs_file()}\n"
                       f"outdir = {self.outdir_train.absolute()}\n"
                       f"instance_file = {self.instance_file_path.absolute()}\n"
                       f"test_instance_file = {self.instance_file_path.absolute()}\n")
            if self.use_features:
                file.write(f"feature_file = {self.feature_file_path}\n")
            if self.wallclock_time is not None:
                file.write(f"wallclock-limit = {self.wallclock_time}\n")
            if self.cpu_time is not None:
                file.write(f"cputime-limit = {self.cpu_time}\n")
            if self.solver_calls is not None:
                file.write(f"runcount-limit = {self.solver_calls}\n")
            # We don't let SMAC do the validation
            file.write("validation = false" + "\n")

    def _prepare_instances(self: ConfigurationScenario) -> None:
        """Create instance list file without instance specifics."""
        self.instance_file_path.parent.mkdir(exist_ok=True, parents=True)
        with self.instance_file_path.open("w+") as file:
            for instance_path in self.instance_set._instance_paths:
                file.write(f"{instance_path.absolute()}\n")

    def _get_performance_measure(self: ConfigurationScenario) -> str:
        """Retrieve the performance measure of the SparkleObjective.

        Returns:
            Performance measure of the sparkle objective
        """
        if self.sparkle_objective.time:
            return "RUNTIME"
        return "QUALITY"

    def _create_feature_file(self: ConfigurationScenario) -> None:
        """Create CSV file from feature data."""
        self.feature_file_path = Path(self.directory
                                      / f"{self.instance_set.name}_features.csv")
        self.feature_data.to_csv(self.directory
                                 / self.feature_file_path, index_label="INSTANCE_NAME")

    def _clean_up_scenario_dirs(self: ConfigurationScenario,
                                configurator_path: Path,) -> list[Path]:
        """Yield directories to clean up after configuration scenario is done.

        Returns:
            list[str]: Full paths to directories that can be removed
        """
        result = []
        configurator_solver_path = configurator_path / "scenarios"\
            / f"{self.solver.name}_{self.instance_set.name}"

        for index in range(self.number_of_runs):
            dir = configurator_solver_path / str(index)
            result.append(dir)
        return result

    @staticmethod
    def from_file(scenario_file: Path, solver: Solver, instance_set: InstanceSet,
                  ) -> ConfigurationScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        config = {}
        with scenario_file.open() as file:
            for line in file:
                key, value = line.strip().split(" = ")
                config[key] = value

        # Collect relevant settings
        cpu_time = int(config["cpu_time"]) if "cpu_time" in config else None
        wallclock_limit = int(config["wallclock-limit"]) if "wallclock-limit" in config \
            else None
        solver_calls = int(config["runcount-limit"]) if "runcount-limit" in config \
            else None
        use_features = bool(config["feature_file"]) if "feature_file" in config \
            else None

        objective_str = config["algo"].split(" ")[-1]
        objective = SparkleObjective(objective_str)
        results_folder = scenario_file.parent / "results"
        state_run_dirs = [p for p in results_folder.iterdir() if p.is_file()]
        number_of_runs = len(state_run_dirs)
        return SMAC2Scenario(solver,
                             instance_set,
                             number_of_runs,
                             solver_calls,
                             cpu_time,
                             wallclock_limit,
                             int(config["cutoffTime"]),
                             config["cutoff_length"],
                             [objective],
                             use_features)
