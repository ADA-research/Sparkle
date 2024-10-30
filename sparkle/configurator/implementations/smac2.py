#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator classes to implement SMAC2 in Sparkle."""
from __future__ import annotations
from pathlib import Path
import fcntl
import glob
import shutil

import pandas as pd

import runrunner as rrr
from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.solver.validator import Validator
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.types import SparkleObjective


class SMAC2(Configurator):
    """Class for SMAC2 (Java) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/smac-v2.10.03-master-778"
    configurator_executable = configurator_path / "smac"
    configurator_target = configurator_path / "smac_target_algorithm.py"

    version = "2.10.03"
    full_name = "Sequential Model-based Algorithm Configuration"

    def __init__(self: SMAC2,
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
            base_dir=base_dir,
            tmp_path=output_path / "tmp",
            multi_objective_support=False)

    @property
    def name(self: SMAC2) -> str:
        """Returns the name of the configurator."""
        return SMAC2.__name__

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
        if shutil.which("java") is None:
            raise RuntimeError(
                "SMAC2 requires Java 1.8.0_402, but Java is not installed. "
                "Please ensure Java is installed and try again."
            )
        scenario.create_scenario()
        output_csv = scenario.validation / "configurations.csv"
        output_csv.parent.mkdir(exist_ok=True, parents=True)
        output = [f"{(scenario.results_directory).absolute()}/"
                  f"{scenario.name}_seed_{seed}_smac.txt"
                  for seed in range(scenario.number_of_runs)]
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{SMAC2.__name__} {output[seed]} {output_csv.absolute()} "
                f"{SMAC2.configurator_executable.absolute()} "
                f"--scenario-file {scenario.scenario_file_path.absolute()} "
                f"--seed {seed} "
                f"--execdir {scenario.tmp.absolute()}"
                for seed in range(scenario.number_of_runs)]
        parallel_jobs = scenario.number_of_runs
        if num_parallel_jobs is not None:
            parallel_jobs = max(num_parallel_jobs, scenario.number_of_runs)
        runs = [rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name=f"{self.name}: {scenario.solver.name} on {scenario.instance_set.name}",
            base_dir=base_dir,
            path=scenario.results_directory,
            output_path=output,
            parallel_jobs=parallel_jobs,
            sbatch_options=sbatch_options,
            srun_options=["-N1", "-n1"])]

        if validate_after:
            self.validator.out_dir = output_csv.parent
            self.validator.tmp_out_dir = base_dir
            validate_run = self.validator.validate(
                [scenario.solver] * scenario.number_of_runs,
                output_csv,
                [scenario.instance_set],
                [scenario.sparkle_objective],
                scenario.cutoff_time,
                subdir=Path(),
                dependency=runs,
                sbatch_options=sbatch_options,
                run_on=run_on)
            runs.append(validate_run)

        if run_on == Runner.LOCAL:
            for run in runs:
                run.wait()
        return runs

    @staticmethod
    def organise_output(output_source: Path, output_target: Path = None) -> None | str:
        """Retrieves configurations from SMAC files and places them in output."""
        call_key = SMAC2.configurator_target.name
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
    def __init__(self: SMAC2Scenario, solver: Solver,
                 instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective],
                 parent_directory: Path,
                 number_of_runs: int = None,
                 solver_calls: int = None,
                 max_iterations: int = None,
                 cpu_time: int = None,
                 wallclock_time: int = None,
                 cutoff_time: int = None,
                 target_cutoff_length: str = None,
                 use_cpu_time_in_tunertime: bool = None,
                 feature_data_df: pd.DataFrame = None)\
            -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            sparkle_objectives: SparkleObjectives used for each run of the configuration.
                Will be simplified to the first objective.
            parent_directory: Directory in which the scenario should be created.
            number_of_runs: The number of configurator runs to perform
                for configuring the solver.
            solver_calls: The number of times the solver is called for each
                configuration run
            max_iterations: The maximum number of iterations allowed for each
                configuration run. [iteration-limit, numIterations, numberOfIterations]
            cpu_time: The time budget allocated for each configuration run. (cpu)
            wallclock_time: The time budget allocated for each configuration run.
                (wallclock)
            cutoff_time: The maximum time allowed for each individual run during
                configuration.
            target_cutoff_length: A domain specific measure of when the algorithm
                should consider itself done.
            use_cpu_time_in_tunertime: Whether to calculate SMAC2's own used time for
                budget deduction. Defaults in SMAC2 to True.
            feature_data_df: If features are used, this contains the feature data.
                Defaults to None.
        """
        super().__init__(solver, instance_set, sparkle_objectives, parent_directory)
        self.solver = solver
        self.instance_set = instance_set
        self.name = f"{self.solver.name}_{self.instance_set.name}"

        if sparkle_objectives is not None:
            if len(sparkle_objectives) > 1:
                print("WARNING: SMAC2 does not have multi objective support. "
                      "Only the first objective will be used.")
            self.sparkle_objective = sparkle_objectives[0]
        else:
            self.sparkle_objective = None

        self.number_of_runs = number_of_runs
        self.solver_calls = solver_calls
        self.cpu_time = cpu_time
        self.wallclock_time = wallclock_time
        self.cutoff_time = cutoff_time
        self.cutoff_length = target_cutoff_length
        self.max_iterations = max_iterations
        self.use_cpu_time_in_tunertime = use_cpu_time_in_tunertime
        self.feature_data = feature_data_df

        # Scenario Paths
        self.instance_file_path = self.directory / f"{self.instance_set.name}.txt"
        self.tmp = self.directory / "tmp"
        self.validation = self.directory / "validation"
        self.results_directory = self.directory / "results"

        # SMAC2 Specific
        self.outdir_train = self.directory / "outdir_train_configuration"

    def create_scenario(self: SMAC2Scenario) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        # Prepare scenario directory
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)
        # Create empty directories as needed
        self.outdir_train.mkdir()
        self.tmp.mkdir()
        self.results_directory.mkdir(parents=True)  # Prepare results directory

        self._prepare_instances()

        if self.feature_data is not None:
            self._create_feature_file()

        self.create_scenario_file()

    def create_scenario_file(self: SMAC2Scenario) -> Path:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        with self.scenario_file_path.open("w") as file:
            file.write(f"algo = {SMAC2.configurator_target.absolute()} "
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
            if self.max_iterations is not None:
                file.write(f"iteration-limit = {self.max_iterations}\n")
            if self.wallclock_time is not None:
                file.write(f"wallclock-limit = {self.wallclock_time}\n")
            if self.cpu_time is not None:
                file.write(f"cputime-limit = {self.cpu_time}\n")
            if self.solver_calls is not None:
                file.write(f"runcount-limit = {self.solver_calls}\n")
            if self.feature_data is not None:
                file.write(f"feature_file = {self.feature_file_path}\n")
            if self.use_cpu_time_in_tunertime is not None:
                file.write("use-cpu-time-in-tunertime = "
                           f"{self.use_cpu_time_in_tunertime}\n")
            # We don't let SMAC do the validation
            file.write("validation = false" + "\n")
        return self.scenario_file_path

    def _prepare_instances(self: SMAC2Scenario) -> None:
        """Create instance list file without instance specifics."""
        self.instance_file_path.parent.mkdir(exist_ok=True, parents=True)
        with self.instance_file_path.open("w+") as file:
            for instance_path in self.instance_set._instance_paths:
                file.write(f"{instance_path.absolute()}\n")

    def _get_performance_measure(self: SMAC2Scenario) -> str:
        """Retrieve the performance measure of the SparkleObjective.

        Returns:
            Performance measure of the sparkle objective
        """
        if self.sparkle_objective.time:
            return "RUNTIME"
        return "QUALITY"

    def _create_feature_file(self: SMAC2Scenario) -> None:
        """Create CSV file from feature data."""
        self.feature_file_path = Path(self.directory
                                      / f"{self.instance_set.name}_features.csv")
        self.feature_data.to_csv(self.directory
                                 / self.feature_file_path, index_label="INSTANCE_NAME")

    def _clean_up_scenario_dirs(self: SMAC2Scenario,
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

    def serialize_scenario(self: SMAC2Scenario) -> dict:
        """Transform ConfigurationScenario to dictionary format."""
        return {
            "number_of_runs": self.number_of_runs,
            "solver_calls": self.solver_calls,
            "cpu_time": self.cpu_time,
            "wallclock_time": self.wallclock_time,
            "cutoff_time": self.cutoff_time,
            "cutoff_length": self.cutoff_length,
            "max_iterations": self.max_iterations,
            "sparkle_objective": self.sparkle_objective.name,
            "feature_data": self.feature_data,
            "use_cpu_time_in_tunertime": self.use_cpu_time_in_tunertime
        }

    @staticmethod
    def from_file(scenario_file: Path) -> SMAC2Scenario:
        """Reads scenario file and initalises SMAC2Scenario."""
        config = {keyvalue[0]: keyvalue[1]
                  for keyvalue in (line.strip().split(" = ", maxsplit=1)
                                   for line in scenario_file.open().readlines()
                                   if line.strip() != "")}

        # Collect relevant settings
        cpu_time = int(config["cpu_time"]) if "cpu_time" in config else None
        wallclock_limit = int(config["wallclock-limit"]) if "wallclock-limit" in config \
            else None
        solver_calls = int(config["runcount-limit"]) if "runcount-limit" in config \
            else None
        max_iterations = int(config["iteration-limit"]) if "iteration-limit" in config \
            else None
        use_cpu_time_in_tunertime = config["use-cputime-in-tunertime"]\
            if "use-cputime-in-tunertime" in config else None

        _, solver_path, objective_str = config["algo"].split(" ")
        objective = SparkleObjective(objective_str)
        solver = Solver(Path(solver_path.strip()))
        # Extract the instance set from the instance file
        instance_file_path = Path(config["instance_file"])
        instance_set_path = Path(instance_file_path.open().readline().strip()).parent
        instance_set = Instance_Set(Path(instance_set_path))
        results_folder = scenario_file.parent / "results"
        state_run_dirs = [p for p in results_folder.iterdir() if p.is_file()]
        number_of_runs = len(state_run_dirs)
        return SMAC2Scenario(solver,
                             instance_set,
                             [objective],
                             instance_file_path.parent.parent,
                             number_of_runs,
                             solver_calls,
                             max_iterations,
                             cpu_time,
                             wallclock_limit,
                             int(config["cutoffTime"]),
                             config["cutoff_length"],
                             use_cpu_time_in_tunertime)
