#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for ablation analysis."""
import re
import shutil
import subprocess
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

import global_variables as sgh
from sparkle.instance import instances_help as sih
from CLI.support import configure_solver_help as scsh
from sparkle.platform import slurm_help as ssh
from CLI.help.command_help import CommandName
from sparkle.solver.solver import Solver
from sparkle.solver import pcs


def get_ablation_scenario_directory(solver_name: str, instance_train_name: str,
                                    instance_test_name: str, exec_path: str = False)\
        -> str:
    """Return the directory where ablation analysis is executed.

    exec_path: overwrite of the default ablation path to put the scenario in
    """
    instance_test_name = (
        f"_{instance_test_name}" if instance_test_name is not None else "")

    ablation_scenario_dir = "" if exec_path else sgh.ablation_dir
    ablation_scenario_dir += (
        f"scenarios/{solver_name}_"
        f"{instance_train_name}{instance_test_name}/"
    )
    return ablation_scenario_dir


def clean_ablation_scenarios(solver_name: str, instance_set_train_name: str) -> None:
    """Clean up ablation analysis directory."""
    ablation_scenario_dir = Path(sgh.ablation_dir + "scenarios/")
    if ablation_scenario_dir.is_dir():
        for ablation_scenario in ablation_scenario_dir.glob(
                f"{solver_name}_{instance_set_train_name}_*"):
            shutil.rmtree(ablation_scenario, ignore_errors=True)
    return


def prepare_ablation_scenario(solver_name: str, instance_train_name: str,
                              instance_test_name: str) -> str:
    """Prepare directories and files for ablation analysis."""
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name,
                                                            instance_train_name,
                                                            instance_test_name)

    ablation_scenario_solver_dir = Path(ablation_scenario_dir, "solver/")
    # Copy solver
    solver_directory = "Solvers/" + solver_name
    shutil.copytree(solver_directory, ablation_scenario_solver_dir, dirs_exist_ok=True)
    return ablation_scenario_dir


def print_ablation_help() -> None:
    """Print help information for ablation analysis."""
    process = subprocess.run([f"./{sgh.ablation_dir}/ablationAnalysis", "-h"],
                             capture_output=True)
    print(process.stdout)


def create_configuration_file(solver_name: str, instance_train_name: str,
                              instance_test_name: str) -> None:
    """Create a configuration file for ablation analysis.

    Args:
        solver_name: Name of the solver
        instance_train_name: The training instance
        instance_test_name: The test instance

    Returns:
        None
    """
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name,
                                                            instance_train_name,
                                                            instance_test_name)

    optimised_configuration_params = scsh.get_optimised_configuration_params(
        solver_name, instance_train_name)

    (smac_run_obj, _, smac_each_run_cutoff_time,
     smac_each_run_cutoff_length, _, _) = scsh.get_smac_settings()
    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    ablation_racing = sgh.settings.get_ablation_racing_flag()
    configurator = sgh.settings.get_general_sparkle_configurator()

    with Path(f"{ablation_scenario_dir}/ablation_config.txt").open("w") as fout:
        fout.write(f"algo = {configurator.configurator_target.absolute()}\n"
                   "execdir = ./solver/\n"
                   "experimentDir = ./\n")
        solver = Solver.get_solver_by_name(solver_name)
        # USER SETTINGS
        fout.write(f"deterministic = {solver.is_deterministic()}\n"
                   f"run_obj = {smac_run_obj}\n")
        objective_str = "MEAN10" if smac_run_obj == "RUNTIME" else "MEAN"
        fout.write(f"overall_obj = {objective_str}\n"
                   f"cutoffTime = {smac_each_run_cutoff_time}\n"
                   f"cutoff_length = {smac_each_run_cutoff_length}\n"
                   f"cli-cores = {concurrent_clis}\n"
                   f"useRacing = {ablation_racing}\n"
                   "seed = 1234\n")
        # Get PCS file name from solver directory
        solver_directory = Path("Solvers/", solver_name)
        pcs_file_name = pcs.get_pcs_file_from_solver_directory(solver_directory)
        pcs_file_path = "./solver/" + str(pcs_file_name)
        fout.write(f"paramfile = {pcs_file_path}\n"
                   "instance_file = instances_train.txt\n"
                   "test_instance_file = instances_test.txt\n"
                   "sourceConfiguration=DEFAULT\n"
                   f'targetConfiguration="{optimised_configuration_params}"')
    return


def create_instance_file(instances_directory: str, ablation_scenario_dir: str,
                         test: bool = False) -> None:
    """Create an instance file for ablation analysis."""
    file_suffix = "_train.txt"
    if test:
        file_suffix = "_test.txt"

    # We give the Ablation script directly the paths of the instances (no copying)
    list_all_path = sih.get_list_all_path(instances_directory)
    file_instance_path = ablation_scenario_dir + "instances" + file_suffix

    instance_set_name = Path(instances_directory).name

    # If a reference list does not exist this is a single-file instance
    if not sih.check_existence_of_reference_instance_list(instance_set_name):
        with Path(file_instance_path).open("w") as fh:
            for instance in list_all_path:
                fh.write(f"{instance.absolute()}\n")
    # Otherwise this is a multi-file instance, and instances need to be wrapped in quotes
    # with function below
    # TODO: Check whether this function also works for single-file instances and can be
    # used in all cases
    else:
        sih.copy_reference_instance_list(Path(file_instance_path), instance_set_name,
                                         "")
    return


def check_for_ablation(solver_name: str, instance_train_name: str,
                       instance_test_name: str) -> bool:
    """Run a solver on an instance, only for internal calls from Sparkle."""
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name,
                                                   instance_test_name, exec_path=False)
    table_file = Path(scenario_dir, "ablationValidation.txt")
    if not table_file.is_file():
        return False
    with table_file.open("r") as fh:
        if fh.readline().strip() != "Ablation analysis validation complete.":
            return False

    return True


def read_ablation_table(solver_name: str, instance_train_name: str,
                        instance_test_name: str) -> list[list[str]]:
    """Read from ablation table of a scenario."""
    if not check_for_ablation(solver_name, instance_train_name, instance_test_name):
        # No ablation table exists for this solver-instance pair
        return []
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name,
                                                   instance_test_name, exec_path=False)
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


def submit_ablation(ablation_scenario_dir: str,
                    instance_set_test: str = None,
                    run_on: Runner = Runner.SLURM) -> list[rrr.SlurmRun]:
    """Submit an ablation job.

    Args:
        ablation_scenario_dir: The prepared dir where the ablation will be executed,
        instance_set_test: The optional test set to run ablation on too.
        run_on: Determines to which RunRunner queue the job is added

    Returns:
        A (potential empty) list of SlurmJobs. Empty when running locally.
    """
    # This script sumbits 4 jobs: Normal, normal callback, validation, validation cb
    # The callback is nothing but a copy script from Albation/scenario/DIR/log to
    # the Log/Ablation/.. folder.

    # 1. submit the ablation to the runrunner queue
    clis = sgh.settings.get_slurm_clis_per_node()
    cmd = "../../ablationAnalysis --optionFile ablation_config.txt"
    srun_options = ["-N1", "-n1", f"-c{clis}"]
    sbatch_options = [f"--cpus-per-task={clis}"] +\
        ssh.get_slurm_options_list()

    run_ablation = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd,
        name=CommandName.RUN_ABLATION,
        base_dir=sgh.sparkle_tmp_path,
        path=ablation_scenario_dir,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    dependencies = []
    if run_on == Runner.LOCAL:
        run_ablation.wait()
    else:
        dependencies.append(run_ablation)

    # 2. Submit intermediate actions (copy path from log)
    log_source = "log/ablation-run1234.txt"
    ablation_path = "ablationPath.txt"
    log_path = Path(sgh.sparkle_global_log_dir) / "Ablation" / run_ablation.name
    log_path.mkdir(parents=True, exist_ok=True)

    cmd_list = [f"cp {log_source} {ablation_path}", f"cp -r log/ {log_path.absolute()}"]
    srun_options_cb = ["-N1", "-n1", "-c1"]
    run_cb = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.ABLATION_CALLBACK,
        path=ablation_scenario_dir,
        base_dir=sgh.sparkle_tmp_path,
        dependencies=run_ablation,
        sbatch_options=sbatch_options,
        srun_options=srun_options_cb)

    if run_on == Runner.LOCAL:
        run_cb.wait()
    else:
        dependencies.append(run_cb)

    # 3. Submit ablation validation run when nessesary, repeat process for the test set
    if instance_set_test is not None:
        cmd = "../../ablationValidation --optionFile ablation_config.txt "\
            "--ablationLogFile ablationPath.txt"

        run_ablation_validation = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=CommandName.RUN_ABLATION_VALIDATION,
            path=ablation_scenario_dir,
            base_dir=sgh.sparkle_tmp_path,
            dependencies=dependencies,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

        if run_on == Runner.LOCAL:
            run_ablation_validation.wait()
        else:
            dependencies.append(run_ablation_validation)

        log_source = "log/ablation-validation-run1234.txt"
        ablation_path = "ablationValidation.txt"
        val_dir = run_ablation_validation.name + "_validation"
        log_path = Path(sgh.sparkle_global_log_dir) / "Ablation" / val_dir
        log_path.mkdir(parents=True, exist_ok=True)
        cmd_list = [f"cp {log_source} {ablation_path}",
                    f"cp -r log/ {log_path.absolute()}"]

        run_v_cb = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd_list,
            name=CommandName.ABLATION_VALIDATION_CALLBACK,
            path=ablation_scenario_dir,
            base_dir=sgh.sparkle_tmp_path,
            dependencies=run_ablation_validation,
            sbatch_options=sbatch_options,
            srun_options=srun_options_cb)

        if run_on == Runner.LOCAL:
            run_v_cb.wait()
        else:
            dependencies.append(run_v_cb)

    return dependencies
