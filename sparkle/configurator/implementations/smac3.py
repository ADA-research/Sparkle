"""Configurator classes to implement SMAC3 in Sparkle."""
from __future__ import annotations
from pathlib import Path
import shutil

from smac import version as smac_version
from smac import Scenario as SmacScenario
from smac import facade as smacfacades
from smac.runhistory.enumerations import StatusType as SmacStatusType
import numpy as np

from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.types import SparkleObjective, resolve_objective, SolverStatus


class SMAC3(Configurator):
    """Class for SMAC3 (Python) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/smac3-v2.2.0"
    configurator_executable = configurator_path / "smac3_target_algorithm.py"

    version = smac_version
    full_name = "Sequential Model-based Algorithm Configuration"

    def __init__(self: SMAC3,
                 base_dir: Path,
                 output_path: Path) -> None:
        """Returns the SMAC3 configurator, Python SMAC V2.2.0.

        Args:
            objectives: The objectives to optimize. Only supports one objective.
            base_dir: The path where the configurator will be executed in.
            output_path: The path where the output will be placed.
        """
        output_path = output_path / SMAC3.__name__
        output_path.mkdir(parents=True, exist_ok=True)
        return super().__init__(
            output_path=output_path,
            base_dir=base_dir,
            tmp_path=output_path / "tmp",
            multi_objective_support=False)

    @property
    def name(self: SMAC3) -> str:
        """Returns the name of the configurator."""
        return SMAC3.__name__

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Returns the SMAC3 scenario class."""
        return SMAC3Scenario

    def configure(self: SMAC3,
                  scenario: SMAC3Scenario,
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
            validate_after: Whether the Validator will be called after the configuration
            sbatch_options: List of slurm batch options to use
            slurm_prepend: Slurm script to prepend to the sbatch
            num_parallel_jobs: The maximum number of jobs to run parallel.
            base_dir: The path where the sbatch scripts will be created for Slurm.
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        if (scenario.smac3_scenario.walltime_limit
                == scenario.smac3_scenario.cputime_limit == np.inf):
            print("WARNING: Starting SMAC3 scenario without any time limit.")
        scenario.create_scenario()
        # We set the seed over the last n run ids in the dataframe
        seeds = data_target.run_ids[data_target.num_runs - scenario.number_of_runs:]
        num_parallel_jobs = num_parallel_jobs or scenario.number_of_runs
        # We do not require the configurator CLI as its already our own python wrapper
        cmds = [f"python3 {self.configurator_executable.absolute()} "
                f"{scenario.scenario_file_path.absolute()} {seed} "
                f"{data_target.csv_filepath}"
                for seed in seeds]
        return super().configure(
            configuration_commands=cmds,
            data_target=data_target,
            output=None,
            scenario=scenario,
            validation_ids=seeds if validate_after else None,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            num_parallel_jobs=num_parallel_jobs,
            base_dir=base_dir,
            run_on=run_on
        )

    @staticmethod
    def organise_output(output_source: Path,
                        output_target: Path,
                        scenario: SMAC3Scenario,
                        run_id: int) -> None | str:
        """Method to restructure and clean up after a single configurator call."""
        import json
        from filelock import FileLock
        if not output_source.exists():
            print(f"SMAC3 ERROR: Output source file does not exist! [{output_source}]")
            return
        results_dict = json.load(output_source.open("r"))
        configurations = [value for _, value in results_dict["configs"].items()]
        config_evals = [[] for _ in range(len(configurations))]
        objective = scenario.sparkle_objective
        for entry in results_dict["data"]:
            config_id, _, _, _, score, _, _, _, _, _ = entry
            # SMAC3 configuration ids start at 1
            config_evals[config_id - 1].append(score)
        config_evals = [objective.instance_aggregator(evaluations)
                        for evaluations in config_evals]
        best_config = configurations[
            config_evals.index(objective.solver_aggregator(config_evals))]
        if output_target is None or not output_target.exists():
            return best_config

        time_stamp = scenario.scenario_file_path.stat().st_mtime
        best_config["configuration_id"] =\
            f"{SMAC3.__name__}_{time_stamp}_{run_id}"
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
                value=[str(best_config)],
                solver=solver,
                instance=instances,
                objective=None,
                run=run_id,
                solver_fields=[PerformanceDataFrame.column_configuration]
            )
            performance_data.save_csv()
        lock.release()

    def get_status_from_logs(self: SMAC3) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError

    @staticmethod
    def convert_status(status: SolverStatus) -> SmacStatusType:
        """Converts Sparkle Solver status to SMAC3 target status."""
        mapping = {
            SolverStatus.SUCCESS: SmacStatusType.SUCCESS,
            SolverStatus.CRASHED: SmacStatusType.CRASHED,
            SolverStatus.TIMEOUT: SmacStatusType.TIMEOUT,
            SolverStatus.WRONG: SmacStatusType.CRASHED,
            SolverStatus.UNKNOWN: SmacStatusType.CRASHED,
            SolverStatus.ERROR: SmacStatusType.CRASHED,
            SolverStatus.KILLED: SmacStatusType.TIMEOUT,
            SolverStatus.SAT: SmacStatusType.SUCCESS,
            SolverStatus.UNSAT: SmacStatusType.SUCCESS
        }
        return mapping[status]


class SMAC3Scenario(ConfigurationScenario):
    """Class to handle SMAC3 configuration scenarios."""

    def __init__(self: SMAC3Scenario,
                 solver: Solver,
                 instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective],
                 parent_directory: Path,
                 cutoff_time: int = None,
                 number_of_runs: int = None,
                 smac_facade: smacfacades.AbstractFacade | str =
                 smacfacades.AlgorithmConfigurationFacade,
                 crash_cost: float | list[float] = np.inf,
                 termination_cost_threshold: float | list[float] = np.inf,
                 walltime_limit: float = np.inf,
                 cputime_limit: float = np.inf,
                 solver_calls: int = None,
                 use_default_config: bool = False,
                 feature_data: FeatureDataFrame | Path = None,
                 min_budget: float | int | None = None,
                 max_budget: float | int | None = None,
                 seed: int = -1,
                 n_workers: int = 1,
                 max_ratio: float = None,
                 smac3_output_directory: Path = Path(),
                 ) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver
                The solver to use for configuration.
            instance_set: InstanceSet
                The instance set to use for configuration.
            sparkle_objectives: list[SparkleObjective]
                The objectives to optimize.
            parent_directory: Path
                The parent directory where the configuration files will be stored.
            cutoff_time: int
                Maximum CPU runtime in seconds that each solver call (trial)
                is allowed to run. Is managed by RunSolver, not pynisher.
            number_of_runs: int
                The number of times this scenario will be executed with different seeds.
            smac_facade: AbstractFacade, defaults to AlgorithmConfigurationFacade
                The SMAC facade to use for Optimisation.
            crash_cost: float | list[float], defaults to np.inf
                Defines the cost for a failed trial. In case of multi-objective,
                each objective can be associated with a different cost.
            termination_cost_threshold: float | list[float], defaults to np.inf
                Defines a cost threshold when the optimization should stop. In case of
                multi-objective, each objective *must* be associated with a cost.
                The optimization stops when all objectives crossed the threshold.
            walltime_limit: float, defaults to np.inf
                The maximum time in seconds that SMAC is allowed to run. Only counts
                solver time.
            cputime_limit: float, defaults to np.inf
                The maximum CPU time in seconds that SMAC is allowed to run. Only counts
                solver time. WARNING: SMAC3 uses "runtime" (walltime) for CPU time
                when determining cputime budget.
            solver_calls: int, defaults to None
                The maximum number of trials (combination of configuration, seed, budget,
                and instance, depending on the task) to run. If left as None, will be
                calculated as int(cutoff time / cputime or walltime limit)
            use_default_config: bool, defaults to False
                If True, the configspace's default configuration is evaluated in the
                initial design. For historic benchmark reasons, this is False by default.
                Notice, that this will result in n_configs + 1 for the initial design.
                Respecting n_trials, this will result in one fewer evaluated
                configuration in the optimization.
            instances: list[str] | None, defaults to None
                Names of the instances to use. If None, no instances are used. Instances
                could be dataset names, seeds, subsets, etc.
            feature_data: FeatureDataFrame or Path, defaults to None
                Instances can be associated with features. For example, meta data of
                the dataset (mean, var, ...) can be incorporated which are then further
                used to expand the training data of the surrogate model. If Path, loaded
                from file. When no features are given, uses index as instance features.
            min_budget: float | int | None, defaults to None
                The minimum budget (epochs, subset size, number of instances, ...) that
                is used for the optimization. Use this argument if you use multi-fidelity
                or instance optimization.
            max_budget: float | int | None, defaults to None
                The maximum budget (epochs, subset size, number of instances, ...) that
                is used for the optimization. Use this argument if you use multi-fidelity
                or instance optimization.
            seed: int, defaults to -1
                The seed is used to make results reproducible.
                If seed is -1, SMAC will generate a random seed.
            n_workers: int, defaults to 1
                The number of workers to use for parallelization.
                If `n_workers` is greather than 1, SMAC will use DASK to parallelize the
                optimization.
            max_ratio: float, defaults to None.
                Facade uses at most scenario.n_trials * max_ratio number of
                configurations in the initial design. Additional configurations are not
                affected by this parameter. Not applicable to each facade.
            smac3_output_directory: Path, defaults to Path()
                The output subdirectory for the SMAC3 scenario. Defaults to the scenario
                results directory.
        """
        super().__init__(solver, instance_set, sparkle_objectives, parent_directory)
        # The files are saved in `./output_directory/name/seed`.
        self.log_dir = self.directory / "logs"
        self.number_of_runs = number_of_runs
        self.feature_data = feature_data
        if isinstance(self.feature_data, Path):  # Load from file
            self.feature_data = FeatureDataFrame(self.feature_data)

        # Facade parameters
        self.smac_facade = smac_facade
        if isinstance(self.smac_facade, str):
            self.smac_facade = getattr(smacfacades, self.smac_facade)
        self.max_ratio = max_ratio

        if self.feature_data is not None:
            instance_features =\
                {instance: self.feature_data.get_instance(str(instance))
                    for instance in self.instance_set.instance_paths}
        else:
            # 'If no instance features are passed, the runhistory encoder can not
            # distinguish between different instances and therefore returns the same data
            # points with different values, all of which are used to train the surrogate
            # model. Consider using instance indices as features.'
            instance_features = {name: [index] for index, name
                                 in enumerate(instance_set.instance_paths)}

        # NOTE: Patchfix; SMAC3 can handle MO but Sparkle also gives non-user specified
        # objectives but not all class methods can handle it here yet
        self.sparkle_objective = sparkle_objectives[0]

        # NOTE: We don't use trial_walltime_limit as a way of managing resources
        # As it uses pynisher to do it (python based) and our targets are maybe not
        # RunSolver is the better option for accuracy.
        self.cutoff_time = cutoff_time
        if solver_calls is None:  # If solver calls is None, try to calculate it
            if self.cutoff_time is not None and (cputime_limit or walltime_limit):
                if cputime_limit:
                    solver_calls = int(cputime_limit / self.cutoff_time)
                elif walltime_limit:
                    solver_calls = int(walltime_limit / self.cutoff_time)
            else:
                solver_calls = 100  # SMAC3 Default value
        self.smac3_scenario = SmacScenario(
            configspace=solver.get_cs(),
            name=self.name,
            output_directory=self.results_directory / smac3_output_directory,
            deterministic=solver.deterministic,
            objectives=[self.sparkle_objective.name],
            crash_cost=crash_cost,
            termination_cost_threshold=termination_cost_threshold,
            walltime_limit=walltime_limit,
            cputime_limit=cputime_limit,
            n_trials=solver_calls,
            use_default_config=use_default_config,
            instances=instance_set.instance_paths,
            instance_features=instance_features,
            min_budget=min_budget,
            max_budget=max_budget,
            seed=seed,
            n_workers=n_workers
        )

    def create_scenario(self: ConfigurationScenario) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)
        # Create empty directories as needed
        self.results_directory.mkdir(parents=True)  # Prepare results directory
        self.log_dir.mkdir(parents=True)
        self.validation.mkdir(parents=True, exist_ok=True)
        self.create_scenario_file()

    def create_scenario_file(self: ConfigurationScenario) -> Path:
        """Create a file with the configuration scenario."""
        with self.scenario_file_path.open("w") as file:
            for key, value in self.serialize().items():
                file.write(f"{key} = {value}\n")

    def serialize(self: ConfigurationScenario) -> dict:
        """Serialize the configuration scenario."""
        feature_data =\
            self.feature_data.csv_filepath if self.feature_data else None
        return {
            "solver": self.solver.directory,
            "instance_set": self.instance_set.directory,
            "sparkle_objectives": ",".join(self.smac3_scenario.objectives),
            "cutoff_time": self.cutoff_time,
            "number_of_runs": self.number_of_runs,
            "smac_facade": self.smac_facade.__name__,
            "crash_cost": self.smac3_scenario.crash_cost,
            "termination_cost_threshold": self.smac3_scenario.termination_cost_threshold,
            "walltime_limit": self.smac3_scenario.walltime_limit,
            "cputime_limit": self.smac3_scenario.cputime_limit,
            "solver_calls": self.smac3_scenario.n_trials,
            "use_default_config": self.smac3_scenario.use_default_config,
            "feature_data": feature_data,
            "min_budget": self.smac3_scenario.min_budget,
            "max_budget": self.smac3_scenario.max_budget,
            "seed": self.smac3_scenario.seed,
            "n_workers": self.smac3_scenario.n_workers,
        }

    @staticmethod
    def from_file(scenario_file: Path,
                  run_index: int = None) -> ConfigurationScenario:
        """Reads scenario file and initalises ConfigurationScenario.

        Args:
            scenario_file: Path to scenario file.
            run_index: If given, reads as the scenario with run_index for offset
                in output directory and seed.

        Returns:
            ConfigurationScenario.
        """
        import ast
        variables = {keyvalue[0]: keyvalue[1].strip()
                     for keyvalue in (line.split(" = ", maxsplit=1)
                                      for line in scenario_file.open().readlines()
                                      if line.strip() != "")}
        variables["solver"] = Solver(Path(variables["solver"]))
        variables["instance_set"] = Instance_Set(Path(variables["instance_set"]))
        variables["sparkle_objectives"] = [
            resolve_objective(o)
            for o in variables["sparkle_objectives"].split(",")]
        variables["parent_directory"] = scenario_file.parent.parent
        variables["cutoff_time"] = int(variables["cutoff_time"])
        variables["number_of_runs"] = int(variables["number_of_runs"])
        variables["smac_facade"] = getattr(smacfacades, variables["smac_facade"])

        # We need to support both lists of floats and single float (np.inf is fine)
        if variables["crash_cost"].startswith("["):
            variables["crash_cost"] =\
                [float(v) for v in ast.literal_eval(variables["crash_cost"])]
        else:
            variables["crash_cost"] = float(variables["crash_cost"])
        if variables["termination_cost_threshold"].startswith("["):
            variables["termination_cost_threshold"] =\
                [float(v) for v in ast.literal_eval(
                    variables["termination_cost_threshold"])]
        else:
            variables["termination_cost_threshold"] =\
                float(variables["termination_cost_threshold"])

        variables["walltime_limit"] = float(variables["walltime_limit"])
        variables["cputime_limit"] = float(variables["cputime_limit"])
        variables["solver_calls"] = ast.literal_eval(variables["solver_calls"])
        variables["use_default_config"] =\
            ast.literal_eval(variables["use_default_config"])

        if variables["feature_data"] != "None":
            variables["feature_data"] = Path(variables["feature_data"])
        else:
            variables["feature_data"] = None

        variables["min_budget"] = ast.literal_eval(variables["min_budget"])
        variables["max_budget"] = ast.literal_eval(variables["max_budget"])

        variables["seed"] = ast.literal_eval(variables["seed"])
        variables["n_workers"] = ast.literal_eval(variables["n_workers"])
        if run_index is not None:  # Offset
            variables["seed"] += run_index
            variables["smac3_output_directory"] = Path(f"run_{run_index}")

        return SMAC3Scenario(**variables)
