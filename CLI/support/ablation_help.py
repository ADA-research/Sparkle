#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for ablation analysis."""
import re
import shutil
import subprocess
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Run

import global_variables as gv

from sparkle.configurator.implementations import SMAC2
from CLI.help.command_help import CommandName
from sparkle.solver import Solver
from sparkle.instance import InstanceSet


def get_ablation_scenario_directory(solver: Solver, train_set: InstanceSet,
                                    test_set: InstanceSet, exec_path: str = False)\
        -> str:
    """Return the directory where ablation analysis is executed.

    exec_path: overwrite of the default ablation path to put the scenario in
    """
    test_extension = f"_{test_set.name}" if test_set is not None else ""

    ablation_scenario_dir = "" if exec_path else f"{gv.ablation_dir / 'scenarios'}/"
    scenario_dir = f"{ablation_scenario_dir}"\
                   f"{solver.name}_{train_set.name}{test_extension}/"
    return scenario_dir


def clean_ablation_scenarios(solver: Solver, train_set: InstanceSet) -> None:
    """Clean up ablation analysis directory."""
    ablation_scenario_dir = gv.ablation_dir / "scenarios"
    if ablation_scenario_dir.is_dir():
        for ablation_scenario in ablation_scenario_dir.glob(
                f"{solver.name}_{train_set.name}_*"):
            shutil.rmtree(ablation_scenario, ignore_errors=True)
    return


def prepare_ablation_scenario(solver: Solver, train_set: InstanceSet,
                              test_set: InstanceSet) -> Path:
    """Prepare directories and files for ablation analysis."""
    ablation_scenario_dir = get_ablation_scenario_directory(solver,
                                                            train_set,
                                                            test_set)

    ablation_scenario_solver_dir = Path(ablation_scenario_dir, "solver/")
    # Copy solver
    shutil.copytree(solver.directory, ablation_scenario_solver_dir, dirs_exist_ok=True)
    return ablation_scenario_dir


def print_ablation_help() -> None:
    """Print help information for ablation analysis."""
    process = subprocess.run([f"./{gv.ablation_dir}/ablationAnalysis", "-h"],
                             capture_output=True)
    print(process.stdout)


def create_configuration_file(solver: Solver, train_set: InstanceSet,
                              test_set: InstanceSet) -> None:
    """Create a configuration file for ablation analysis.

    Args:
        solver: Solver object
        instance_train_name: The training instance
        instance_test_name: The test instance

    Returns:
        None
    """
    ablation_scenario_dir = get_ablation_scenario_directory(solver,
                                                            train_set,
                                                            test_set)
    configurator = gv.settings.get_general_sparkle_configurator()
    _, opt_config_str = configurator.get_optimal_configuration(
        solver, train_set)
    if "-init_solution" not in opt_config_str:
        opt_config_str = "-init_solution '1' " + opt_config_str
    perf_measure = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    smac_run_obj = SMAC2.get_smac_run_obj(perf_measure)
    smac_each_run_cutoff_length = gv.settings.get_configurator_target_cutoff_length()
    smac_each_run_cutoff_time = gv.settings.get_general_target_cutoff_time()
    concurrent_clis = gv.settings.get_slurm_max_parallel_runs_per_node()
    ablation_racing = gv.settings.get_ablation_racing_flag()
    configurator = gv.settings.get_general_sparkle_configurator()

    with Path(f"{ablation_scenario_dir}/ablation_config.txt").open("w") as fout:
        # We need to append the solver dir to the configurator call to avoid
        # Issues with ablation's call to the wrapper
        fout.write(f'algo = "{configurator.configurator_target.absolute()} '
                   f'{Path(ablation_scenario_dir).absolute()}/solver"\n'
                   "execdir = ./solver/\n"
                   "experimentDir = ./\n")
        # USER SETTINGS
        fout.write(f"deterministic = {1 if solver.deterministic else 0}\n"
                   f"run_obj = {smac_run_obj}\n")
        objective_str = "MEAN10" if smac_run_obj == "RUNTIME" else "MEAN"
        fout.write(f"overall_obj = {objective_str}\n"
                   f"cutoffTime = {smac_each_run_cutoff_time}\n"
                   f"cutoff_length = {smac_each_run_cutoff_length}\n"
                   f"cli-cores = {concurrent_clis}\n"
                   f"useRacing = {ablation_racing}\n"
                   "seed = 1234\n")
        # Get PCS file name from solver directory
        pcs_file_path = f"./solver/{solver.get_pcs_file().name}"
        fout.write(f"paramfile = {pcs_file_path}\n"
                   "instance_file = instances_train.txt\n"
                   "test_instance_file = instances_test.txt\n"
                   "sourceConfiguration=DEFAULT\n"
                   f'targetConfiguration="{opt_config_str}"')
    return


def create_instance_file(instance_set: InstanceSet, ablation_scenario_dir: str,
                         test: bool = False) -> None:
    """Create an instance file for ablation analysis."""
    file_suffix = "_train.txt"
    if test:
        file_suffix = "_test.txt"
    # We give the Ablation script directly the paths of the instances (no copying)
    file_instance_path = ablation_scenario_dir + "instances" + file_suffix
    with Path(file_instance_path).open("w") as fh:
        for instance in instance_set.instance_paths:
            # We need to unpack the multi instance file paths in quotes
            if isinstance(instance, list):
                joined_instances = " ".join([str(file.absolute()) for file in instance])
                fh.write(f"{joined_instances}\n")
            else:
                fh.write(f"{instance.absolute()}\n")
    return


def check_for_ablation(solver: Solver, train_set: InstanceSet,
                       test_set: InstanceSet) -> bool:
    """Checks if ablation has terminated successfully."""
    scenario_dir = get_ablation_scenario_directory(solver, train_set,
                                                   test_set, exec_path=False)
    path = Path(scenario_dir, "ablationValidation.txt")
    if not path.is_file():
        return False
    return path.open().readline().strip() == "Ablation analysis validation complete."


def read_ablation_table(solver: Solver, train_set: InstanceSet,
                        test_set: InstanceSet) -> list[list[str]]:
    """Read from ablation table of a scenario."""
    if not check_for_ablation(solver, train_set, test_set):
        # No ablation table exists for this solver-instance pair
        return []
    scenario_dir = get_ablation_scenario_directory(solver, train_set,
                                                   test_set, exec_path=False)
    table_file = Path(scenario_dir) / "ablationValidation.txt"

    results = [["Round", "Flipped parameter", "Source value", "Target value",
                "Validation result"]]

    with Path(table_file).open("r") as fh:
        for line in fh.readlines():
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


def submit_ablation(ablation_scenario_dir: Path,
                    test_set: InstanceSet = None,
                    run_on: Runner = Runner.SLURM) -> list[Run]:
    """Submit an ablation job.

    Args:
        ablation_scenario_dir: The prepared dir where the ablation will be executed,
        test_set: The optional test set to run ablation on too.
        run_on: Determines to which RunRunner queue the job is added

    Returns:
        A  list of Run objects. Empty when running locally.
    """
    # This script sumbits 4 jobs: Normal, normal callback, validation, validation cb
    # The callback is nothing but a copy script from Albation/scenario/DIR/log to
    # the Log/Ablation/.. folder.

    # 1. submit the ablation to the runrunner queue
    clis = gv.settings.get_slurm_max_parallel_runs_per_node()
    cmd = "../../ablationAnalysis --optionFile ablation_config.txt"
    srun_options = ["-N1", "-n1", f"-c{clis}"]
    sbatch_options = [f"--cpus-per-task={clis}"] +\
        gv.settings.get_slurm_extra_options(as_args=True)

    run_ablation = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd,
        name=CommandName.RUN_ABLATION,
        base_dir=gv.sparkle_tmp_path,
        path=ablation_scenario_dir,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    dependencies = []
    if run_on == Runner.LOCAL:
        run_ablation.wait()
    dependencies.append(run_ablation)

    # 2. Submit intermediate actions (copy path from log)
    log_source = "log/ablation-run1234.txt"
    ablation_path = "ablationPath.txt"
    log_path = gv.sparkle_global_log_dir / "Ablation" / run_ablation.name
    log_path.mkdir(parents=True, exist_ok=True)

    cmd_list = [f"cp {log_source} {ablation_path}", f"cp -r log/ {log_path.absolute()}"]
    srun_options_cb = ["-N1", "-n1", "-c1"]
    run_cb = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.ABLATION_CALLBACK,
        path=ablation_scenario_dir,
        base_dir=gv.sparkle_tmp_path,
        dependencies=run_ablation,
        sbatch_options=sbatch_options,
        srun_options=srun_options_cb)

    if run_on == Runner.LOCAL:
        run_cb.wait()
    dependencies.append(run_cb)

    # 3. Submit ablation validation run when nessesary, repeat process for the test set
    if test_set is not None:
        # NOTE: The test set is not actually used?
        cmd = "../../ablationValidation --optionFile ablation_config.txt "\
            "--ablationLogFile ablationPath.txt"

        run_ablation_validation = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=CommandName.RUN_ABLATION_VALIDATION,
            path=ablation_scenario_dir,
            base_dir=gv.sparkle_tmp_path,
            dependencies=dependencies,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

        if run_on == Runner.LOCAL:
            run_ablation_validation.wait()
        dependencies.append(run_ablation_validation)

        log_source = "log/ablation-validation-run1234.txt"
        ablation_path = "ablationValidation.txt"
        val_dir = run_ablation_validation.name + "_validation"
        log_path = gv.sparkle_global_log_dir / "Ablation" / val_dir
        log_path.mkdir(parents=True, exist_ok=True)
        cmd_list = [f"cp {log_source} {ablation_path}",
                    f"cp -r log/ {log_path.absolute()}"]

        run_v_cb = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd_list,
            name=CommandName.ABLATION_VALIDATION_CALLBACK,
            path=ablation_scenario_dir,
            base_dir=gv.sparkle_tmp_path,
            dependencies=run_ablation_validation,
            sbatch_options=sbatch_options,
            srun_options=srun_options_cb)

        if run_on == Runner.LOCAL:
            run_v_cb.wait()
        dependencies.append(run_v_cb)

    return dependencies
