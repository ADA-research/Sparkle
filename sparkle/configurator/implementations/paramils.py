"""Configurator class to use different configurators like SMAC."""

from __future__ import annotations
# from typing import Callable
from pathlib import Path
# import ast
# from statistics import mean
# import operator
import fcntl
# import glob
import shutil

# import pandas as pd

from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective


class ParamILS(Configurator):
    """Class for ParamILS (Ruby) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/paramils2.3.8-source"
    configurator_executable = configurator_path / "param_ils_2_3_run.rb"
    target_algorithm = "paramils_target_algorithm.py"
    configurator_target = configurator_path / target_algorithm

    def __init__(self: ParamILS,
                 base_dir: Path,
                 output_path: Path) -> None:
        """Returns the ParamILS (Ruby) configurator, V2.3.8.

        Args:
            base_dir: The path where the configurator will be executed in.
            output_path: The path where the output will be placed.
        """
        output_path = output_path / ParamILS.__name__
        output_path.mkdir(parents=True, exist_ok=True)
        return super().__init__(
            output_path=output_path,
            base_dir=base_dir,
            tmp_path=output_path / "tmp",
            multi_objective_support=False)

    @property
    def name(self: ParamILS) -> str:
        """Returns the name of the configurator."""
        return ParamILS.__name__

    @staticmethod
    def scenario_class() -> ParamILSScenario:
        """Returns the ParamILS scenario class."""
        return ParamILSScenario

    def configure(self: ParamILS,
                  scenario: ParamILSScenario,
                  data_target: PerformanceDataFrame,
                  validate_after: bool = True,
                  sbatch_options: list[str] = [],
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> list[Run]:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario object
            data_target: PerformanceDataFrame where to store the found configurations
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
        seeds = data_target.run_ids[data_target.num_runs - scenario.number_of_runs:]
        output = [f"{(self.scenario.result_directory).absolute()}/"
                  f"{self.scenario.name}_seed_{seed}_paramils.txt"
                  for seed in seeds]
        # execdir timeout should go to another place
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{ParamILS.__name__} {output[seed]} {output_csv.absolute()} "
                f"{ParamILS.configurator_executable.absolute()} "
                f"-scenariofile {(self.scenario.scenario_file_path).absolute()} "
                f"-numRun {seed} "
                f"-outdir {output[seed]}"
                for seed in seeds]

        if num_parallel_jobs is not None:
            num_parallel_jobs = max(num_parallel_jobs, len(cmds))

        return super().configure(
            configuration_commands=cmds,
            data_target=data_target,
            output=output,
            num_parallel_jobs=num_parallel_jobs,
            scenario=scenario,
            validation_ids=seeds if validate_after else None,
            sbatch_options=sbatch_options,
            base_dir=base_dir,
            run_on=run_on
        )

    @staticmethod
    def organise_output(output_source: Path, output_target: Path = None) -> None | str:
        """Retrieves configurations from SMAC files and places them in output."""
        call_key = ParamILS.target_algorithm
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

    def get_status_from_logs(self: ParamILS) -> None:
        """Method to scan the log files of the configurator for warnings."""
        return


class ParamILSScenario(ConfigurationScenario):
    """Class to handle ParamILS configuration scenarios."""

    def __init__(self: ParamILSScenario, solver: Solver,
                 instance_set: InstanceSet,
                 tuner_timeout: int = None, cutoff_time: int = None,
                 cutoff_length: int = None,
                 sparkle_objectives: list[SparkleObjective] = None)\
            -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            execdir: The execution directroy.
            outdir: Output directory.
            instance_set: Instances object for the scenario.
            tuner_timeout: The time budget allocated for each configuration run. (cpu)
            cutoff_time: The maximum time allowed for each individual run during
                configuration.
            cutoff_length: The maximum number of iterations allowed for each
                individual run during configuration.
            sparkle_objectives: SparkleObjectives used for each run of the configuration.
                Will be simplified to the first objective.
        """
        super().__init__(solver, instance_set, sparkle_objectives)
        self.solver = solver
        self.instance_set = instance_set
        self.name = f"{self.solver.name}_{self.instance_set.name}"
        self.sparkle_objective = sparkle_objectives[0] if sparkle_objectives else None

        self.tuner_timeout = tuner_timeout
        self.cutoff_time = cutoff_time
        self.cutoff_length = cutoff_length

        self.parent_directory = Path()
        self.directory = Path()
        self.result_directory = Path()
        self.scenario_file_path = Path()

    def create_scenario(self: ParamILSScenario, parent_directory: Path) -> None:
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

    def _set_paths(self: ParamILSScenario, parent_directory: Path) -> None:
        """Set the paths for the scenario based on the specified parent directory."""
        self.parent_directory = parent_directory
        self.directory = self.parent_directory / "scenarios" / self.name
        self.result_directory = self.directory / "results"
        self.outdir_train = self.directory / "outdir_train_configuration"
        self.tmp = self.directory / "tmp"
        self.validation = self.directory / "validation"

    def _prepare_scenario_directory(self: ParamILSScenario) -> None:
        """Delete old scenario dir, recreate it, create empty dirs inside."""
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)

        # Create empty directories as needed
        self.outdir_train.mkdir()
        self.tmp.mkdir()

    def _prepare_result_directory(self: ParamILSScenario) -> None:
        """Delete possible files in result directory."""
        shutil.rmtree(self.result_directory, ignore_errors=True)
        self.result_directory.mkdir(parents=True)

    def _create_scenario_file(self: ParamILSScenario) -> None:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        self.scenario_file_path = self.directory / f"{self.name}_scenario.txt"
        with self.scenario_file_path.open("w") as file:
            file.write(f"algo = {ParamILS.configurator_target.absolute()} "
                       f"{self.solver.directory.absolute()} {self.sparkle_objective} \n"
                       f"execdir = {self.tmp.absolute()}/\n"
                       f"deterministic = {1 if self.solver.deterministic else 0}\n"
                       f"run_obj = {self._get_performance_measure()}\n"
                       f"cutoffTime = {self.cutoff_time}\n"
                       f"cutoff_length = {self.cutoff_length}\n"
                       f"tunerTimeout = {self.tuner_timeout}\n"
                       f"paramfile = {self.solver.get_pcs_file()}\n"
                       f"outdir = {self.outdir_train.absolute()}\n"
                       f"instance_file = {self.instance_file_path.absolute()}\n"
                       f"test_instance_file = {self.instance_file_path.absolute()}\n")
            # We don't let SMAC do the validation
            # file.write("validation = false" + "\n") TODO

    def _prepare_instances(self: ParamILSScenario) -> None:
        """Create instance list file without instance specifics."""
        self.instance_file_path.parent.mkdir(exist_ok=True, parents=True)
        with self.instance_file_path.open("w+") as file:
            for instance_path in self.instance_set._instance_paths:
                file.write(f"{instance_path.absolute()}\n")

    def _get_performance_measure(self: ParamILSScenario) -> str:
        """Retrieve the ParamILS performance measure of the SparkleObjective.

        Returns:
            Performance measure of the sparkle objective
        """
        if self.sparkle_objective.time:
            return "runtime"
        return "approx"

    @staticmethod
    def from_file(scenario_file: Path, solver: Solver, instance_set: InstanceSet,
                  ) -> ParamILSScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        config = {}
        with scenario_file.open() as file:
            for line in file:
                key, value = line.strip().split(" = ")
                config[key] = value

        # Collect relevant settings
        wallclock_limit = int(config["wallclock-limit"]) if "wallclock-limit" in config \
            else None

        objective_str = config["algo"].split(" ")[-1]
        objective = SparkleObjective(objective_str)
        return ParamILSScenario(solver,
                                instance_set,
                                wallclock_limit,
                                int(config["cutoffTime"]),
                                config["cutoff_length"],
                                [objective])
