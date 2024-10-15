"""Configurator classes to implement IRACE in Sparkle."""
from __future__ import annotations
from pathlib import Path

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver, Validator
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective

from runrunner import Runner, Run


class IRACE(Configurator):
    """Class for IRACE configurator."""

    def __init__(self: Configurator, validator: Validator, output_path: Path,
                 executable_path: Path, configurator_target: Path,
                 objectives: list[SparkleObjective], base_dir: Path, tmp_path: Path,
                 ) -> None:
        """Initialize IRACE configurator."""
        super().__init__(validator, output_path, executable_path, configurator_target,
                         objectives, base_dir, tmp_path, multi_objective_support=False)

    @property
    def scenario(self: Configurator) -> ConfigurationScenario:
        """Returns the IRACE scenario class."""
        return IRACEScenario

    def configure(self: Configurator,
                  scenario: ConfigurationScenario,
                  validate_after: bool = True,
                  sbatch_options: list[str] = [],
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> Run:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario to execute.
            validate_after: Whether to validate the configuration on the training set
                afterwards or not.
            sbatch_options: List of slurm batch options to use
            num_parallel_jobs: The maximum number of jobs to run in parallel
            base_dir: The base_dir of RunRunner where the sbatch scripts will be placed
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        raise NotImplementedError

    def get_optimal_configuration(self: Configurator,
                                  solver: Solver,
                                  instance_set: InstanceSet,
                                  objective: SparkleObjective) -> tuple[float, str]:
        """Returns the optimal configuration string for a solver of an instance set."""
        raise NotImplementedError

    @staticmethod
    def organise_output(output_source: Path, output_target: Path) -> None | str:
        """Method to restructure and clean up after a single configurator call."""
        raise NotImplementedError

    def set_scenario_dirs(self: Configurator,
                          solver: Solver, instance_set: InstanceSet) -> None:
        """Patching method to allow the rebuilding of configuration scenario."""
        raise NotImplementedError

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError


class IRACEScenario(ConfigurationScenario):
    """Class for IRACE scenario."""

    def __init__(self: IRACEScenario, solver: Solver, instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective] = None)\
            -> None:
        """Initialize scenario."""
        super().__init__(solver, instance_set, sparkle_objectives)

    def create_scenario(self: IRACEScenario, parent_directory: Path) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        raise NotImplementedError

    def create_scenario_file(self: ConfigurationScenario) -> None:
        """Create a file from the IRACE scenario."""
        raise NotImplementedError

    @staticmethod
    def from_file(scenario_file: Path, solver: Solver, instance_set: InstanceSet,
                  ) -> ConfigurationScenario:
        """Reads scenario file and initalises IRACEScenario."""
        raise NotImplementedError
