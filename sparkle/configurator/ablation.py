#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for ablation analysis."""
from __future__ import annotations
import re
import shutil
import decimal
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Run

from sparkle.configurator import ConfigurationScenario
from sparkle.instance import InstanceSet


class AblationScenario:
    """Class for ablation analysis."""

    # We use the SMAC2 target algorithm for solver output handling
    configurator_target = Path(__file__).parent.parent.resolve() /\
        "Components" / "smac2-v2.10.03-master-778" / "smac2_target_algorithm.py"

    ablation_dir = Path(__file__).parent.parent / "Components" /\
        "ablationAnalysis-0.9.4"
    ablation_executable = ablation_dir / "ablationAnalysis"
    ablation_validation_executable = ablation_dir / "ablationValidation"

    def __init__(self: AblationScenario,
                 configuration_scenario: ConfigurationScenario,
                 test_set: InstanceSet,
                 output_dir: Path,
                 override_dirs: bool = False) -> None:
        """Initialize ablation scenario.

        Args:
            solver: Solver object
            configuration_scenario: Configuration scenario
            train_set: The training instance
            test_set: The test instance
            output_dir: The output directory
            override_dirs: Whether to clean the scenario directory if it already exists
        """
        self.config_scenario = configuration_scenario
        self.solver = configuration_scenario.solver
        self.train_set = configuration_scenario.instance_set
        self.concurrent_clis = None
        self.test_set = test_set
        self.output_dir = output_dir
        self.scenario_name = configuration_scenario.name
        if self.test_set is not None:
            self.scenario_name += f"_{self.test_set.name}"
        self.scenario_dir = self.output_dir / self.scenario_name
        if override_dirs and self.scenario_dir.exists():
            print("Warning: found existing ablation scenario. This will be removed.")
            shutil.rmtree(self.scenario_dir)

        # Create required scenario directories
        self.tmp_dir = self.scenario_dir / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        self.validation_dir = self.scenario_dir / "validation"
        self.validation_dir_tmp = self.validation_dir / "tmp"
        self.validation_dir_tmp.mkdir(parents=True, exist_ok=True)
        self.table_file = self.validation_dir / "log" / "ablation-validation-run1234.txt"

    def create_configuration_file(self: AblationScenario,
                                  cutoff_time: int,
                                  cutoff_length: str,
                                  concurrent_clis: int,
                                  best_configuration: dict,
                                  ablation_racing: bool = False) -> Path:
        """Create a configuration file for ablation analysis.

        Args:
            cutoff_time: The cutoff time for ablation analysis
            cutoff_length: The cutoff length for ablation analysis
            concurrent_clis: The maximum number of concurrent jobs on a single node

        Returns:
            None
        """
        self.concurrent_clis = concurrent_clis
        ablation_scenario_dir = self.scenario_dir
        objective = self.config_scenario.sparkle_objective
        pcs = self.solver.get_cs()
        parameter_names = [p.name for p in pcs.values()]
        # We need to remove any redundant keys that are not in PCS
        removable_keys = [key for key in best_configuration
                          if key not in parameter_names]
        for key in removable_keys:
            del best_configuration[key]
        opt_config_str = " ".join([f"-{k} {v}" for k, v in best_configuration.items()])
        # We need to check which params are missing and supplement with default values
        for p in list(pcs.values()):
            if p.name not in opt_config_str:
                opt_config_str += f" -{p.name} {p.default_value}"

        # Ablation cannot deal with E scientific notation in floats
        ctx = decimal.Context(prec=16)
        for config in opt_config_str.split(" -"):
            _, value = config.strip().split(" ")
            if "e" in value.lower():
                value = value.strip("'")
                float_value = float(value.lower())
                formatted = format(ctx.create_decimal(float_value), "f")
                opt_config_str = opt_config_str.replace(value, formatted)

        smac_run_obj = "RUNTIME" if objective.time else "QUALITY"
        objective_str = "MEAN10" if objective.time else "MEAN"
        pcs_file_path = f"{self.config_scenario.solver.pcs_file.absolute()}"

        # Create config file
        config_file = Path(f"{ablation_scenario_dir}/ablation_config.txt")
        config = (f'algo = "{AblationScenario.configurator_target.absolute()} '
                  f"{self.config_scenario.solver.directory.absolute()} "
                  f'{self.tmp_dir.absolute()} {objective}"\n'
                  f"execdir = {self.tmp_dir.absolute()}\n"
                  "experimentDir = ./\n"
                  f"deterministic = {1 if self.solver.deterministic else 0}\n"
                  f"run_obj = {smac_run_obj}\n"
                  f"overall_obj = {objective_str}\n"
                  f"cutoffTime = {cutoff_time}\n"
                  f"cutoff_length = {cutoff_length}\n"
                  f"cli-cores = {self.concurrent_clis}\n"
                  f"useRacing = {ablation_racing}\n"
                  "seed = 1234\n"
                  f"paramfile = {pcs_file_path}\n"
                  "instance_file = instances_train.txt\n"
                  "test_instance_file = instances_test.txt\n"
                  "sourceConfiguration=DEFAULT\n"
                  f'targetConfiguration="{opt_config_str}"')
        config_file.open("w").write(config)
        # Write config to validation directory
        conf_valid = config.replace(f"execdir = {self.tmp_dir.absolute()}\n",
                                    f"execdir = {self.validation_dir_tmp.absolute()}\n")
        (self.validation_dir / config_file.name).open("w").write(conf_valid)
        return self.validation_dir / config_file.name

    def create_instance_file(self: AblationScenario, test: bool = False) -> Path:
        """Create an instance file for ablation analysis."""
        file_suffix = "_train.txt"
        instance_set = self.train_set
        if test:
            file_suffix = "_test.txt"
            instance_set = self.test_set if self.test_set is not None else self.train_set
        # We give the Ablation script the paths of the instances
        file_instance = self.scenario_dir / f"instances{file_suffix}"
        with file_instance.open("w") as fh:
            for instance in instance_set._instance_paths:
                # We need to unpack the multi instance file paths in quotes
                if isinstance(instance, list):
                    joined_instances = " ".join(
                        [str(file.absolute()) for file in instance])
                    fh.write(f"{joined_instances}\n")
                else:
                    fh.write(f"{instance.absolute()}\n")
        # Copy to validation directory
        shutil.copyfile(file_instance, self.validation_dir / file_instance.name)
        return file_instance

    def check_for_ablation(self: AblationScenario) -> bool:
        """Checks if ablation has terminated successfully."""
        if not self.table_file.is_file():
            return False
        # First line in the table file should be "Ablation analysis validation complete."
        table_line = self.table_file.open().readline().strip()
        return table_line == "Ablation analysis validation complete."

    def read_ablation_table(self: AblationScenario) -> list[list[str]]:
        """Read from ablation table of a scenario."""
        if not self.check_for_ablation():
            # No ablation table exists for this solver-instance pair
            return []
        results = [["Round", "Flipped parameter", "Source value", "Target value",
                    "Validation result"]]

        for line in self.table_file.open().readlines():
            # Pre-process lines from the ablation file and add to the results dictionary.
            # Sometimes ablation rounds switch multiple parameters at once.
            # EXAMPLE: 2 EDR, EDRalpha   0, 0.1   1, 0.1013241633106732 486.31691
            # To split the row correctly, we remove the space before the comma separated
            # parameters and add it back.
            # T.S. 30-01-2024: the results object is a nested list not dictionary?
            values = re.sub(r"\s+", " ", line.strip())
            values = re.sub(r", ", ",", values)
            values = [val.replace(",", ", ") for val in values.split(" ")]
            if len(values) == 5:
                results.append(values)
        return results

    def submit_ablation(self: AblationScenario,
                        log_dir: Path,
                        sbatch_options: list[str] = [],
                        slurm_prepend: str | list[str] | Path = None,
                        run_on: Runner = Runner.SLURM) -> list[Run]:
        """Submit an ablation job.

        Args:
            log_dir: Directory to store job logs
            sbatch_options: Options to pass to sbatch
            slurm_prepend: Script to prepend to sbatch script
            run_on: Determines to which RunRunner queue the job is added

        Returns:
            A  list of Run objects. Empty when running locally.
        """
        # 1. submit the ablation to the runrunner queue
        cmd = (f"{AblationScenario.ablation_executable.absolute()} "
               "--optionFile ablation_config.txt")
        srun_options = ["-N1", "-n1", f"-c{self.concurrent_clis}"]
        sbatch_options += [f"--cpus-per-task={self.concurrent_clis}"]
        run_ablation = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=f"Ablation analysis: {self.solver.name} on {self.train_set.name}",
            base_dir=log_dir,
            path=self.scenario_dir,
            sbatch_options=sbatch_options,
            srun_options=srun_options,
            prepend=slurm_prepend)

        runs = []
        if run_on == Runner.LOCAL:
            run_ablation.wait()
        runs.append(run_ablation)

        # 2. Run ablation validation run if we have a test set to run on
        if self.test_set is not None:
            # Validation dir should have a copy of all needed files, except for the
            # output of the ablation run, which is stored in ablation-run[seed].txt
            cmd = f"{AblationScenario.ablation_validation_executable.absolute()} "\
                  "--optionFile ablation_config.txt "\
                  "--ablationLogFile ../log/ablation-run1234.txt"

            run_ablation_validation = rrr.add_to_queue(
                runner=run_on,
                cmd=cmd,
                name=f"Ablation validation: Test set {self.test_set.name}",
                path=self.validation_dir,
                base_dir=log_dir,
                dependencies=run_ablation,
                sbatch_options=sbatch_options,
                prepend=slurm_prepend)

            if run_on == Runner.LOCAL:
                run_ablation_validation.wait()
            runs.append(run_ablation_validation)
        return runs
