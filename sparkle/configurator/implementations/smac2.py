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

import runrunner as rrr
from runrunner import Runner, Run

from sparkle.configurator.configurator import Configurator
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.platform import CommandName
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
            name=CommandName.CONFIGURE_SOLVER,
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
        self.scenario = ConfigurationScenario(solver, instance_set)
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
