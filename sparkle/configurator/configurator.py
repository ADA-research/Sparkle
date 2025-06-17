#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different algorithm configurators like SMAC."""
from __future__ import annotations
from pathlib import Path

import runrunner as rrr
from runrunner import Runner, Run

from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.structures import PerformanceDataFrame
from sparkle.types import SparkleObjective


class Configurator:
    """Abstact class to use different configurators like SMAC."""
    configurator_cli_path = Path(__file__).parent.resolve() / "configurator_cli.py"

    def __init__(self: Configurator, output_path: Path,
                 base_dir: Path, tmp_path: Path,
                 multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            output_path: Output directory of the Configurator.
            objectives: The list of Sparkle Objectives the configurator has to
                optimize.
            base_dir: Where to execute the configuration
            tmp_path: Path for the temporary files of the configurator, optional
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.output_path = output_path
        self.base_dir = base_dir
        self.tmp_path = tmp_path
        self.multiobjective = multi_objective_support
        self.scenario = None

    @property
    def name(self: Configurator) -> str:
        """Return the name of the configurator."""
        return self.__class__.__name__

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Return the scenario class of the configurator."""
        return ConfigurationScenario

    def configure(self: Configurator,
                  configuration_commands: list[str],
                  data_target: PerformanceDataFrame,
                  output: Path,
                  scenario: ConfigurationScenario,
                  configuration_ids: list[str] = None,
                  validate_after: bool = True,
                  sbatch_options: list[str] = None,
                  slurm_prepend: str | list[str] | Path = None,
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> Run:
        """Start configuration job.

        This method is shared by the configurators and should be called by the
        implementation/subclass of the configurator.

        Args:
            configuration_commands: List of configurator commands to execute
            data_target: Performance data to store the results.
            output: Output directory.
            scenario: ConfigurationScenario to execute.
            configuration_ids: List of configuration ids that are to be created
            validate_after: Whether the configurations should be validated
            sbatch_options: List of slurm batch options to use
            slurm_prepend: Slurm script to prepend to the sbatch
            num_parallel_jobs: The maximum number of jobs to run in parallel
            base_dir: The base_dir of RunRunner where the sbatch scripts will be placed
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        # Add the configuration IDs to the dataframe with empty configurations
        data_target.add_configuration(str(scenario.solver.directory),
                                      configuration_ids,
                                      [{}] * len(configuration_ids))
        data_target.save_csv()
        # Submit the configuration job
        runs = [rrr.add_to_queue(
            runner=run_on,
            cmd=configuration_commands,
            name=f"{self.name}: {scenario.solver.name} on {scenario.instance_set.name}",
            base_dir=base_dir,
            output_path=output,
            parallel_jobs=num_parallel_jobs,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend)]

        if validate_after:
            validate = scenario.solver.run_performance_dataframe(
                scenario.instance_set,
                config_ids=configuration_ids,
                performance_dataframe=data_target,
                cutoff_time=scenario.cutoff_time,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                log_dir=scenario.validation,
                base_dir=base_dir,
                dependencies=runs,
                job_name=f"{self.name}: Validating {len(configuration_ids)} "
                         f"{scenario.solver.name} Configurations on "
                         f"{scenario.instance_set.name}",
                run_on=run_on,
            )
            runs.append(validate)

        if run_on == Runner.LOCAL:
            print(f"[{self.name}] Running {len(runs)} jobs locally...")
            for run in runs:
                run.wait()
            print(f"[{self.name}] Finished running {len(runs)} jobs locally.")
        return runs

    @staticmethod
    def organise_output(output_source: Path,
                        output_target: Path,
                        scenario: ConfigurationScenario,
                        configuration_id: str) -> None | str:
        """Method to restructure and clean up after a single configurator call.

        Args:
            output_source: Path to the output file of the configurator run.
            output_target: Path to the Performance DataFrame to store result.
            scenario: ConfigurationScenario of the configuration.
            configuration_id: ID (of the run) of the configuration.
        """
        raise NotImplementedError

    @staticmethod
    def save_configuration(scenario: ConfigurationScenario,
                           configuration_id: str,
                           configuration: dict,
                           output_target: Path) -> dict | None:
        """Method to save a configuration to a file.

        If the output_target is None, return the configuration.

        Args:
            scenario: ConfigurationScenario of the configuration. Should be removed.
            configuration_id: ID (of the run) of the configuration.
            configuration: Configuration to save.
            output_target: Path to the Performance DataFrame to store result.
        """
        if output_target is None or not output_target.exists():
            return configuration
        # Save result to Performance DataFrame
        from filelock import FileLock
        lock = FileLock(f"{output_target}.lock")
        with lock.acquire(timeout=60):
            performance_data = PerformanceDataFrame(output_target)
            # Resolve absolute path to Solver column
            solver = [s for s in performance_data.solvers
                      if Path(s).name == scenario.solver.name][0]
            # Update the configuration ID by adding the configuration
            performance_data.add_configuration(
                solver=solver,
                configuration_id=configuration_id,
                configuration=configuration)
            performance_data.save_csv()

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError


class ConfigurationScenario:
    """Template class to handle a configuration scenarios."""
    def __init__(self: ConfigurationScenario,
                 solver: Solver,
                 instance_set: InstanceSet,
                 sparkle_objectives: list[SparkleObjective],
                 number_of_runs: int,
                 parent_directory: Path) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            sparkle_objectives: Sparkle Objectives to optimize.
            number_of_runs: The number of configurator runs to perform.
            parent_directory: Directory in which the scenario should be placed.
        """
        self.solver = solver
        self.instance_set = instance_set
        self.sparkle_objectives = sparkle_objectives
        self.name = f"{self.solver.name}_{self.instance_set.name}"
        self.number_of_runs = number_of_runs

        self.directory = parent_directory / self.name
        self.scenario_file_path = self.directory / f"{self.name}_scenario.txt"
        self.validation: Path = self.directory / "validation"
        self.tmp: Path = self.directory / "tmp"
        self.results_directory: Path = self.directory / "results"

    @property
    def configurator(self: ConfigurationScenario) -> Configurator:
        """Return the type of configurator the scenario belongs to."""
        return Configurator

    @property
    def configuration_ids(self: ConfigurationScenario) -> list[str]:
        """Return the IDs of the configurations for the scenario.

        Only exists after the scenario has been created.

        Returns:
            List of configuration IDs, one for each run.
        """
        if not self.scenario_file_path.exists():
            return []
        from datetime import datetime
        time_stamp = datetime.fromtimestamp(self.scenario_file_path.stat().st_mtime)
        return [f"{self.name}_{time_stamp.strftime('%Y%m%d%H%M%S')}_{i}"
                for i in range(self.number_of_runs)]

    def create_scenario(self: ConfigurationScenario, parent_directory: Path) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        raise NotImplementedError

    def create_scenario_file(self: ConfigurationScenario) -> Path:
        """Create a file with the configuration scenario.

        Writes supplementary information to the target algorithm (algo =) as:
        algo = {configurator_target} {solver_directory} {sparkle_objective}
        """
        raise NotImplementedError

    def serialise(self: ConfigurationScenario) -> dict:
        """Serialize the configuration scenario."""
        raise NotImplementedError

    @classmethod
    def find_scenario(cls: ConfigurationScenario,
                      directory: Path,
                      solver: Solver,
                      instance_set: InstanceSet) -> ConfigurationScenario:
        """Resolve a scenario from a directory and Solver / Training set."""
        scenario_name = f"{solver.name}_{instance_set.name}"
        path = directory / f"{scenario_name}" / f"{scenario_name}_scenario.txt"
        if not path.exists():
            return None
        return cls.from_file(path)

    @staticmethod
    def from_file(scenario_file: Path) -> ConfigurationScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        raise NotImplementedError
