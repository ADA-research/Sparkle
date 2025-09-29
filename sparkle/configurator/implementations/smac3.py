"""Configurator classes to implement SMAC3 in Sparkle."""

from __future__ import annotations
from pathlib import Path

from smac import version as smac_version
from smac import Scenario as SmacScenario
from smac import facade as smacfacades
from smac.runhistory.enumerations import StatusType as SmacStatusType
import numpy as np
import random
from typing import Optional

from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.types import SparkleObjective, resolve_objective, SolverStatus


class SMAC3(Configurator):
    """Class for SMAC3 (Python) configurator."""

    configurator_path = Path(__file__).parent.resolve() / "SMAC3"
    configurator_target = configurator_path / "smac3_target_algorithm.py"

    full_name = "Sequential Model-based Algorithm Configuration"
    version = smac_version

    def __init__(self: SMAC3) -> None:
        """Returns the SMAC3 configurator, Python SMAC V2.3.1."""
        return super().__init__(multi_objective_support=False)

    @property
    def name(self: SMAC3) -> str:
        """Returns the name of the configurator."""
        return SMAC3.__name__

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Returns the SMAC3 scenario class."""
        return SMAC3Scenario

    @staticmethod
    def check_requirements(verbose: bool = False) -> bool:
        """Check that SMAC3 is installed."""
        return True  # Is automatically installed with Sparkle

    @staticmethod
    def download_requirements() -> None:
        """Download SMAC3."""
        return  # Nothing to do

    def configure(
        self: SMAC3,
        scenario: SMAC3Scenario,
        data_target: PerformanceDataFrame,
        validate_after: bool = True,
        sbatch_options: list[str] = [],
        slurm_prepend: str | list[str] | Path = None,
        num_parallel_jobs: int = None,
        base_dir: Path = None,
        run_on: Runner = Runner.SLURM,
    ) -> list[Run]:
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
        scenario.create_scenario()
        if (
            scenario.smac3_scenario.walltime_limit
            == scenario.smac3_scenario.cputime_limit
            == np.inf
        ):
            print("WARNING: Starting SMAC3 scenario without any time limit.")
        configuration_ids = scenario.configuration_ids

        # Scenario file also has a seed, but not for all type of configurators
        seeds = [random.randint(0, 2**32 - 1) for _ in range(scenario.number_of_runs)]
        num_parallel_jobs = num_parallel_jobs or scenario.number_of_runs
        # We do not require the configurator CLI as its already our own python wrapper
        cmds = [
            f"python3 {self.configurator_target.absolute()} "
            f"{scenario.scenario_file_path.absolute()} {configuration_id} {seed} "
            f"{data_target.csv_filepath}"
            for configuration_id, seed in zip(configuration_ids, seeds)
        ]
        return super().configure(
            configuration_commands=cmds,
            data_target=data_target,
            output=None,
            scenario=scenario,
            configuration_ids=configuration_ids,
            validate_after=validate_after,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            num_parallel_jobs=num_parallel_jobs,
            base_dir=base_dir,
            run_on=run_on,
        )

    @staticmethod
    def organise_output(
        output_source: Path,
        output_target: Path,
        scenario: SMAC3Scenario,
        configuration_id: str,
    ) -> None | str:
        """Method to restructure and clean up after a single configurator call."""
        import json

        if not output_source.exists():
            print(f"SMAC3 ERROR: Output source file does not exist! [{output_source}]")
            return
        results_dict = json.load(output_source.open("r"))
        configurations = [value for _, value in results_dict["configs"].items()]
        config_evals = [[] for _ in range(len(configurations))]
        objective = scenario.sparkle_objective
        for entry in results_dict["data"]:
            smac_conf_id = entry["config_id"]
            score = entry["cost"]
            # SMAC3 configuration ids start at 1
            config_evals[smac_conf_id - 1].append(score)
        config_evals = [
            objective.instance_aggregator(evaluations) for evaluations in config_evals
        ]
        best_config = configurations[
            config_evals.index(objective.solver_aggregator(config_evals))
        ]
        return Configurator.save_configuration(
            scenario, configuration_id, best_config, output_target
        )

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
            SolverStatus.UNSAT: SmacStatusType.SUCCESS,
        }
        return mapping[status]


class SMAC3Scenario(ConfigurationScenario):
    """Class to handle SMAC3 configuration scenarios."""

    def __init__(
        self: SMAC3Scenario,
        solver: Solver,
        instance_set: InstanceSet,
        sparkle_objectives: list[SparkleObjective],
        number_of_runs: int,
        parent_directory: Path,
        solver_cutoff_time: int = None,
        smac_facade: smacfacades.AbstractFacade
        | str = smacfacades.AlgorithmConfigurationFacade,
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
        timestamp: str = None,
    ) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver
                The solver to use for configuration.
            instance_set: InstanceSet
                The instance set to use for configuration.
            sparkle_objectives: list[SparkleObjective]
                The objectives to optimize.
            number_of_runs: int
                The number of times this scenario will be executed with different seeds.
            parent_directory: Path
                The parent directory where the configuration files will be stored.
            solver_cutoff_time: int
                Maximum CPU runtime in seconds that each solver call (trial)
                is allowed to run. Is managed by RunSolver, not pynisher.
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
                solver time.
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
            timestamp: An optional timestamp for the directory name.
        """
        super().__init__(
            solver,
            instance_set,
            sparkle_objectives,
            number_of_runs,
            parent_directory,
            timestamp,
        )
        self.feature_data = feature_data
        if isinstance(self.feature_data, Path):  # Load from file
            self.feature_data = FeatureDataFrame(self.feature_data)

        # Facade parameters
        self.smac_facade = smac_facade
        if isinstance(self.smac_facade, str):
            self.smac_facade = getattr(smacfacades, self.smac_facade)
        self.max_ratio = max_ratio

        if self.feature_data is not None:
            instance_features = {
                instance: self.feature_data.get_instance(str(instance))
                for instance in self.instance_set.instance_paths
            }
        else:
            # 'If no instance features are passed, the runhistory encoder can not
            # distinguish between different instances and therefore returns the same data
            # points with different values, all of which are used to train the surrogate
            # model. Consider using instance indices as features.'
            instance_features = {
                name: [index] for index, name in enumerate(instance_set.instance_paths)
            }

        # NOTE: Patchfix; SMAC3 can handle MO but Sparkle also gives non-user specified
        # objectives but not all class methods can handle it here yet
        self.sparkle_objective = sparkle_objectives[0]

        # NOTE: We don't use trial_walltime_limit as a way of managing resources
        # As it uses pynisher to do it (python based) and our targets are maybe not
        # RunSolver is the better option for accuracy.
        self.solver_cutoff_time = solver_cutoff_time
        if solver_calls is None:  # If solver calls is None, try to calculate it
            if self.solver_cutoff_time is not None and (cputime_limit or walltime_limit):
                if cputime_limit:
                    solver_calls = int(cputime_limit / self.solver_cutoff_time)
                elif walltime_limit:
                    solver_calls = int(walltime_limit / self.solver_cutoff_time)
            else:
                solver_calls = 100  # SMAC3 Default value
        self.smac3_output_directory = smac3_output_directory
        self.crash_cost = crash_cost
        self.termination_cost_threshold = termination_cost_threshold
        self.walltime_limit = walltime_limit
        self.cputime_limit = cputime_limit
        self.solver_calls = solver_calls
        self.use_default_config = use_default_config
        self.instance_features = instance_features
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.seed = seed
        self.n_workers = n_workers
        self.smac3_scenario: Optional[SmacScenario] = None

    def create_scenario(self: SMAC3Scenario) -> None:
        """This prepares all the necessary subdirectories related to configuration."""
        super().create_scenario()
        self.log_dir.mkdir(parents=True)
        if self.smac3_scenario is None:
            self.set_smac3_scenario()
        self.create_scenario_file()

    def set_smac3_scenario(self: SMAC3Scenario) -> None:
        """Set the smac scenario object."""
        self.smac3_scenario = SmacScenario(
            configspace=self.solver.get_configuration_space(),
            name=self.name,
            output_directory=self.results_directory / self.smac3_output_directory,
            deterministic=self.solver.deterministic,
            objectives=[self.sparkle_objective.name],
            crash_cost=self.crash_cost,
            termination_cost_threshold=self.termination_cost_threshold,
            walltime_limit=self.walltime_limit,
            cputime_limit=self.cputime_limit,
            n_trials=self.solver_calls,
            use_default_config=self.use_default_config,
            instances=self.instance_set.instance_paths,
            instance_features=self.instance_features,
            min_budget=self.min_budget,
            max_budget=self.max_budget,
            seed=self.seed,
            n_workers=self.n_workers,
        )

    @property
    def log_dir(self: SMAC3Scenario) -> Path:
        """Return the path of the log directory."""
        if self.directory:
            return self.directory / "logs"
        return None

    @property
    def configurator(self: SMAC3Scenario) -> SMAC3:
        """Return the type of configurator the scenario belongs to."""
        return SMAC3

    def create_scenario_file(self: SMAC3Scenario) -> Path:
        """Create a file with the configuration scenario."""
        with self.scenario_file_path.open("w") as file:
            for key, value in self.serialise().items():
                file.write(f"{key} = {value}\n")

    def serialise(self: SMAC3Scenario) -> dict:
        """Serialize the configuration scenario."""
        feature_data = str(self.feature_data.csv_filepath) if self.feature_data else None
        return {
            "solver": self.solver.directory,
            "instance_set": self.instance_set.directory,
            "sparkle_objectives": ",".join(self.smac3_scenario.objectives),
            "solver_cutoff_time": self.solver_cutoff_time,
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
    def from_file(scenario_file: Path, run_index: int = None) -> SMAC3Scenario:
        """Reads scenario file and initalises ConfigurationScenario.

        Args:
            scenario_file: Path to scenario file.
            run_index: If given, reads as the scenario with run_index for offset
                in output directory and seed.

        Returns:
            ConfigurationScenario.
        """
        import ast

        variables = {
            keyvalue[0]: keyvalue[1].strip()
            for keyvalue in (
                line.split(" = ", maxsplit=1)
                for line in scenario_file.open().readlines()
                if line.strip() != ""
            )
        }
        variables["solver"] = Solver(Path(variables["solver"]))
        variables["instance_set"] = Instance_Set(Path(variables["instance_set"]))
        variables["sparkle_objectives"] = [
            resolve_objective(o) for o in variables["sparkle_objectives"].split(",")
        ]
        variables["parent_directory"] = scenario_file.parent.parent
        variables["solver_cutoff_time"] = int(variables["solver_cutoff_time"])
        variables["number_of_runs"] = int(variables["number_of_runs"])
        variables["smac_facade"] = getattr(smacfacades, variables["smac_facade"])

        # We need to support both lists of floats and single float (np.inf is fine)
        if variables["crash_cost"].startswith("["):
            variables["crash_cost"] = [
                float(v) for v in ast.literal_eval(variables["crash_cost"])
            ]
        else:
            variables["crash_cost"] = float(variables["crash_cost"])
        if variables["termination_cost_threshold"].startswith("["):
            variables["termination_cost_threshold"] = [
                float(v)
                for v in ast.literal_eval(variables["termination_cost_threshold"])
            ]
        else:
            variables["termination_cost_threshold"] = float(
                variables["termination_cost_threshold"]
            )

        variables["walltime_limit"] = float(variables["walltime_limit"])
        variables["cputime_limit"] = float(variables["cputime_limit"])
        variables["solver_calls"] = ast.literal_eval(variables["solver_calls"])
        variables["use_default_config"] = ast.literal_eval(
            variables["use_default_config"]
        )

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

        timestamp = scenario_file.parent.name.split("_")[-1]
        scenario = SMAC3Scenario(**variables, timestamp=timestamp)
        scenario.set_smac3_scenario()
        return scenario
