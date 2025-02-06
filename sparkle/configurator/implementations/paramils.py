"""Configurator class to use different configurators like SMAC."""
from __future__ import annotations
from pathlib import Path
import shutil

from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator
from sparkle.configurator.implementations.smac2 import SMAC2Scenario
from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective


class ParamILS(Configurator):
    """Class for ParamILS (Java) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/paramils-v3.0.0"
    configurator_executable = configurator_path / "paramils"
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
        if shutil.which("java") is None:
            raise RuntimeError(
                "ParamILS requires Java 1.8.0_402, but Java is not installed. "
                "Please ensure Java is installed and try again."
            )
        scenario.create_scenario()
        # We set the seed over the last n run ids in the dataframe
        seeds = data_target.run_ids[data_target.num_runs - scenario.number_of_runs:]
        output = [f"{(scenario.results_directory).absolute()}/"
                  f"{scenario.name}_seed_{seed}_smac.txt"
                  for seed in seeds]
        # NOTE: Could add --rungroup $dirname to change the created directory name
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{ParamILS.__name__} {output_file} {data_target.csv_filepath} "
                f"{scenario.scenario_file_path} {seed} "
                f"{ParamILS.configurator_executable.absolute()} "
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
            base_dir=base_dir,
            run_on=run_on,
        )

    @staticmethod
    def organise_output(output_source: Path,
                        output_target: Path = None,
                        scenario: ParamILSScenario = None,
                        run_id: int = None) -> None | str:
        """Retrieves configurations from SMAC files and places them in output."""
        pass

    def get_status_from_logs(self: ParamILS) -> None:
        """Method to scan the log files of the configurator for warnings."""
        return


class ParamILSScenario(SMAC2Scenario):
    """Class to handle ParamILS configuration scenarios."""

    def __init__(self: ParamILSScenario,
                 solver: Solver,
                 instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective],
                 parent_directory: Path,
                 number_of_runs: int = None,
                 solver_calls: int = None,
                 max_iterations: int = None,
                 cutoff_time: int = None,
                 cli_cores: int = None,
                 use_cpu_time_in_tunertime: bool = None,
                 feature_data: FeatureDataFrame | Path = None,
                 tuner_timeout: int = None,
                 focused_ils: bool = True,
                 initial_configurations: int = 10,
                 min_runs: int = 1,
                 max_runs: int = 2000,
                 random_restart: float = 0.05,
                 )\
            -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            sparkle_objectives: SparkleObjectives used for each run of the configuration.
            parent_directory: Directory in which the scenario should be created.
            number_of_runs: The number of configurator runs to perform
                for configuring the solver.
            solver_calls: The number of times the solver is called for each
                configuration run
            max_iterations: The maximum number of iterations allowed for each
                configuration run. [iteration-limit, numIterations, numberOfIterations]
            cutoff_time: The maximum number of seconds allowed for each
                configuration run. [time-limit, cpu-time, wallclock-time]
            cli_cores: The maximum number of cores allowed for each
                configuration run.
            use_cpu_time_in_tunertime: Whether to use cpu_time in the tuner
                time limit.
            feature_data: The feature data for the instances in the scenario.
            tuner_timeout: The maximum number of seconds allowed for the tuner.
            focused_ils: Comparison approach of ParamILS.
                True for focused ILS, false for basic.
            initial_configurations: The number of initial configurations.
            min_runs: The minimum number of runs required for a single configuration.
            max_runs: The maximum number of runs allowed for a single configuration.
            random_restart: The probability to restart from a random configuration.
        """
        super().__init__(solver, instance_set, sparkle_objectives, parent_directory,
                         number_of_runs, solver_calls, max_iterations, None,
                         None, cutoff_time, None, cli_cores,
                         use_cpu_time_in_tunertime, feature_data)
        self.solver = solver
        self.instance_set = instance_set
        self.tuner_timeout = tuner_timeout
        self.multi_objective = len(sparkle_objectives) > 1  # Not using MO yet in Sparkle
        self.approach = "BASIC" if not focused_ils else "FOCUSED"
        self.initial_configurations = initial_configurations
        self.min_runs = min_runs
        self.max_runs = max_runs
        self.random_restart = random_restart

    def create_scenario_file(self: ParamILSScenario) -> Path:
        """Create a file with the configuration scenario."""
        scenario_file = super().create_scenario_file(ParamILS.configurator_target,
                                                     "paramils")
        with scenario_file.open("+a") as fout:
            fout.write(f"approach = {self.approach}\n")
            fout.write(f"R = {self.initial_configurations}\n")
            fout.write(f"min-runs = {self.min_runs}\n")
            fout.write(f"max-runs = {self.max_runs}\n")
            fout.write(f"random-restart = {self.random_restart}\n")
            # Add check-instances-exist = True?
            fout.write("check-instances-exist = True\n")
        return scenario_file

    @staticmethod
    def from_file(scenario_file: Path) -> ParamILSScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        from sparkle.types import resolve_objective
        from sparkle.instance import Instance_Set
        config = {}
        with scenario_file.open() as file:
            import ast
            for line in file:
                key, value = line.strip().split(" = ")
                key = key.replace("-", "_")
                try:
                    config[key] = ast.literal_eval(value)
                except Exception:
                    config[key] = value

        _, solver_path, _, objective_str = config["algo"].split(" ")
        objective = resolve_objective(objective_str)
        solver = Solver(Path(solver_path.strip()))
        # Extract the instance set from the instance file
        instance_file_path = Path(config["instance_file"])
        instance_set_path = Path(instance_file_path.open().readline().strip()).parent
        instance_set = Instance_Set(Path(instance_set_path))

        del config["algo"]
        del config["run_obj"]
        del config["deterministic"]
        del config["paramfile"]
        del config["instance_file"]
        del config["test_instance_file"]
        del config["outdir"]
        del config["validation"]
        del config["check_instances_exist"]

        # TODO: Convert parameter names
        if "cutoffTime" in config:
            config["cutoff_time"] = config.pop("cutoffTime")
        if "runcount-limit" in config:
            config["solver_calls"] = config.pop("runcount-limit")
        if "approach" in config:
            config["focused_ils"] = config.pop("approach") == "FOCUS"
        if "R" in config:
            config["initial_configurations"] = config.pop("R")
        if "runcount_limit" in config:
            config["solver_calls"] = config.pop("runcount_limit")

        return ParamILSScenario(solver,
                                instance_set,
                                [objective],
                                scenario_file.parent,
                                **config
                                )
