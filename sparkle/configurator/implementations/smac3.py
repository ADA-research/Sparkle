"""Configurator classes to implement SMAC3 in Sparkle."""
from __future__ import annotations
from pathlib import Path
# import fcntl
# import glob
import shutil

import smac
# import pandas as pd
import numpy as np

# import runrunner as rrr
from runrunner import Runner, Run
import smac.scenario

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
# from sparkle.solver.validator import Validator
from sparkle.structures import FeatureDataFrame
from sparkle.instance import InstanceSet  # , Instance_Set
from sparkle.types import SparkleObjective, resolve_objective


class SMAC3(Configurator):
    """Class for SMAC3 (Python) configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/smac3-v2.20.0"
    configurator_executable = configurator_path / "smac"
    configurator_target = configurator_path / "smac_target_algorithm.py"

    version = smac.version
    full_name = "Sequential Model-based Algorithm Configuration"

    def __init__(self: SMAC3,
                 base_dir: Path,
                 output_path: Path) -> None:
        """Returns the SMAC3 configurator, Python SMAC V2.20.0.

        Args:
            objectives: The objectives to optimize. Only supports one objective.
            base_dir: The path where the configurator will be executed in.
            output_path: The path where the output will be placed.
        """
        raise NotImplementedError

    @property
    def name(self: SMAC3) -> str:
        """Returns the name of the configurator."""
        return SMAC3.__name__

    @property
    def scenario_class(self: Configurator) -> ConfigurationScenario:
        """Returns the SMAC3 scenario class."""
        return SMAC3Scenario

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
        raise NotImplementedError


class SMAC3Scenario(ConfigurationScenario):
    """Class to handle SMAC3 configuration scenarios."""

    def __init__(self: SMAC3Scenario,
                 solver: Solver,
                 instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective],
                 parent_directory: Path,
                 crash_cost: float = np.inf,
                 termination_cost_threshold: float = np.inf,
                 walltime_limit: float = np.inf,
                 cputime_limit: float = np.inf,
                 trial_walltime_limit: float | None = None,
                 trial_memory_limit: int | None = None,
                 n_trials: int = 100,
                 use_default_config: bool = False,
                 instance_features: FeatureDataFrame | dict[str, list[float]] = None,
                 min_budget: float | int | None = None,
                 max_budget: float | int | None = None,
                 seed: int = -1,
                 n_workers: int = 1,
                 ) -> None:
        """Initialize scenario paths and names.

        Args:
            solver : Solver
                The solver to use for configuration.
            instance_set : InstanceSet
                The instance set to use for configuration.
            sparkle_objectives : list[SparkleObjective]
                The objectives to optimize.
            parent_directory : Path
                The parent directory where the configuration files will be stored.
            crash_cost : float | list[float], defaults to np.inf
                Defines the cost for a failed trial. In case of multi-objective,
                each objective can be associated with a different cost.
            termination_cost_threshold : float | list[float], defaults to np.inf
                Defines a cost threshold when the optimization should stop. In case of
                multi-objective, each objective *must* be associated with a cost.
                The optimization stops when all objectives crossed the threshold.
            walltime_limit : float, defaults to np.inf
                The maximum time in seconds that SMAC is allowed to run.
            cputime_limit : float, defaults to np.inf
                The maximum CPU time in seconds that SMAC is allowed to run.
            trial_walltime_limit : float | None, defaults to None
                The maximum time in seconds that a trial is allowed to run.
                If not specified, no constraints are enforced. Otherwise,
                the process will be spawned by pynisher.
            trial_memory_limit : int | None, defaults to None
                The maximum memory in MB that a trial is allowed to use. If not specified
                no constraints are enforced.
            n_trials : int, defaults to 100
                The maximum number of trials (combination of configuration, seed, budget,
                and instance, depending on the task) to run.
            use_default_config: bool, defaults to False.
                If True, the configspace's default configuration is evaluated in the
                initial design. For historic benchmark reasons, this is False by default.
                Notice, that this will result in n_configs + 1 for the initial design.
                Respecting n_trials, this will result in one fewer evaluated
                configuration in the optimization.
            instances : list[str] | None, defaults to None
                Names of the instances to use. If None, no instances are used. Instances
                could be dataset names, seeds, subsets, etc.
            instance_features : dict[str, list[float]] | None, defaults to None
                Instances can be associated with features. For example, meta data of
                the dataset (mean, var, ...) can be incorporated which are then further
                used to expand the training data of the surrogate model.
            min_budget : float | int | None, defaults to None
                The minimum budget (epochs, subset size, number of instances, ...) that
                is used for the optimization. Use this argument if you use multi-fidelity
                or instance optimization.
            max_budget : float | int | None, defaults to None
                The maximum budget (epochs, subset size, number of instances, ...) that
                is used for the optimization. Use this argument if you use multi-fidelity
                or instance optimization.
            seed : int, defaults to 0
                The seed is used to make results reproducible.
                If seed is -1, SMAC will generate a random seed.
            n_workers : int, defaults to 1
                The number of workers to use for parallelization.
                If `n_workers` is greather than 1, SMAC will use DASK to parallelize the
                optimization.
        """
        super().__init__(solver, instance_set, sparkle_objectives, parent_directory)
        # The files are saved in `./output_directory/name/seed`.
        self.results_directory = self.parent_directory / "smac3_output"

        if isinstance(instance_features, FeatureDataFrame):
            instance_features =\
                {instance_name: instance_features.get_instance(instance_name)
                 for instance_name in instance_features.instances}

        configspace = solver.get_config_space()  # TODO: Extract config space from solver
        self.smac3_scenario: smac.scenario = smac.scenario(
            configspace=configspace,
            name=self.name,
            output_dir=self.directory,
            deterministic=solver.deterministic,
            objectives=[o.name for o in sparkle_objectives],
            crash_cost=crash_cost,
            termination_cost_threshold=termination_cost_threshold,
            walltime_limit=walltime_limit,
            cputime_limit=cputime_limit,
            trial_walltime_limit=trial_walltime_limit,
            trial_memory_limit=trial_memory_limit,
            n_trials=n_trials,
            use_default_config=use_default_config,
            instances=instance_set,  # Correct?
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

    def create_scenario_file(self: ConfigurationScenario) -> Path:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        with self.scenario_file_path.open("w") as file:
            for key, value in self.serialize().items():
                file.write(f"{key} = {value}\n")

    def serialize(self: ConfigurationScenario) -> dict:
        """Serialize the configuration scenario."""
        return {
            "solver": self.solver.directory,
            "instance_set": self.instance_set.directory,
            "sparkle_objectives": ",".join(self.smac3_scenario.objectives),
            "parent_directory": self.results_directory,
            "deterministic": self.smac3_scenario.deterministic,
            "crash_cost": self.smac3_scenario.crash_cost,
            "termination_cost_threshold": self.smac3_scenario.termination_cost_threshold,
            "walltime_limit": self.smac3_scenario.walltime_limit,
            "cputime_limit": self.smac3_scenario.cputime_limit,
            "trial_walltime_limit": self.smac3_scenario.trial_walltime_limit,
            "trial_memory_limit": self.smac3_scenario.trial_memory_limit,
            "n_trials": self.smac3_scenario.n_trials,
            "use_default_config": self.smac3_scenario.use_default_config,
            "instance_features": self.smac3_scenario.instance_features,
            "min_budget": self.smac3_scenario.min_budget,
            "max_budget": self.smac3_scenario.max_budget,
            "seed": self.smac3_scenario.seed,
            "n_workers": self.smac3_scenario.n_workers,
        }

    @staticmethod
    def from_file(scenario_file: Path) -> ConfigurationScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        import ast
        variables = {key: value for line in scenario_file.read_text().splitlines()
                     for key, value in line.split(" = ")}
        variables["solver"] = Solver(Path(variables["solver"]))
        variables["instance_set"] = InstanceSet(Path(variables["instance_set"]))
        variables["sparkle_objectives"] = [
            resolve_objective(o)
            for o in variables["sparkle_objectives"].split(",")]
        variables["parent_directory"] = Path(variables["parent_directory"])
        variables["deterministic"] = bool(variables["deterministic"])
        variables["crash_cost"] = float(variables["crash_cost"])
        # We need to support both lists of floats and single float (np.inf is fine)
        if variables["termination_cost_threshold"].startswith("["):  # Hacky test
            tct = ast.literal_eval(variables["termination_cost_threshold"])
            variables["termination_cost_threshold"] = [float(i) for i in tct]
        else:
            variables["termination_cost_threshold"] =\
                float(variables["termination_cost_threshold"])
        variables["walltime_limit"] = float(variables["walltime_limit"])
        variables["cputime_limit"] = float(variables["cputime_limit"])
        variables["trial_walltime_limit"] = float(variables["trial_walltime_limit"])
        variables["trial_memory_limit"] = float(variables["trial_memory_limit"])
        variables["n_trials"] = int(variables["n_trials"])
        variables["use_default_config"] = bool(variables["use_default_config"])
        # variables["instance_features"] =
        variables["min_budget"] = float(variables["min_budget"])  # NOTE: Can also be int
        variables["max_budget"] = float(variables["max_budget"])  # NOTE: Can also be int
        variables["seed"] = int(variables["seed"])
        variables["n_workers"] = int(variables["n_workers"])
        return SMAC3Scenario(**variables)
