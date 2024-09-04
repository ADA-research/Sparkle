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

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl

from sparkle.configurator.implementations import SMAC2
from sparkle.platform import CommandName
from sparkle.solver import Solver
from sparkle.instance import InstanceSet


class AblationScenario:
    """Class for ablation analysis."""
    def __init__(self: AblationScenario,
                 solver: Solver,
                 train_set: InstanceSet,
                 test_set: InstanceSet,
                 output_dir: Path,
                 ablation_executable: Path = None,
                 ablation_validation_executable: Path = None,
                 override_dirs: bool = False) -> None:
        """Initialize ablation scenario.

        Args:
            solver: Solver object
            train_set: The training instance
            test_set: The test instance
            output_dir: The output directory
            ablation_executable: (Only for execution) The ablation executable
            ablation_validation_executable: (Only for execution) The validation exec
            override_dirs: Whether to clean the scenario directory if it already exists
        """
        self.ablation_exec = ablation_executable
        self.ablation_validation_exec = ablation_validation_executable
        self.solver = solver
        self.train_set = train_set
        self.test_set = test_set
        self.output_dir = output_dir
        self.scenario_name = f"{self.solver.name}_{self.train_set.name}"
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

    def create_configuration_file(self: AblationScenario) -> None:
        """Create a configuration file for ablation analysis.

        Args:
            solver: Solver object
            instance_train_name: The training instance
            instance_test_name: The test instance

        Returns:
            None
        """
        ablation_scenario_dir = self.scenario_dir
        objective = gv.settings().get_general_sparkle_objectives()[0]
        configurator = gv.settings().get_general_sparkle_configurator()
        _, opt_config_str = configurator.get_optimal_configuration(
            self.solver, self.train_set, objective=objective)

        # We need to check which params are missing and supplement with default values
        pcs = self.solver.get_pcs()
        for p in pcs:
            if p["name"] not in opt_config_str:
                opt_config_str += f" -{p['name']} {p['default']}"

        # Ablation cannot deal with E scientific notation in floats
        ctx = decimal.Context(prec=16)
        for config in opt_config_str.split(" -"):
            _, value = config.strip().split(" ")
            if "e" in value.lower():
                value = value.strip("'")
                float_value = float(value.lower())
                formatted = format(ctx.create_decimal(float_value), "f")
                opt_config_str = opt_config_str.replace(value, formatted)

        smac_run_obj = SMAC2.get_smac_run_obj(objective)
        objective_str = "MEAN10" if smac_run_obj == "RUNTIME" else "MEAN"
        run_cutoff_time = gv.settings().get_general_target_cutoff_time()
        run_cutoff_length = gv.settings().get_configurator_target_cutoff_length()
        concurrent_clis = gv.settings().get_slurm_max_parallel_runs_per_node()
        ablation_racing = gv.settings().get_ablation_racing_flag()
        configurator = gv.settings().get_general_sparkle_configurator()
        pcs_file_path = f"{self.solver.get_pcs_file().absolute()}"  # Get Solver PCS

        # Create config file
        config_file = Path(f"{ablation_scenario_dir}/ablation_config.txt")
        config = (f'algo = "{configurator.configurator_target.absolute()} '
                  f'{self.solver.directory.absolute()} {objective}"\n'
                  f"execdir = {self.tmp_dir.absolute()}\n"
                  "experimentDir = ./\n"
                  f"deterministic = {1 if self.solver.deterministic else 0}\n"
                  f"run_obj = {smac_run_obj}\n"
                  f"overall_obj = {objective_str}\n"
                  f"cutoffTime = {run_cutoff_time}\n"
                  f"cutoff_length = {run_cutoff_length}\n"
                  f"cli-cores = {concurrent_clis}\n"
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

    def create_instance_file(self: AblationScenario, test: bool = False) -> None:
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
                        run_on: Runner = Runner.SLURM) -> list[Run]:
        """Submit an ablation job.

        Args:
            run_on: Determines to which RunRunner queue the job is added

        Returns:
            A  list of Run objects. Empty when running locally.
        """
        # 1. submit the ablation to the runrunner queue
        clis = gv.settings().get_slurm_max_parallel_runs_per_node()
        cmd = f"{self.ablation_exec.absolute()} --optionFile ablation_config.txt"
        srun_options = ["-N1", "-n1", f"-c{clis}"]
        sbatch_options = [f"--cpus-per-task={clis}"] +\
            gv.settings().get_slurm_extra_options(as_args=True)

        run_ablation = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=CommandName.RUN_ABLATION,
            base_dir=sl.caller_log_dir,
            path=self.scenario_dir,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

        runs = []
        if run_on == Runner.LOCAL:
            run_ablation.wait()
        runs.append(run_ablation)

        # 2. Run ablation validation run if we have a test set to run on
        if self.test_set is not None:
            # Validation dir should have a copy of all needed files, except for the
            # output of the ablation run, which is stored in ablation-run[seed].txt
            cmd = f"{self.ablation_validation_exec.absolute()} "\
                  "--optionFile ablation_config.txt "\
                  "--ablationLogFile ../log/ablation-run1234.txt"

            run_ablation_validation = rrr.add_to_queue(
                runner=run_on,
                cmd=cmd,
                name=CommandName.RUN_ABLATION_VALIDATION,
                path=self.validation_dir,
                base_dir=sl.caller_log_dir,
                dependencies=run_ablation,
                sbatch_options=sbatch_options,
                srun_options=srun_options)

            if run_on == Runner.LOCAL:
                run_ablation_validation.wait()
            runs.append(run_ablation_validation)

        return runs
