#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for ablation analysis."""

import sys
import stat
import re
import shutil
import subprocess
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_instances_help as sih
from Commands.sparkle_help import sparkle_configure_solver_help as scsh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help.sparkle_command_help import CommandName

from sparkle.slurm_parsing import SlurmBatch
import runrunner as rrr
from runrunner.base import Runner


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


def get_slurm_params(solver_name: str, instance_train_name: str, instance_test_name: str,
                     postfix: str = "", dependency: str = None) -> tuple[str]:
    """Return the Slurm settings to use."""
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name,
                                                   instance_test_name, exec_path=True)

    sbatch_script_name = f"ablation_{solver_name}_{instance_train_name}"
    if instance_test_name is not None:
        sbatch_script_name = f"{sbatch_script_name}_{instance_test_name}"
    sbatch_script_name = f"{sbatch_script_name}{postfix}"

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    sbatch_options_list = [f"--job-name={sbatch_script_name}",
                           f"--output={sbatch_script_name}.txt",
                           f"--error={sbatch_script_name}.err",
                           f"--cpus-per-task={concurrent_clis}"]
    if dependency is not None:
        sbatch_options_list.append(f"--dependency=afterany:{dependency}")
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    return (scenario_dir, sbatch_script_name, sbatch_options_list)


def generate_slurm_script(solver_name: str, instance_train_name: str,
                          instance_test_name: str, dependency: str = None) -> str:
    """Create a Slurm batch script."""
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name, postfix="",
        dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    srun_options_str = f"-N1 -n1 -c{concurrent_clis}"
    target_call_str = ("../../ablationAnalysis --optionFile "
                       "ablation_config.txt")
    job_params_list = []
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str, target_call_str)

    return sbatch_script_name


def generate_callback_slurm_script(solver_name: str, instance_train_name: str,
                                   instance_test_name: str, dependency: str = None,
                                   validation: bool = False) -> str:
    """Create callback Slurm batch script for ablation analysis.

    Args:
        solver_name: Name of the Solver
        instance_train_name: Train instance
        instance_test_name: Test instance
        dependency: The original job ID this script is calling back on
        validation: Boolean indicating whether its regular or validation script

    Returns:
        str, name of the sbatch script
    """
    postfix = "_callback"
    callback_script_name = "callback.sh"

    if validation:
        postfix = "_validation_callback"
        callback_script_name = "validation_callback.sh"

    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name, postfix=postfix,
        dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name
    log_path = sgh.sparkle_global_log_dir + "Ablation/" + sbatch_script_name
    if validation:
        log_path += "_validation/"
    else:
        log_path += "/"

    callback_script_path = Path(sgh.ablation_dir + scenario_dir + callback_script_name)
    Path(log_path).mkdir(parents=True, exist_ok=True)
    log_source = "log/ablation-run1234.txt"
    ablation_path = "ablationPath.txt"
    rollback = "../" * (len(scenario_dir.split("/")) + 1)
    if validation:
        log_source = "log/ablation-validation-run1234.txt"
        ablation_path = "ablationValidation.txt"
        rollback = "../" * (len(sgh.ablation_dir.split("/")) + 1)

    with callback_script_path.open("w") as fh:
        fh.write("#!/bin/bash\n"
                 "# Automatically generated by SPARKLE\n\n"
                 f"cp {log_source} {ablation_path}\n"
                 f"cp -r log/ {rollback}{log_path}\n")

    callback_script_path.chmod(mode=callback_script_path.stat().st_mode | stat.S_IEXEC)

    job_params_list = []
    srun_options_str = "-N1 -n1 -c1"
    target_call_str = "./" + callback_script_name
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str, target_call_str)

    return sbatch_script_name


def generate_validation_slurm_script(solver_name: str, instance_train_name: str,
                                     instance_test_name: str, dependency: str = None)\
        -> str:
    """Create a Slurm batch script for ablation analysis validation."""
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name, postfix="_validation",
        dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    srun_options_str = f"-N1 -n1 -c{concurrent_clis}"
    target_call_str = ("../../ablationValidation --optionFile ablation_config.txt "
                       "--ablationLogFile "
                       "ablationPath.txt")
    job_params_list = []
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str, target_call_str)

    return sbatch_script_name


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

    with Path(f"{ablation_scenario_dir}/ablation_config.txt").open("w") as fout:
        fout.write(f"algo = ../../../../../{sgh.smac_dir}{sgh.smac_target_algorithm}\n"
                   "execdir = ./solver/\n"
                   "experimentDir = ./\n")

        # USER SETTINGS
        fout.write(f"deterministic = {scsh.get_solver_deterministic(solver_name)}\n"
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
        pcs_file_name = scsh.get_pcs_file_from_solver_directory(solver_directory)
        pcs_file_path = "./solver/" + str(pcs_file_name)
        fout.write(f"paramfile = {pcs_file_path}\n"
                   "instance_file = instances_train.txt\n"
                   "test_instance_file = instances_test.txt\n"
                   "sourceConfiguration=DEFAULT\n"
                   f'targetConfiguration="{optimised_configuration_params}"')
    return


def create_instance_file(instances_directory: str, ablation_scenario_dir: str,
                         train_or_test: str) -> None:
    """Create an instance file for ablation analysis."""
    if train_or_test == "train":
        file_suffix = "_train.txt"
    elif train_or_test == "test":
        file_suffix = "_test.txt"
    else:
        print("Invalid function call of copy_instances_to_ablation; stopping execution")
        sys.exit(-1)

    if instances_directory[-1] != "/":
        instances_directory += "/"

    list_all_path = sih.get_list_all_path(instances_directory)
    file_instance_path = ablation_scenario_dir + "instances" + file_suffix

    # Relative path
    pwd = Path.cwd()
    full_ablation_scenario_dir = Path(pwd) / ablation_scenario_dir / "solver/"
    full_instances_directory = Path(pwd) / instances_directory
    relative_instance_directory = (Path(full_instances_directory)
                                   / full_ablation_scenario_dir)

    instance_set_name = Path(instances_directory).name

    # If a reference list does not exist this is a single-file instance
    if not sih.check_existence_of_reference_instance_list(instance_set_name):
        list_all_path = [str(instance)[len(instances_directory):]
                         for instance in list_all_path]

        with Path(file_instance_path).open("w") as fh:
            for instance in list_all_path:
                instance_path = f"{relative_instance_directory / instance}\n"
                fh.write(instance_path)
    # Otherwise this is a multi-file instance, and instances need to be wrapped in quotes
    # with function below
    # TODO: Check whether this function also works for single-file instances and can be
    # used in all cases
    else:
        relative_instance_directory = relative_instance_directory + "/"
        sih.copy_reference_instance_list(Path(file_instance_path), instance_set_name,
                                         relative_instance_directory)

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


def get_ablation_table(solver_name: str, instance_train_name: str,
                       instance_test_name: str) -> list[list[str]]:
    """Run a solver on an instance, only for internal calls from Sparkle."""
    if not check_for_ablation(solver_name, instance_train_name, instance_test_name):
        # No ablation table exists for this solver-instance pair
        return dict()
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


def submit_ablation_sparkle(solver_name: str,
                            instance_set_test: str,
                            instance_set_train_name: str,
                            instance_set_test_name: str,
                            ablation_scenario_dir: str) -> list[str]:
    """Sends an ablation to Slurm using Sparkle's internal mechanics.

    Args:
        solver_name:
        instance_set_test:
        instance_set_train_name:
        instance_set_test_name:
        ablation_scenario_dir:

    Returns:
        List of job id's corresponding to jobs launched in this method
    """
    sbatch_script_path = generate_slurm_script(solver_name, instance_set_train_name,
                                               instance_set_test_name)
    print(f"Created {sbatch_script_path}")
    dependency_jobid_list = []

    jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.RUN_ABLATION,
                                     ablation_scenario_dir)
    dependency_jobid_list.append(jobid)
    print(f"Launched sbatch script {sbatch_script_path} with jobid {jobid}")

    # Submit intermediate actions (copy path from log)
    sbatch_script_path = generate_callback_slurm_script(solver_name,
                                                        instance_set_train_name,
                                                        instance_set_test_name,
                                                        dependency=jobid)
    jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.RUN_ABLATION,
                                     ablation_scenario_dir)
    dependency_jobid_list.append(jobid)
    print(f"Launched callback sbatch script {sbatch_script_path} with jobid {jobid}")

    # Submit ablation validation run when nessesary
    if instance_set_test is not None:
        sbatch_script_path = generate_validation_slurm_script(
            solver_name,
            instance_set_train_name,
            instance_set_test_name,
            dependency=jobid)
        jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.RUN_ABLATION,
                                         ablation_scenario_dir)
        dependency_jobid_list.append(jobid)
        print(f"Launched validation sbatch script {sbatch_script_path}"
              f"with jobid {jobid}")

        # Submit intermediate actions (copy validation table from log)
        sbatch_script_path = generate_callback_slurm_script(
            solver_name,
            instance_set_train_name,
            instance_set_test_name,
            dependency=jobid,
            validation=True
        )
        jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.RUN_ABLATION,
                                         ablation_scenario_dir)
        dependency_jobid_list.append(jobid)
        print(f"Launched validation callback sbatch script {sbatch_script_path} with "
              f"jobid {jobid}")

    return dependency_jobid_list


def submit_ablation_runrunner(solver_name: str,
                              instance_set_test: str,
                              instance_set_train_name: str,
                              instance_set_test_name: str,
                              ablation_scenario_dir: str,
                              run_on: Runner = Runner.SLURM) -> list[str]:
    """Sends an ablation to the RunRunner queue.

    Args:
        solver_name:
        instance_set_test:
        instance_set_train_name:
        instance_set_test_name:
        ablation_scenario_dir:
        run_on: Determines to which RunRunner queue the job is added

    Returns:
        A (potential empty) list of Slurm job id strings. Empty when running locally.
    """
    # This script sumbits 4 jobs: Normal, normal callback, validation, validation cb
    # The callback is nothing but a copy script from Albation/scenario/DIR/log to
    # the Log/Ablation/.. folder. This should be avoidable.
    # 1. submit the ablation to the runrunner queue
    # Remove the below if block once runrunner works satisfactorily
    if run_on == Runner.SLURM_RR:
        run_on = Runner.SLURM
    sbatch_script_path = generate_slurm_script(
        solver_name, instance_set_train_name, instance_set_test_name
    )
    batch = SlurmBatch(ablation_scenario_dir + sbatch_script_path)
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=batch.cmd,
        name=CommandName.RUN_ABLATION,
        path=ablation_scenario_dir,
        sbatch_options=batch.sbatch_options,
        srun_options=batch.srun_options)

    print(f"Created {batch.file}")
    dependency = []
    if run_on == Runner.LOCAL:
        run.wait()
    else:
        dependency.append(run.run_id)

    # 2. Submit intermediate actions (copy path from log)
    sbatch_script_path = generate_callback_slurm_script(
        solver_name, instance_set_train_name, instance_set_test_name
    )
    batch = SlurmBatch(ablation_scenario_dir + sbatch_script_path)
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=batch.cmd,
        name=CommandName.RUN_ABLATION,
        path=ablation_scenario_dir,
        dependency=dependency,
        sbatch_options=batch.sbatch_options,
        srun_options=batch.srun_options)

    print(f"Created {batch.file}")
    if run_on == Runner.LOCAL:
        run.wait()
    else:
        dependency.append(run.run_id)

    # 3. Submit ablation validation run when nessesary, repeat process for the test set
    if instance_set_test is not None:
        sbatch_script_path = generate_validation_slurm_script(
            solver_name,
            instance_set_train_name,
            instance_set_test_name)

        batch = SlurmBatch(ablation_scenario_dir + sbatch_script_path)
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=batch.cmd,
            name=CommandName.RUN_ABLATION,
            path=ablation_scenario_dir,
            sbatch_options=batch.sbatch_options,
            srun_options=batch.srun_options)
        print(f"Created {batch.file}")
        if run_on == Runner.LOCAL:
            run.wait()
        else:
            dependency.append(run.run_id)
        # Submit intermediate actions (copy validation table from log)
        sbatch_script_path = generate_callback_slurm_script(
            solver_name,
            instance_set_train_name,
            instance_set_test_name,
            validation=True
        )
        batch = SlurmBatch(ablation_scenario_dir + sbatch_script_path)
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=batch.cmd,
            name=CommandName.RUN_ABLATION,
            path=ablation_scenario_dir,
            sbatch_options=batch.sbatch_options,
            srun_options=batch.srun_options)

        print(f"Created {batch.file}")
        if run_on == Runner.LOCAL:
            run.wait()
        else:
            dependency.append(run.run_id)
    # Remove the below if block once runrunner works satisfactorily
    if run_on == Runner.SLURM_RR:
        run_on = Runner.SLURM
    return dependency
