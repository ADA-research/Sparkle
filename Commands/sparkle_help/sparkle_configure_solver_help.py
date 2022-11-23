#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for algorithm configuration."""

import os
import sys
import fcntl
import shutil
from pathlib import Path
from pathlib import PurePath
from enum import Enum

try:
    from sparkle_help import sparkle_file_help as sfh
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_logging as sl
    from sparkle_help import sparkle_slurm_help as ssh
    from sparkle_help.sparkle_settings import PerformanceMeasure
    from sparkle_help import sparkle_instances_help as sih
    from sparkle_help.sparkle_command_help import CommandName
    from sparkle_help import sparkle_job_help as sjh
except ImportError:
    import sparkle_file_help as sfh
    import sparkle_global_help as sgh
    import sparkle_logging as sl
    import sparkle_slurm_help as ssh
    from sparkle_settings import PerformanceMeasure
    import sparkle_instances_help as sih
    from sparkle_command_help import CommandName
    import sparkle_job_help as sjh


class InstanceType(Enum):
    """Enum of possible instance types."""

    TRAIN = 1
    TEST = 2


def get_smac_run_obj() -> str:
    """Return the SMAC run objective."""
    # Get smac_run_obj from general settings
    smac_run_obj = sgh.settings.get_general_performance_measure()

    # Convert to SMAC format
    if smac_run_obj == PerformanceMeasure.RUNTIME:
        smac_run_obj = smac_run_obj.name
    elif smac_run_obj == PerformanceMeasure.QUALITY_ABSOLUTE:
        smac_run_obj = "QUALITY"
    else:
        print("Warning: Unknown performance measure", smac_run_obj,
              "! This is a bug in Sparkle.")

    return smac_run_obj


def get_smac_settings():
    """Return the SMAC settings."""
    smac_each_run_cutoff_length = sgh.settings.get_smac_target_cutoff_length()
    smac_run_obj = get_smac_run_obj()
    smac_whole_time_budget = sgh.settings.get_config_budget_per_run()
    smac_each_run_cutoff_time = sgh.settings.get_general_target_cutoff_time()
    num_of_smac_run = sgh.settings.get_config_number_of_runs()
    num_of_smac_run_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()

    return (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
            smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel)


def copy_file_instance(solver_name: str, instance_set_train_name: str,
                       instance_set_target_name: str, instance_type: str) -> None:
    """Copy file with the specified postfix listing instances to the solver directory."""
    file_postfix = f"_{instance_type}.txt"

    smac_solver_dir = get_smac_solver_dir(solver_name, instance_set_train_name)
    smac_file_instance_path_ori = (f"{sgh.smac_dir}/example_scenarios/instances/"
                                   f"{instance_set_target_name}{file_postfix}")
    smac_file_instance_path_target = (
        smac_solver_dir + instance_set_target_name + file_postfix)

    command_line = f"cp {smac_file_instance_path_ori} {smac_file_instance_path_target}"
    os.system(command_line)

    log_str = "List of instances to be used for configuration"
    sl.add_output(smac_file_instance_path_target, log_str)

    return


def get_solver_deterministic(solver_name: str) -> str:
    """Return a str indicating whether a given solver is deterministic or not."""
    deterministic = ""
    target_solver_path = "Solvers/" + solver_name
    solver_list_path = sgh.solver_list_path

    fin = open(solver_list_path, "r+")
    fcntl.flock(fin.fileno(), fcntl.LOCK_EX)

    while True:
        myline = fin.readline()
        if not myline:
            break
        myline = myline.strip()
        mylist = myline.split()

        if (mylist[0] == target_solver_path):
            deterministic = mylist[1]
            break

    return deterministic


def create_file_scenario_validate(solver_name: str, instance_set_train_name: str,
                                  instance_set_val_name: str,
                                  instance_type: InstanceType, default: bool) -> str:
    """Create a file with the configuration scenario to be used for SMAC validation.

    This will be located in the solver directory.
    """
    if instance_type is InstanceType.TRAIN:
        inst_type = "train"
    else:
        inst_type = "test"

    if default is True:
        config_type = "default"
    else:
        config_type = "configured"

    smac_solver_dir = get_smac_solver_dir(solver_name, instance_set_train_name)
    scenario_file_name = (
        f"{instance_set_val_name}_{inst_type}_{config_type}_scenario.txt")
    smac_file_scenario = smac_solver_dir + scenario_file_name

    (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
     smac_each_run_cutoff_length, _, _) = get_smac_settings()

    smac_paramfile = (f"example_scenarios/{solver_name}_{instance_set_train_name}/"
                      f"{get_pcs_file_from_solver_directory(smac_solver_dir)}")
    if instance_type == InstanceType.TRAIN:
        smac_outdir = (f"example_scenarios/{solver_name}_{instance_set_train_name}/"
                       f"outdir_{inst_type}_{config_type}/")
    else:
        smac_outdir = (f"example_scenarios/{solver_name}_{instance_set_train_name}/"
                       f"outdir_{instance_set_val_name}_{inst_type}_{config_type}/")
    smac_instance_file = (f"example_scenarios/{solver_name}_{instance_set_train_name}/"
                          f"{instance_set_val_name}_{inst_type}.txt")
    smac_test_instance_file = smac_instance_file

    fout = open(smac_file_scenario, "w+")
    fout.write("algo = ./" + sgh.sparkle_smac_wrapper + "\n")
    fout.write(f"execdir = example_scenarios/{solver_name}_{instance_set_train_name}/\n")
    fout.write("deterministic = " + get_solver_deterministic(solver_name) + "\n")
    fout.write("run_obj = " + smac_run_obj + "\n")
    fout.write("wallclock-limit = " + str(smac_whole_time_budget) + "\n")
    fout.write("cutoffTime = " + str(smac_each_run_cutoff_time) + "\n")
    fout.write("cutoff_length = " + smac_each_run_cutoff_length + "\n")
    fout.write("paramfile = " + smac_paramfile + "\n")
    fout.write("outdir = " + smac_outdir + "\n")
    fout.write("instance_file = " + smac_instance_file + "\n")
    fout.write("test_instance_file = " + smac_test_instance_file + "\n")
    fout.close()

    # Log scenario file location
    log_str = (f"SMAC Scenario file for the validation of the {config_type} solver "
               f"{solver_name} on the {inst_type}ing set")
    sl.add_output(smac_file_scenario, log_str)

    return scenario_file_name


def create_file_scenario_configuration(solver_name: str, instance_set_name: str,
                                       use_features: bool = False):
    """Create a file with the configuration scenario in the solver directory."""
    solver_instance_name = f"{solver_name}_{instance_set_name}"
    solver_instance_dir = Path("example_scenarios", solver_instance_name)

    smac_solver_dir = Path(get_smac_solver_dir(solver_name, instance_set_name))
    smac_file_scenario = Path(smac_solver_dir, f"{solver_instance_name}_scenario.txt")
    smac_paramfile = Path(get_pcs_file_from_solver_directory(smac_solver_dir))

    smac_paramfile_dir = solver_instance_dir / smac_paramfile
    smac_outdir = solver_instance_dir / "outdir_train_configuration/"
    smac_instance_file = solver_instance_dir / f"{instance_set_name}_train.txt"
    smac_feature_file = solver_instance_dir / f"{instance_set_name}_features.csv"

    (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
     smac_each_run_cutoff_length, _, _) = get_smac_settings()

    fout = open(smac_file_scenario, "w")
    fout.write(f"algo = ./{sgh.sparkle_smac_wrapper}\n")
    fout.write(f"execdir = {solver_instance_dir}/\n")
    fout.write(f"deterministic = {get_solver_deterministic(solver_name)}\n")
    fout.write(f"run_obj = {smac_run_obj}\n")
    fout.write(f"wallclock-limit = {smac_whole_time_budget}\n")
    fout.write(f"cutoffTime = {smac_each_run_cutoff_time}\n")
    fout.write(f"cutoff_length = {smac_each_run_cutoff_length}\n")
    fout.write(f"paramfile = {smac_paramfile_dir}\n")
    fout.write(f"outdir = {smac_outdir}\n")
    fout.write(f"instance_file = {smac_instance_file}\n")
    fout.write(f"test_instance_file = {smac_instance_file}\n")
    if use_features:
        fout.write(f"feature_file = {smac_feature_file}\n")
    fout.write("validation = true" + "\n")
    fout.close()

    sl.add_output(str(smac_file_scenario), "SMAC configuration scenario on the training set")
    sl.add_output(f"{sgh.smac_dir}{smac_outdir}",
                  "SMAC configuration output on the training set")

    return


def remove_configuration_directory(solver_name: str, smac_solver_dir: Path) -> None:
    """Remove the configuration directory."""
    # Delete directory and then create it new with necessary files
    shutil.rmtree(smac_solver_dir, ignore_errors=True)
    create_configuration_directory(smac_solver_dir, solver_name)

    return


def clean_configuration_directory(solver_name: str, instance_set_name: str) -> None:
    """Prepare clean configuration directory."""
    smac_solver_dir = Path(get_smac_solver_dir(solver_name, instance_set_name))

    remove_configuration_directory(solver_name, smac_solver_dir)
    create_configuration_directory(smac_solver_dir, solver_name)

    return


def get_smac_solver_dir(solver_name: str, instance_set_name: str) -> str:
    """Return the directory of a solver under the SMAC directory."""
    smac_scenario_dir = f"{sgh.smac_dir}/example_scenarios"
    smac_solver_dir = f"{smac_scenario_dir}/{solver_name}_{instance_set_name}/"

    return smac_solver_dir


def create_configuration_directory(smac_solver_dir: Path, solver_name: str):
    """Create a directory for the configuration of a solver+instance-set combination."""
    create_necessary_files_for_configured_solver(smac_solver_dir)

    # Copy PCS file to smac_solver_dir
    solver_diretory = f"Solvers/{solver_name}/"
    pcs_file = solver_diretory + get_pcs_file_from_solver_directory(solver_diretory)
    command_line = f"cp {pcs_file} {smac_solver_dir}"
    os.system(command_line)

    return


def create_necessary_files_for_configured_solver(smac_solver_dir: Path) -> None:
    """Create directories needed for configuration of a solver."""
    outdir_dir = smac_solver_dir / "outdir_train_configuration"
    command_line = "mkdir -p " + str(outdir_dir)
    os.system(command_line)

    tmp_dir = smac_solver_dir / "tmp"
    command_line = f"mkdir -p {tmp_dir}"
    os.system(command_line)

    return


def get_pcs_file_from_solver_directory(solver_directory: str) -> str:
    """Return the name of the PCS file in a solver directory.

    If not found, return an empty str.
    """
    list_files = os.listdir(solver_directory)

    for file_name in list_files:
        file_extension = sfh.get_file_full_extension(file_name)

        if file_extension == "pcs":
            return file_name

    return ""


def copy_solver_files_to_smac_dir(solver_name: str, instance_set_name: str) -> None:
    """Create and copy required directories and files for configuration with SMAC."""
    smac_solver_dir = Path(get_smac_solver_dir(solver_name, instance_set_name))
    _, _, _, _, num_of_smac_run, _ = get_smac_settings()

    for i in range(1, num_of_smac_run + 1):
        smac_solver_path_i = smac_solver_dir / str(i)
        # Create directories, -p makes sure any missing parents are also created
        cmd = f"mkdir -p {smac_solver_path_i}/tmp/"
        os.system(cmd)

        solver_diretory = Path("Solvers", solver_name, "*")
        cmd = f"cp -r {solver_diretory} {smac_solver_path_i}"
        os.system(cmd)

    return


def remove_validation_directories_execution_or_output(solver_name: str,
                                                      instance_set_train_name: str,
                                                      instance_set_test_name: str,
                                                      exec_or_out: str):
    """Remove execution or output directories for validation."""
    solver_dir = get_smac_solver_dir(solver_name, instance_set_train_name) + exec_or_out

    train_default_dir = Path(solver_dir + "_train_default/")
    sfh.rmtree(train_default_dir)

    if instance_set_test_name is not None:
        test_default_dir = Path(
            solver_dir + "_" + instance_set_test_name + "_test_default/")
        sfh.rmtree(test_default_dir)

        test_configured_dir = Path(
            solver_dir + "_" + instance_set_test_name + "_test_configured/")
        sfh.rmtree(test_configured_dir)

    return


def remove_validation_directories(solver_name: str, instance_set_train_name: str,
                                  instance_set_test_name: str):
    """Remove validation directories for a solver and instance set(s) combination."""
    remove_validation_directories_execution_or_output(
        solver_name, instance_set_train_name, instance_set_test_name, "validate")
    remove_validation_directories_execution_or_output(
        solver_name, instance_set_train_name, instance_set_test_name, "output")

    return


def prepare_smac_execution_directories_validation(solver_name: str,
                                                  instance_set_train_name: str,
                                                  instance_set_test_name: str):
    """Create and copy required directories and files for validation with SMAC.

    Remove old directories and files as needed.
    """
    # Make sure no old files remain that could interfere
    remove_validation_directories(solver_name, instance_set_train_name,
                                  instance_set_test_name)

    smac_solver_dir = get_smac_solver_dir(solver_name, instance_set_train_name)
    _, _, _, _, num_of_smac_run, _ = get_smac_settings()

    for i in range(1, num_of_smac_run + 1):
        solver_diretory = "Solvers/" + solver_name + "/*"

        # Train default
        execdir = "validate_train_default/"

        # Create directories, -p makes sure any missing parents are also created
        cmd = "mkdir -p " + smac_solver_dir + execdir + "/tmp/"
        os.system(cmd)
        # Copy solver to execution directory
        cmd = "cp -r " + solver_diretory + " " + smac_solver_dir + execdir
        os.system(cmd)

        # Test default
        if instance_set_test_name is not None:
            execdir = f"validate_{instance_set_test_name}_test_default/"

            # Create directories, -p makes sure any missing parents are also created
            cmd = "mkdir -p " + smac_solver_dir + execdir + "/tmp/"
            os.system(cmd)
            # Copy solver to execution directory
            cmd = "cp -r " + solver_diretory + " " + smac_solver_dir + execdir
            os.system(cmd)

            # Test configured
            execdir = "validate_{}_test_configured/".format(instance_set_test_name)

            # Create directories, -p makes sure any missing parents are also created
            cmd = "mkdir -p " + smac_solver_dir + execdir + "/tmp/"
            os.system(cmd)
            # Copy solver to execution directory
            cmd = "cp -r " + solver_diretory + " " + smac_solver_dir + execdir
            os.system(cmd)

    return


def create_smac_configure_sbatch_script(solver_name: str, instance_set_name: str) -> Path:
    """Generate a Slurm batch script for algorithm configuration with SMAC."""
    execdir = Path(".", "example_scenarios", f"{solver_name}_{instance_set_name}")
    smac_file_scenario_name = Path(f"{solver_name}_{instance_set_name}_scenario.txt")
    _, _, _, _, num_of_smac_run, num_of_smac_run_in_parallel = get_smac_settings()

    # Remove possible old results for this scenario
    result_part = Path("results", f"{solver_name}_{instance_set_name}")
    result_dir = sgh.smac_dir / result_part
    [item.unlink() for item in result_dir.glob("*") if item.is_file()]

    scenario_file = execdir / smac_file_scenario_name

    sbatch_script_path = Path(f"{smac_file_scenario_name}_{num_of_smac_run}_exp_sbatch.sh")

    generate_configuration_sbatch_script(sbatch_script_path, scenario_file, result_part,
                                         num_of_smac_run, num_of_smac_run_in_parallel,
                                         execdir)

    return sbatch_script_path


def generate_configuration_sbatch_script(sbatch_script_path: Path, scenario_file: Path,
                                         result_directory: Path, num_job_total: int,
                                         num_job_in_parallel: int, smac_execdir: Path):
    """Generate a Slurm batch script for algorithm configuration."""
    sbatch_options_list = ssh.get_slurm_sbatch_user_options_list()
    num_job_in_parallel = max(num_job_in_parallel, num_job_total)

    output_log_path = Path(sgh.smac_dir, "tmp", f"{sbatch_script_path}.txt")
    error_log_path = Path(sgh.smac_dir, "tmp", f"{sbatch_script_path}.err")

    # Remove possible old output
    output_log_path.unlink(missing_ok=True)
    error_log_path.unlink(missing_ok=True)

    # Log output paths
    sl.add_output(str(output_log_path),
                  "Output log of batch script for parallel configuration runs with SMAC")
    sl.add_output(str(error_log_path),
                  "Error log of batch script for parallel configuration runs with SMAC")

    (sgh.smac_dir / result_directory).mkdir(parents=True, exist_ok=True)
    Path(sgh.smac_dir, "tmp").mkdir(parents=True, exist_ok=True)

    fout = open(f"{sgh.smac_dir}{sbatch_script_path}", "w+")
    fout.write("#!/bin/bash\n")
    fout.write("###\n")
    fout.write(f"#SBATCH --job-name={sbatch_script_path}\n")
    fout.write(f"#SBATCH --output=tmp/{sbatch_script_path}.txt\n")
    fout.write(f"#SBATCH --error=tmp/{sbatch_script_path}.err\n")
    fout.write("###\n")
    fout.write("###\n")
    fout.write("#SBATCH --mem-per-cpu=3000\n")
    fout.write(f"#SBATCH --array=0-{num_job_total}%{num_job_in_parallel}\n")
    fout.write("###\n")
    # Options from the slurm/sbatch settings file
    for i in sbatch_options_list:
        fout.write(f"#SBATCH {i}\n")
    fout.write("###\n")

    fout.write("params=( \\\n")

    sl.add_output(
        f"{sgh.smac_dir}{result_directory}{sbatch_script_path}_seed_N_smac.txt",
        f"Configuration log for SMAC run 1 < N <= {num_job_total}")

    for i in range(0, num_job_total):
        seed = i + 1
        result_path = f"{result_directory}{sbatch_script_path}_seed_{seed}_smac.txt"
        smac_execdir_i = smac_execdir / str(seed)
        sl.add_output(sgh.smac_dir + result_path, 
                      f"Configuration log for SMAC run {num_job_total}")

        fout.write(f"'{scenario_file} {seed} {result_path} {smac_execdir_i}' \\\n")

    fout.write(")\n")

    cmd_srun_prefix = "srun -N1 -n1 "
    cmd_srun_prefix += ssh.get_slurm_srun_user_options_str()
    cmd_smac_prefix = "./each_smac_run_core.sh "

    cmd = f"{cmd_srun_prefix} {cmd_smac_prefix} " + "${params[$SLURM_ARRAY_TASK_ID]}"
    fout.write(cmd + "\n")
    fout.close()

    return


def submit_smac_configure_sbatch_script(smac_configure_sbatch_script_name: str) -> str:
    """Submit a Slurm batch script for algorithm configuration with SMAC."""
    ori_path = Path.cwd()
    command_line = (f"cd {sgh.smac_dir} ; sbatch {smac_configure_sbatch_script_name} ; "
                    f"cd {ori_path}")

    output_list = os.popen(command_line).readlines()

    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(jobid, CommandName.CONFIGURE_SOLVER)
    else:
        jobid = ""

    return jobid


def check_configuration_exists(solver_name: str, instance_set_name: str) -> bool:
    """Check the results directory for this solver and instance set combination exists.

    NOTE: This function assumes SMAC output.
    """
    # Check the results directory exists
    smac_results_dir = Path(
        sgh.smac_dir + "/results/" + solver_name + "_" + instance_set_name + "/")

    all_good = smac_results_dir.is_dir()

    if not all_good:
        print("ERROR: No configuration results found for the given solver and training "
              "instance set.")
        sys.exit(-1)

    return all_good


def check_instance_list_file_exist(solver_name: str, instance_set_name: str) -> None:
    """Check the instance list file exists."""
    file_name = Path(instance_set_name + "_train.txt")
    instance_list_file_path = Path(PurePath(Path(sgh.smac_dir)
                                   / Path("example_scenarios")
                                   / Path(solver_name + "_" + instance_set_name)
                                   / file_name))

    all_good = instance_list_file_path.is_file()

    if not all_good:
        print("ERROR: Instance list file not found, make sure configuration was "
              "completed correctly for this solver and instance set combination.")
        sys.exit(-1)

    return


def check_configuration_permission_error(solver_name: str, instance_set_name: str):
    """Check the files for solver permission errors."""
    smac_results_dir = Path(f"{sgh.smac_dir}/results/{solver_name}_{instance_set_name}/")

    # Get the name of the first file in the directory
    # If there is an error, it will be in all files, so checking one is sufficient
    filename = next(Path(smac_results_dir / f) for f in os.listdir(smac_results_dir)
                    if Path(smac_results_dir / f).is_file())

    with open(filename, "r") as file:
        content = file.read()
        if "exec failed: Permission denied" in content:
            print("ERROR: The solver configuration was not succesfull so the validation "
                  "could not be completed. This is due to missing execution permissions "
                  "for the solver executable.")
            sys.exit(-1)

    print(file)


def check_validation_prerequisites(solver_name: str, instance_set_name: str) -> None:
    """Validate prerequisites for validation are available."""
    check_configuration_exists(solver_name, instance_set_name)
    check_instance_list_file_exist(solver_name, instance_set_name)
    check_configuration_permission_error(solver_name, instance_set_name)

    return


# Write optimised configuration string to file
def write_optimised_configuration_str(solver_name, instance_set_name) -> None:
    """Write the latest optimised configuration parameter str to file."""
    optimised_configuration_str, _, _ = get_optimised_configuration(
        solver_name, instance_set_name)
    latest_configuration_str_path = sgh.sparkle_tmp_path + "latest_configuration.txt"

    with open(latest_configuration_str_path, "w") as outfile:
        outfile.write(optimised_configuration_str)
    # Log output
    sl.add_output(latest_configuration_str_path, "Configured algorithm parameters of the"
                  " most recent configuration process")

    return


def write_optimised_configuration_pcs(solver_name, instance_set_name) -> None:
    """Write optimised configuration to a new PCS file."""
    # Read optimised configuration and convert to dict
    optimised_configuration_str, _, _ = get_optimised_configuration(
        solver_name, instance_set_name)
    optimised_configuration_str += " -arena '12345'"
    optimised_configuration_list = optimised_configuration_str.split()

    # Create dictionary
    config_dict = {}
    for i in range(0, len(optimised_configuration_list), 2):
        # Remove dashes and spaces from parameter names, and remove quotes and
        # spaces from parameter values before adding them to the dict
        config_dict[optimised_configuration_list[i].strip(" -")] = (
            optimised_configuration_list[i + 1].strip(" '"))

    # Read existing PCS file and create output content
    solver_diretory = "Solvers/" + solver_name
    pcs_file = solver_diretory + "/" + get_pcs_file_from_solver_directory(
        solver_diretory)
    pcs_file_out = []

    with open(pcs_file) as infile:
        for line in infile:
            # Copy empty lines
            if not line.strip():
                line_out = line
            # Don't mess with conditional (containing '|') and forbidden (starting
            # with '{') parameter clauses, copy them as is
            elif "|" in line or line.startswith("{"):
                line_out = line
            # Also copy parameters that do not appear in the optimised list
            # (if the first word in the line does not match one of the parameter names
            # in the dict)
            elif line.split()[0] not in config_dict:
                line_out = line
            # Modify default values with optimised values
            else:
                words = line.split("[")
                if len(words) == 2:
                    # Second element is default value + possible tail
                    param_name = line.split()[0]
                    param_val = config_dict[param_name]
                    tail = words[1].split("]")[1]
                    line_out = words[0] + "[" + param_val + "]" + tail
                elif len(words) == 3:
                    # Third element is default value + possible tail
                    param_name = line.split()[0]
                    param_val = config_dict[param_name]
                    tail = words[2].split("]")[1]
                    line_out = words[0] + words[1] + "[" + param_val + "]" + tail
                else:
                    # This does not seem to be a line with a parameter definition, copy
                    # as is
                    line_out = line
            pcs_file_out.append(line_out)

    latest_configuration_pcs_path = sgh.sparkle_tmp_path + "latest_configuration.pcs"

    with open(latest_configuration_pcs_path, "w") as outfile:
        for element in pcs_file_out:
            outfile.write(str(element))
    # Log output
    sl.add_output(latest_configuration_pcs_path, "PCS file with configured algorithm "
                  "parameters of the most recent configuration process as default "
                  "values")

    return


def check_optimised_configuration_params(params: str) -> None:
    """Check if a given configuration parameter str appears to be valid."""
    # Check if a valid configuration was found
    if params == "":
        print(f"ERROR: Invalid optimised_configuration_str: {params}; "
              "Stopping execution!")
        sys.exit(-1)

    return


def check_optimised_configuration_performance(performance: str) -> None:
    """Check if a given configuration performance str appears to be valid."""
    # Check if a valid seed was found
    if performance == -1:
        print("ERROR: Invalid optimised_configuration_performance; Stopping execution!")
        sys.exit(-1)

    return


def check_optimised_configuration_seed(seed: str) -> None:
    """Check if a given configuration seed str appears to be valid."""
    # Check if a valid seed was found
    if seed == -1:
        print("ERROR: Invalid optimised_configuration_seed; Stopping execution!")
        sys.exit(-1)

    return


def get_optimised_configuration_params(solver_name: str, instance_set_name: str) -> str:
    """Return the optimised configuration parameter str."""
    optimised_configuration_str, _, _ = get_optimised_configuration_from_file(
        solver_name, instance_set_name)
    check_optimised_configuration_params(optimised_configuration_str)

    return optimised_configuration_str


def get_optimised_configuration_from_file(solver_name: str, instance_set_name: str
                                          ) -> tuple[str, str, str]:
    """Read the optimised configuration, its performance, and seed from file."""
    optimised_configuration_str = ""
    optimised_configuration_performance = -1
    optimised_configuration_seed = -1

    smac_results_dir = f"{sgh.smac_dir}/results/{solver_name}_{instance_set_name}/"
    list_file_result_name = os.listdir(smac_results_dir)

    key_str_1 = "Estimated mean quality of final incumbent config"

    # Compare results of each run on the training set to find the best configuration
    # among them
    for file_result_name in list_file_result_name:
        file_result_path = smac_results_dir + file_result_name
        fin = open(file_result_path, "r+")

        while True:
            myline = fin.readline()
            if not myline:
                break
            myline = myline.strip()

            if myline.find(key_str_1) == 0:
                mylist = myline.split()
                # Skip 14 words leading up to the performance value
                this_configuration_performance = float(mylist[14][:-1])

                if (optimised_configuration_performance < 0
                   or this_configuration_performance
                   < optimised_configuration_performance):
                    optimised_configuration_performance = this_configuration_performance

                    # Skip the line before the line with the optimised configuration
                    myline_2 = fin.readline()
                    myline_2 = fin.readline()
                    # If this is a single file instance:
                    if not sih.check_existence_of_reference_instance_list(
                            instance_set_name):
                        mylist_2 = myline_2.strip().split()
                        # Skip 8 words before the configured parameters
                        start_index = 8
                    # Otherwise, for multi-file instances:
                    else:
                        # Skip everything before the last double quote "
                        mylist_2 = myline_2.strip().split('"')
                        last_idx = len(mylist_2) - 1
                        mylist_2 = mylist_2[last_idx].strip().split()
                        # Then skip another 4 words before the configured parameters
                        start_index = 4
                    end_index = len(mylist_2)
                    optimised_configuration_str = ""
                    for i in range(start_index, end_index):
                        optimised_configuration_str += " " + mylist_2[i]

                    # Get seed used to call smac
                    myline_3 = fin.readline()
                    mylist_3 = myline_3.strip().split()
                    optimised_configuration_seed = mylist_3[4]

        fin.close()

    return (optimised_configuration_str, optimised_configuration_performance,
            optimised_configuration_seed)


def get_optimised_configuration(solver_name: str,
                                instance_set_name: str) -> tuple[str, str, str]:
    """Return the optimised configuration str, its performance, and its seed."""
    (optimised_configuration_str, optimised_configuration_performance,
     optimised_configuration_seed) = get_optimised_configuration_from_file(
        solver_name, instance_set_name)
    check_optimised_configuration_params(optimised_configuration_str)
    check_optimised_configuration_performance(optimised_configuration_performance)
    check_optimised_configuration_seed(optimised_configuration_seed)

    return (optimised_configuration_str, optimised_configuration_performance,
            optimised_configuration_seed)


def generate_validation_callback_slurm_script(solver: str, instance_set_train: str,
                                              instance_set_test: str,
                                              dependency: str) -> str:
    """Generate a callback Slurm batch script for validation."""
    command_line = "echo $(pwd) $(date)\n"
    command_line += ("srun -N1 -n1 ./Commands/validate_configured_vs_default.py "
                     "--settings-file Settings/latest.ini")
    command_line += f" --solver {solver}"
    command_line += f" --instance-set-train {instance_set_train}"
    if instance_set_test is not None:
        command_line += f" --instance-set-test {instance_set_test}"

    jobid = generate_generic_callback_slurm_script(
        "validation", solver, instance_set_train, instance_set_test, dependency,
        command_line, CommandName.VALIDATE_CONFIGURED_VS_DEFAULT)

    return jobid


def generate_ablation_callback_slurm_script(solver: str, instance_set_train: str,
                                            instance_set_test: str,
                                            dependency: str) -> str:
    """Generate a callback Slurm batch script for ablation."""
    command_line = "echo $(pwd) $(date)\n"
    command_line += ("srun -N1 -n1 ./Commands/run_ablation.py --settings-file "
                     "Settings/latest.ini")
    command_line += f" --solver {solver}"
    command_line += f" --instance-set-train {instance_set_train}"

    if instance_set_test is not None:
        command_line += f" --instance-set-test {instance_set_test}"

    jobid = generate_generic_callback_slurm_script(
        "ablation", solver, instance_set_train, instance_set_test, dependency,
        command_line, CommandName.RUN_ABLATION)

    return jobid


def generate_generic_callback_slurm_script(name: str, solver: str,
                                           instance_set_train: str,
                                           instance_set_test: str, dependency: str,
                                           command_line: str,
                                           command_name: CommandName) -> str:
    """Generate a callback Slurm batch script."""
    solver_name = sfh.get_last_level_directory_name(solver)
    instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
    instance_set_test_name = None

    if instance_set_test is not None:
        instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)

    delayed_job_file_name = f"delayed_{name}_{solver_name}_{instance_set_train_name}"

    if instance_set_test is not None:
        delayed_job_file_name += f"_{instance_set_test_name}"

    delayed_job_file_name += "_script.sh"

    sparkle_tmp_path = Path(sgh.sparkle_tmp_path)
    sparkle_tmp_path.mkdir(parents=True, exist_ok=True)
    delayed_job_file_path = sparkle_tmp_path / delayed_job_file_name
    delayed_job_output = f"{delayed_job_file_path}.txt"
    delayed_job_error = f"{delayed_job_file_path}.err"

    job_name = f"--job-name={delayed_job_file_name}"
    output = f"--output={delayed_job_output}"
    error = f"--error={delayed_job_error}"

    sl.add_output(delayed_job_file_path, f"Delayed {name} script")
    sl.add_output(delayed_job_output, f"Delayed {name} standard output")
    sl.add_output(delayed_job_error, f"Delayed {name} error output")

    sbatch_options_list = [job_name, output, error]
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    # Only overwrite task specific arguments
    sbatch_options_list.append(f"--dependency=afterany:{dependency}")
    sbatch_options_list.append("--nodes=1")
    sbatch_options_list.append("--ntasks=1")
    sbatch_options_list.append("-c1")
    sbatch_options_list.append("--mem-per-cpu=3000")

    fout = open(delayed_job_file_path, "w")
    fout.write("#!/bin/bash\n")  # Use bash to execute this script
    fout.write("###\n")
    fout.write("###\n")

    for sbatch_option in sbatch_options_list:
        fout.write(f"#SBATCH {sbatch_option}\n")

    fout.write("###\n")
    fout.write(f"{command_line}\n")
    fout.close()

    os.popen(f"chmod 755 {delayed_job_file_path}")

    output_list = os.popen(f"sbatch ./{delayed_job_file_path}").readlines()

    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(jobid, command_name)
    else:
        jobid = ""

    print(f"Callback script to launch {name} is placed at {delayed_job_file_path}")
    print(f"Once configuration is finished, {name} will automatically start as a Slurm "
          f"job: {jobid}")

    return jobid
