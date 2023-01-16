#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for ablation analysis."""

import os
import sys
import re
import shutil
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_instances_help as sih
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_slurm_help as ssh


def get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name,
                                    exec_path=False):
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


def clean_ablation_scenarios(solver_name: str, instance_set_train_name: str):
    """Clean up ablation analysis directory."""
    ablation_scenario_dir = Path(sgh.ablation_dir + "scenarios/")
    if ablation_scenario_dir.is_dir():
        for ablation_scenario in ablation_scenario_dir.glob(
                f"{solver_name}_{instance_set_train_name}_*"):
            shutil.rmtree(ablation_scenario, ignore_errors=True)
    return


def prepare_ablation_scenario(solver_name, instance_train_name, instance_test_name):
    """Prepare directories and files for ablation analysis."""
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name,
                                                            instance_train_name,
                                                            instance_test_name)
    ablation_scenario_solver_dir = Path(ablation_scenario_dir, "solver/")

    Path(ablation_scenario_dir).mkdir(parents=True, exist_ok=True)
    ablation_scenario_solver_dir.mkdir(parents=True, exist_ok=True)

    # Copy ablation executables to isolated scenario directory
    copy_candidates = ["conf/", "lib/", "ablationAnalysis", "ablationAnalysis.jar",
                       "ablationValidation", "LICENSE.txt", "README.txt"]
    for candidate in copy_candidates:
        recursive = "-r" if candidate[-1] == "/" else ""
        candidate_path = str(PurePath(sgh.ablation_dir, candidate))
        cmd = f"cp {recursive} {candidate_path} {ablation_scenario_dir}"
        os.system(cmd)

    # Copy solver
    solver_directory = r"Solvers/" + solver_name + r"/*"
    cmd = f"cp -r {solver_directory} {ablation_scenario_solver_dir}"
    os.system(cmd)

    return ablation_scenario_dir


def print_ablation_help():
    """Print help information for ablation analysis."""
    call = f"./{sgh.ablation_dir}/ablationAnalysis -h"
    print(os.system(call))


def get_slurm_params(solver_name, instance_train_name, instance_test_name, postfix="",
                     dependency=None):
    """Return the Slurm settings to use."""
    if instance_test_name is not None:
        sbatch_script_name = (
            f"ablation_{solver_name}_"
            f"{instance_train_name}_{instance_test_name}"
        )
    else:
        sbatch_script_name = f"ablation_{solver_name}_{instance_train_name}"
    sbatch_script_name += f"{postfix}"

    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name,
                                                   instance_test_name, exec_path=True)
    concurrent_clis = sgh.settings.get_slurm_clis_per_node()

    job_name = "--job-name=" + sbatch_script_name
    output = "--output=" + sbatch_script_name + ".txt"
    error = "--error=" + sbatch_script_name + ".err"
    cpus = f"--cpus-per-task={concurrent_clis}"

    sbatch_options_list = [job_name, output, error, cpus]

    if dependency is not None:
        sbatch_options_list.append(f"--dependency=afterany:{dependency}")

    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    return (scenario_dir, sbatch_script_name, sbatch_options_list)


def generate_slurm_script(solver_name, instance_train_name, instance_test_name,
                          dependency=None):
    """Create a Slurm batch script."""
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name, postfix="",
        dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    srun_options_str = f"-N1 -n1 -c{concurrent_clis}"
    target_call_str = ("./ablationAnalysis --optionFile "
                       "ablation_config.txt")

    job_params_list = []
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str, target_call_str)

    return sbatch_script_name


def generate_callback_slurm_script(solver_name, instance_train_name, instance_test_name,
                                   dependency=None):
    """Create callback Slurm batch script for ablation analysis."""
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name, postfix="_callback",
        dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    callback_script_name = "callback.sh"
    callback_script_path = scenario_dir + callback_script_name
    log_path = sgh.sparkle_global_log_dir + "Ablation/" + sbatch_script_name + "/"

    Path(log_path).mkdir(parents=True, exist_ok=True)
    with open(sgh.ablation_dir + callback_script_path, "w") as fh:
        fh.write("#!/bin/bash\n")
        fh.write("# Automatically generated by SPARKLE\n\n")
        fh.write("cp log/ablation-run1234.txt ablationPath.txt\n")
        rollback = "../" * (len(scenario_dir.split("/")) + 1)
        fh.write(f"cp -r log/ {rollback}{log_path}\n")
        fh.close()
    os.system(f"chmod 755 {sgh.ablation_dir + callback_script_path}")

    srun_options_str = "-N1 -n1 -c1 --mem-per-cpu=1000"
    target_call_str = callback_script_name

    job_params_list = []
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str, target_call_str)

    return sbatch_script_name


def generate_validation_slurm_script(solver_name, instance_train_name,
                                     instance_test_name, dependency=None):
    """Create a Slurm batch script for ablation analysis validation."""
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name, postfix="_validation",
        dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    srun_options_str = f"-N1 -n1 -c{concurrent_clis}"
    target_call_str = ("./ablationValidation --optionFile ablation_config.txt "
                       "--ablationLogFile "
                       "ablationPath.txt")

    job_params_list = []
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str, target_call_str)

    return sbatch_script_name


def generate_validation_callback_slurm_script(solver_name, instance_train_name,
                                              instance_test_name, dependency=None):
    """Create callback Slurm batch script for ablation analysis validation."""
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(
        solver_name, instance_train_name, instance_test_name,
        postfix="_validation_callback", dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    callback_script_name = "validation_callback.sh"
    callback_script_path = scenario_dir + callback_script_name

    log_path = f"{sgh.sparkle_global_log_dir}Ablation/{sbatch_script_name}_validation/"

    Path(log_path).mkdir(parents=True, exist_ok=True)
    with open(sgh.ablation_dir + callback_script_path, "w") as fh:
        fh.write("#!/bin/bash\n")
        fh.write("# Automatically generated by SPARKLE\n\n")
        fh.write("cp log/ablation-validation-run1234.txt ablationValidation.txt"
                 "\n")
        rollback = "../" * (len(sgh.ablation_dir.split("/")) + 1)
        fh.write(f"cp -r log/ {rollback}{log_path}\n")
        fh.close()
    os.system(f"chmod 755 {sgh.ablation_dir + callback_script_path}")

    srun_options_str = "-N1 -n1 -c1 --mem-per-cpu=1000"
    target_call_str = callback_script_name

    job_params_list = []
    ssh.generate_sbatch_script_generic(f"{sgh.ablation_dir}{sbatch_script_path}",
                                       sbatch_options_list, job_params_list,
                                       srun_options_str,
                                       target_call_str)

    return sbatch_script_name


def create_configuration_file(solver_name, instance_train_name, instance_test_name):
    """Create a configuration file for ablation analysis."""
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name,
                                                            instance_train_name,
                                                            instance_test_name)

    optimised_configuration_params = scsh.get_optimised_configuration_params(
        solver_name, instance_train_name)

    (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
     smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str
     ) = scsh.get_smac_settings()
    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    ablation_racing = sgh.settings.get_ablation_racing_flag()

    with open(f"{ablation_scenario_dir}/ablation_config.txt", "w") as fout:
        fout.write("algo = ./sparkle_smac_wrapper.py\n")
        fout.write("execdir = ./solver/\n")
        fout.write("experimentDir = ./\n")

        # USER SETTINGS
        fout.write(f"deterministic = {scsh.get_solver_deterministic(solver_name)}\n")
        fout.write("run_obj = " + smac_run_obj + "\n")
        fout.write(
            "overall_obj = "
            f"{'MEAN10' if smac_run_obj == 'RUNTIME' else 'MEAN'}\n"
        )
        fout.write("cutoffTime = " + str(smac_each_run_cutoff_time) + "\n")
        fout.write("cutoff_length = " + str(smac_each_run_cutoff_length) + "\n")
        fout.write(f"cli-cores = {concurrent_clis}\n")
        fout.write(f"useRacing = {ablation_racing}\n")

        fout.write("seed = 1234\n")
        # Get PCS file name from solver directory
        solver_directory = Path("Solvers/", solver_name)
        pcs_file_name = scsh.get_pcs_file_from_solver_directory(solver_directory)
        pcs_file_path = "./solver/" + str(pcs_file_name)
        fout.write("paramfile = " + pcs_file_path + "\n")
        fout.write("instance_file = instances_train.txt\n")
        fout.write("test_instance_file = instances_test.txt\n")
        fout.write("sourceConfiguration=DEFAULT\n")
        fout.write(f'targetConfiguration="{optimised_configuration_params}"')
        fout.close()
    return


def create_instance_file(instances_directory, ablation_scenario_dir, train_or_test):
    """Create an instance file for ablation analysis."""
    if train_or_test == r"train":
        file_suffix = r"_train.txt"
    elif train_or_test == r"test":
        file_suffix = r"_test.txt"
    else:
        print('Invalid function call of "copy_instances_to_ablation"; stoping execution')
        sys.exit()

    if instances_directory[-1] != "/":
        instances_directory += "/"
    print(f"create_instance_file ({instances_directory}, {ablation_scenario_dir}, "
          f"{train_or_test})")
    list_all_path = sih.get_list_all_path(instances_directory)
    file_instance_path = ablation_scenario_dir + "instances" + file_suffix

    # Relative path
    pwd = os.getcwd()
    full_ablation_scenario_dir = os.path.join(pwd, ablation_scenario_dir, "solver/")
    full_instances_directory = os.path.join(pwd, instances_directory)
    relative_instance_directory = os.path.relpath(full_instances_directory,
                                                  full_ablation_scenario_dir)

    instance_set_name = Path(instances_directory).name

    # If a reference list does not exist this is a single-file instance
    if not sih.check_existence_of_reference_instance_list(instance_set_name):
        list_all_path = [str(instance)[len(instances_directory):]
                         for instance in list_all_path]

        with open(file_instance_path, "w") as fh:
            for instance in list_all_path:
                instance_path = f"{os.path.join(relative_instance_directory,instance)}\n"
                fh.write(instance_path)

            fh.close()
    # Otherwise this is a multi-file instance, and instances need to be wrapped in quotes
    # with function below
    # TODO: Check whether this function also works for single-file instances and can be
    # used in all cases
    else:
        relative_instance_directory = relative_instance_directory + "/"
        sih.copy_reference_instance_list(Path(file_instance_path), instance_set_name,
                                         relative_instance_directory)

    return


def check_for_ablation(solver_name, instance_train_name, instance_test_name) -> bool:
    """Run a solver on an instance, only for internal calls from Sparkle."""
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name,
                                                   instance_test_name, exec_path=False)
    table_file = Path(scenario_dir, "ablationValidation.txt")
    if not table_file.is_file():
        return False
    fh = open(table_file, "r")
    first_line = fh.readline().strip()
    fh.close()
    if first_line != "Ablation analysis validation complete.":
        return False

    return True


def get_ablation_table(solver_name, instance_train_name, instance_test_name):
    """Run a solver on an instance, only for internal calls from Sparkle."""
    if not check_for_ablation(solver_name, instance_train_name, instance_test_name):
        # No ablation table exists for this solver-instance pair
        return dict()
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name,
                                                   instance_test_name, exec_path=False)
    print(scenario_dir)
    table_file = os.path.join(scenario_dir, "ablationValidation.txt")

    results = [["Round", "Flipped parameter", "Source value", "Target value",
                "Validation result"]]

    with open(table_file, "r") as fh:
        for line in fh.readlines():
            # Pre-process lines from the ablation file and add to the results dictionary.
            # Sometimes ablation rounds switch multiple parameters at once.
            # EXAMPLE: 2 EDR, EDRalpha   0, 0.1   1, 0.1013241633106732 486.31691
            # To split the row correctly, we remove the space before the comma separated
            # parameters and add it back.
            values = re.sub(r"\s+", " ", line.strip())
            values = re.sub(r", ", ",", values)
            values = [val.replace(",", ", ") for val in values.split(" ")]
            if len(values) == 5:
                results.append(values)

        fh.close()

    return results
