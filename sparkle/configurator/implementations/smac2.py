"""Configurator classes to implement SMAC2 in Sparkle."""
from __future__ import annotations
from pathlib import Path
import glob
import shutil
import math

import pandas as pd

from runrunner import Runner, Run

from sparkle.tools.parameters import PCSConvention
from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.types import SparkleObjective, resolve_objective


class SMAC2(Configurator):
    """Class for SMAC2 (Java) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/smac2-v2.10.03-master-778"
    configurator_executable = configurator_path / "smac"
    configurator_target = configurator_path / "smac2_target_algorithm.py"

    version = "2.10.03"
    full_name = "Sequential Model-based Algorithm Configuration"

    def __init__(self: SMAC2,
                 base_dir: Path,
                 output_path: Path) -> None:
        """Returns the SMAC2 configurator, Java SMAC V2.10.03.

        Args:
            objectives: The objectives to optimize. Only supports one objective.
            base_dir: The path where the configurator will be executed in.
            output_path: The path where the output will be placed.
        """
        output_path = output_path / SMAC2.__name__
        output_path.mkdir(parents=True, exist_ok=True)
        return super().__init__(
            output_path=output_path,
            base_dir=base_dir,
            tmp_path=output_path / "tmp",
            multi_objective_support=False)

    @property
    def name(self: SMAC2) -> str:
        """Returns the name of the configurator."""
        return SMAC2.__name__

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Returns the SMAC2 scenario class."""
        return SMAC2Scenario

    def configure(self: SMAC2,
                  scenario: SMAC2Scenario,
                  data_target: PerformanceDataFrame,
                  validate_after: bool = True,
                  sbatch_options: list[str] = [],
                  slurm_prepend: str | list[str] | Path = None,
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> list[Run]:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario object
            data_target: PerformanceDataFrame where to store the found configurations
            validate_after: Whether the configurations should be validated on the
                train set afterwards.
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
        # We set the seed over the last n run ids in the dataframe
        seeds = data_target.run_ids[data_target.num_runs - scenario.number_of_runs:]
        output = [f"{(scenario.results_directory).absolute()}/"
                  f"{scenario.name}_seed_{seed}_smac.txt"
                  for seed in seeds]
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{SMAC2.__name__} {output_file} {data_target.csv_filepath} "
                f"{scenario.scenario_file_path} {seed} "
                f"{SMAC2.configurator_executable.absolute()} "
                f"--scenario-file {scenario.scenario_file_path} "
                f"--seed {seed} "
                for output_file, seed in zip(output, seeds)]
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
            slurm_prepend=slurm_prepend,
            base_dir=base_dir,
            run_on=run_on
        )

    @staticmethod
    def organise_output(output_source: Path,
                        output_target: Path,
                        scenario: SMAC2Scenario,
                        run_id: int) -> None | dict:
        """Retrieves configuration from SMAC file and places them in output."""
        from filelock import FileLock
        call_key = SMAC2.configurator_target.name
        # Last line describing a call is the best found configuration
        for line in reversed(output_source.open("r").readlines()):
            if call_key in line:
                call_str = line.split(call_key, maxsplit=1)[1].strip()
                # The Configuration appears after the first 7 arguments
                configuration = call_str.split(" ", 8)[-1]
                break
        configuration = Solver.config_str_to_dict(configuration)
        if output_target is None or not output_target.exists():
            return configuration
        time_stamp = scenario.scenario_file_path.stat().st_mtime
        configuration["configuration_id"] =\
            f"{SMAC2.__name__}_{time_stamp}_{run_id}"
        instance_names = scenario.instance_set.instance_names
        lock = FileLock(f"{output_target}.lock")
        with lock.acquire(timeout=60):
            performance_data = PerformanceDataFrame(output_target)
            # Resolve absolute path to Solver column
            solver = [s for s in performance_data.solvers
                      if Path(s).name == scenario.solver.name][0]
            # For some reason the instance paths in the instance set are absolute
            instances = [instance for instance in performance_data.instances
                         if Path(instance).name in instance_names]
            # We don't set the seed in the dataframe, as that should be part of the conf
            performance_data.set_value(
                value=[str(configuration)],
                solver=solver,
                instance=instances,
                objective=None,
                run=run_id,
                solver_fields=[PerformanceDataFrame.column_configuration]
            )
            performance_data.save_csv()

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
    def __init__(self: SMAC2Scenario,
                 solver: Solver,
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
                 cli_cores: int = None,
                 use_cpu_time_in_tunertime: bool = None,
                 feature_data: FeatureDataFrame | Path = None)\
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
            cli_cores: int
                The number of cores to use to execute runs. Defaults in SMAC2 to 1.
            use_cpu_time_in_tunertime: Whether to calculate SMAC2's own used time for
                budget deduction. Defaults in SMAC2 to True.
            feature_data: If features are used, this contains the feature data.
                If it is a FeatureDataFrame, will convert values to SMAC2 format.
                If it is a Path, will pass the path to SMAC2.
                Defaults to None.
        """
        super().__init__(solver, instance_set, sparkle_objectives, parent_directory)
        self.solver = solver
        self.instance_set = instance_set
        self.name = f"{self.solver.name}_{self.instance_set.name}"

        if sparkle_objectives is not None:
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
        self.cli_cores = cli_cores
        self.use_cpu_time_in_tunertime = use_cpu_time_in_tunertime

        self.feature_data = feature_data
        self.feature_file_path = None
        if self.feature_data:
            if isinstance(self.feature_data, FeatureDataFrame):
                # Convert feature data to SMAC2 format
                data_dict = {}
                for instance in self.instance_set.instance_paths:
                    data_dict[str(instance)] = feature_data.get_instance(str(instance))

                self.feature_data = pd.DataFrame.from_dict(
                    data_dict, orient="index",
                    columns=[f"Feature{index+1}"
                             for index in range(feature_data.num_features)])

                def map_nan(x: str) -> int:
                    """Map non-numeric values with -512 (Pre-defined by SMAC2)."""
                    if math.isnan(x):
                        return -512.0
                    try:
                        return float(x)
                    except Exception:
                        return -512.0

                self.feature_data = self.feature_data.map(map_nan)
                self.feature_file_path =\
                    self.directory / f"{self.instance_set.name}_features.csv"
            elif isinstance(self.feature_data, Path):  # Read from Path
                self.feature_file_path = feature_data
                self.feature_data = pd.read_csv(self.feature_file_path,
                                                index_col=0)
            else:
                print(f"WARNING: Feature data is of type {type(feature_data)}. "
                      "Expected FeatureDataFrame or Path.")

        # Scenario Paths
        self.instance_file_path = self.directory / f"{self.instance_set.name}.txt"

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
        self.validation.mkdir()
        self.results_directory.mkdir(parents=True)  # Prepare results directory

        self._prepare_instances()

        if self.feature_data is not None:
            self._create_feature_file()

        self.create_scenario_file()

    def create_scenario_file(
            self: SMAC2Scenario,
            configurator_target: Path = SMAC2.configurator_target,
            pcs_port: PCSConvention = PCSConvention.SMAC) -> Path:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        with self.scenario_file_path.open("w") as file:
            file.write(f"algo = {configurator_target.absolute()} "
                       f"{self.solver.directory} {self.tmp} {self.sparkle_objective} \n"
                       f"deterministic = {1 if self.solver.deterministic else 0}\n"
                       f"run_obj = {self._get_performance_measure()}\n"
                       f"cutoffTime = {self.cutoff_time}\n"
                       f"paramfile = {self.solver.get_pcs_file(pcs_port)}\n"
                       f"outdir = {self.outdir_train}\n"
                       f"instance_file = {self.instance_file_path}\n"
                       f"test_instance_file = {self.instance_file_path}\n")
            if self.cutoff_length is not None:
                file.write(f"cutoff_length = {self.cutoff_length}\n")
            if self.max_iterations is not None:
                file.write(f"iteration-limit = {self.max_iterations}\n")
            if self.wallclock_time is not None:
                file.write(f"wallclock-limit = {self.wallclock_time}\n")
            if self.cpu_time is not None:
                file.write(f"cputime-limit = {self.cpu_time}\n")
            if self.solver_calls is not None:
                file.write(f"runcount-limit = {self.solver_calls}\n")
            if self.cli_cores is not None:
                file.write(f"cli-cores = {self.cli_cores}")
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
                file.write(f"{instance_path}\n")

    def _create_feature_file(self: SMAC2Scenario) -> None:
        """Create CSV file from feature data."""
        self.feature_data.to_csv(self.feature_file_path,
                                 index_label="INSTANCE_NAME")

    def _get_performance_measure(self: SMAC2Scenario) -> str:
        """Retrieve the performance measure of the SparkleObjective.

        Returns:
            Performance measure of the sparkle objective
        """
        if self.sparkle_objective.time:
            return "RUNTIME"
        return "QUALITY"

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
            "feature_data": self.feature_data_path,
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
        cli_cores = config["cli-cores"] if "cli-cores" in config else None

        _, solver_path, _, objective_str = config["algo"].split(" ")
        objective = resolve_objective(objective_str)
        solver = Solver(Path(solver_path.strip()))
        # Extract the instance set from the instance file
        instance_file_path = Path(config["instance_file"])
        instance_set_path = Path(instance_file_path.open().readline().strip()).parent
        instance_set = Instance_Set(Path(instance_set_path))
        results_folder = scenario_file.parent / "results"
        state_run_dirs = [p for p in results_folder.iterdir() if p.is_file()]
        number_of_runs = len(state_run_dirs)
        feature_data_path = None
        if "feature_file" in config:
            feature_data_path = Path(config["feature_file"])
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
                             cli_cores,
                             use_cpu_time_in_tunertime,
                             feature_data_path)
