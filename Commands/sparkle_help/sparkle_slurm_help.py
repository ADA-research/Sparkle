#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for interaction with Slurm."""

from __future__ import annotations

import os
import fcntl
import shlex
import subprocess
import sys
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_configure_solver_help as scsh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help import sparkle_job_help as sjh

from runrunner.base import Runner
import runrunner as rrr

def get_slurm_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with the Slurm options given in the Slurm settings file.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    if path_modifier is None:
        path_modifier = ""

    slurm_options_list = []

    sparkle_slurm_settings_path = str(path_modifier) + sgh.sparkle_slurm_settings_path

    settings_file = Path(sparkle_slurm_settings_path).open("r")
    while True:
        current_line = settings_file.readline()
        if not current_line:
            break
        if current_line[0] == "-":
            current_line = current_line.strip()
            slurm_options_list.append(current_line)
    settings_file.close()

    return slurm_options_list


def get_slurm_sbatch_user_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with Slurm batch options given by the user.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    return get_slurm_options_list(path_modifier)


def get_slurm_sbatch_default_options_list() -> list[str]:
    """Return the default list of Slurm batch options.

    Returns:
      List of strings. Currently, this is the empty list.
    """
    return list()


def get_slurm_srun_user_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with the Slurm run options given by the user.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    return get_slurm_options_list(path_modifier)


def get_slurm_srun_user_options_str(path_modifier: str = None) -> str:
    """Return a single string with the Slurm run option given by the user.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      A single string of Slurm options.
    """
    srun_options_list = get_slurm_srun_user_options_list(path_modifier)
    srun_options_str = ""

    for i in srun_options_list:
        srun_options_str += i + " "

    return srun_options_str


def check_slurm_option_compatibility(srun_option_string: str) -> tuple[bool, str]:
    """Check if the given srun_option_string is compatible with the Slurm cluster.

    Args:
      srun_option_string: Specific run option string.

    Returns:
      A 2-tuple of type (combatible, message). The first entry is a Boolean
      incidating the compatibility and the second is a additional informative
      string message.
    """
    args = shlex.split(srun_option_string)
    kwargs = {}

    for i in range(len(args)):
        arg = args[i]
        if "=" in arg:
            splitted = arg.split("=")
            kwargs[splitted[0]] = splitted[1]
        elif i < len(args) and "-" not in args[i + 1]:
            kwargs[arg] = args[i + 1]

    if not ("--partition" in kwargs.keys() or "-p" in kwargs.keys()):
        print("###Could not check slurm compatibility because no partition was "
              "specified; continuing###")
        return True, "Could not Check"

    partition = kwargs.get("--partition", kwargs.get("-p", None))

    output = str(subprocess.check_output(["sinfo", "--nohead", "--format", '"%c;%m"',
                                          "--partition", partition]))
    # we expect a string of the form b'"{};{}"\n'
    cpus, memory = output[3:-4].split(";")
    cpus = int(cpus)
    memory = float(memory)

    if "--cpus-per-task" in kwargs.keys() or "-c" in kwargs.keys():
        requested_cpus = int(kwargs.get("--cpus-per-task", kwargs.get("-c", 0)))
        if requested_cpus > cpus:
            return False, f"ERROR: CPU specification of {requested_cpus} cannot be " \
                          f"satisfied for {partition}, only got {cpus}"

    if "--mem-per-cpu" in kwargs.keys() or "-m" in kwargs.keys():
        requested_memory = float(kwargs.get("--mem-per-cpu", kwargs.get("-m", 0))) * \
            int(kwargs.get("--cpus-per-task", kwargs.get("-c", cpus)))
        if requested_memory > memory:
            return False, f"ERROR: Memory specification {requested_memory}MB can " \
                          f"not be satisfied for {partition}, only got {memory}MB"

    return True, "Check successful"


def generate_sbatch_script_generic(sbatch_script_path: str,
                                   sbatch_options_list: list[str],
                                   job_params_list: list[str],
                                   srun_options_str: str,
                                   target_call_str: str,
                                   job_output_list: list[str] = None) -> None:
    """Generate the generic components of a Slurm batch script.

    Args:
      sbatch_script_path: Path to batch script.
      sbatch_options_list: List of Slurm options for batch script execution.
      job_params_list: List of job parameters.
      srun_options_str: A string with run options.
      target_call_str: The target call string.
      job_output_list: Optional list of job outputs that should be appended to
        the job output. Default is None.
    """
    fout = Path(sbatch_script_path).open("w+")  # open the file of sbatch script

    # using the UNIX file lock to prevent other attempts to visit this sbatch script
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)

    # specify the options of sbatch in the top of this sbatch script
    fout.write("#!/bin/bash\n")
    fout.write("###\n")
    fout.write("###\n")

    for i in sbatch_options_list:
        fout.write("#SBATCH " + str(i) + "\n")

    fout.write("###\n")

    # specify the array of parameters for each command
    if len(job_params_list) > 0:
        fout.write("params=( \\" + "\n")

        for i in range(0, len(job_params_list)):
            fout.write(f"'{job_params_list[i]}' \\\n")

        fout.write(")" + "\n")

    # if there is a list of output file paths, write the output parameter
    if job_output_list is not None:
        fout.write("output=( \\" + "\n")

        for i in range(0, len(job_output_list)):
            fout.write(f"'{job_output_list[i]}' \\\n")

        fout.write(")" + "\n")

    # specify the prefix of the executing command
    command_prefix = "srun " + srun_options_str + " " + target_call_str
    # specify the complete command
    command_line = command_prefix
    if len(job_params_list) > 0:
        command_line += " " + "${params[$SLURM_ARRAY_TASK_ID]}"

    # add output file paths to the command if given
    if job_output_list is not None:
        command_line += " > ${output[$SLURM_ARRAY_TASK_ID]}"

    # write the complete command in this sbatch script
    fout.write(command_line + "\n")
    fout.close()  # close the file of the sbatch script


def get_sbatch_options_list(sbatch_script_path: Path,
                            num_jobs: int,
                            job: str,
                            smac: bool = True) -> list[str]:
    """Return and write output paths for a list of standardised Slurm batch options.

    Args:
      sbatch_script_path: Path object representing the batch script.
      num_jobs: The number of jobs.
      job: The job identifier.
      smac: A Boolean indicating whether SMAC should be used. Default is True.

    Returns:
      A list of batch options for Slurm.
    """
    if smac:
        tmp_dir = sgh.smac_dir + "tmp/"
    else:
        tmp_dir = "Tmp/"

    sbatch_script_name = sfh.get_file_name(str(sbatch_script_path))

    # Set sbatch options
    max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
    if num_jobs < max_jobs:
        max_jobs = num_jobs
    std_out = f"{tmp_dir}{sbatch_script_name}.txt"
    std_err = f"{tmp_dir}{sbatch_script_name}.err"
    job_name = f"--job-name={sbatch_script_name}"
    output = f"--output={std_out}"
    error = f"--error={std_err}"
    array = f"--array=0-{str(num_jobs - 1)}%{str(max_jobs)}"
    sbatch_options_list = [job_name, output, error, array]

    # Log script and output paths
    sl.add_output(str(sbatch_script_path), f"Slurm batch script for {job}")
    sl.add_output(std_out,
                  f"Standard output of Slurm batch script for {job}")
    sl.add_output(std_err,
                  f"Error output of Slurm batch script for {job}")

    # Remove possible old output
    sfh.rmfile(Path(std_out))
    sfh.rmfile(Path(std_err))

    return sbatch_options_list


def generate_sbatch_script_for_validation(solver_name: str,
                                          instance_set_train_name: str,
                                          instance_set_test_name: str = None) -> str:
    """Generate a Slurm batch script for algorithm configuration validation.

    Args:
      solver_name: Name of the solver.
      instance_set_train_name: The name of the instance set for training.
      instance_set_test_name: Optional name of the instance set for testing.

    Returns:
      Path to the generated Slurm batch script file.
    """
    # Set script name and path
    if instance_set_test_name is not None:
        sbatch_script_name = (f"{solver_name}_{instance_set_train_name}_"
                              f"{instance_set_test_name}_validation_sbatch.sh")
    else:
        sbatch_script_name = (f"{solver_name}_{instance_set_train_name}_validation_"
                              "sbatch.sh")

    sbatch_script_path = sgh.smac_dir + sbatch_script_name

    # Get sbatch options
    num_jobs = 3
    job = "validation"
    sbatch_options_list = get_sbatch_options_list(Path(sbatch_script_path), num_jobs,
                                                  job)

    scenario_dir = "example_scenarios/" + solver_name + "_" + instance_set_train_name

    # Train default
    default = True
    scenario_file_name = scsh.create_file_scenario_validate(
        solver_name, instance_set_train_name, instance_set_train_name,
        scsh.InstanceType.TRAIN, default)
    scenario_file_path = scenario_dir + "/" + scenario_file_name
    exec_dir = scenario_dir + "/validate_train_default/"
    configuration_str = "DEFAULT"
    train_default_out = "results/" + solver_name + "_validation_" + scenario_file_name

    train_default = (f"--scenario-file {scenario_file_path} --execdir {exec_dir}"
                     f" --configuration {configuration_str}")

    # Create job list
    job_params_list = [train_default]
    job_output_list = [train_default_out]

    # If given, also validate on the test set
    if instance_set_test_name is not None:
        # Test default
        default = True
        scenario_file_name = scsh.create_file_scenario_validate(
            solver_name, instance_set_train_name, instance_set_test_name,
            scsh.InstanceType.TEST, default)
        scenario_file_path = scenario_dir + "/" + scenario_file_name
        exec_dir = f"{scenario_dir}/validate_{instance_set_test_name}_test_default/"
        configuration_str = "DEFAULT"
        test_default_out = "results/" + solver_name + "_validation_" + scenario_file_name

        test_default = (f"--scenario-file {scenario_file_path} --execdir {exec_dir}"
                        f" --configuration {configuration_str}")

        # Test configured
        default = False
        scenario_file_name = scsh.create_file_scenario_validate(
            solver_name, instance_set_train_name, instance_set_test_name,
            scsh.InstanceType.TEST, default)
        scenario_file_path = scenario_dir + "/" + scenario_file_name
        optimised_configuration_str, _, _ = scsh.get_optimised_configuration(
            solver_name, instance_set_train_name)
        exec_dir = f"{scenario_dir}/validate_{instance_set_test_name}_test_configured/"
        configuration_str = '"' + str(optimised_configuration_str) + '"'

        # Write configuration to file to be used by smac-validate
        config_file_path = scenario_dir + "/configuration_for_validation.txt"
        # open the file of sbatch script
        fout = Path(sgh.smac_dir + config_file_path).open("w+")
        # using the UNIX file lock to prevent other attempts to visit this sbatch script
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        fout.write(optimised_configuration_str + "\n")

        test_configured_out = f"results/{solver_name}_validation_{scenario_file_name}"

        test_configured = (f"--scenario-file {scenario_file_path} --execdir {exec_dir}"
                           f" --configuration-list {config_file_path}")

        # Extend job list
        job_params_list.extend([test_default, test_configured])
        job_output_list.extend([test_default_out, test_configured_out])

    # Number of cores available on a CPU of this cluster
    n_cpus = sgh.settings.get_slurm_clis_per_node()

    # Adjust maximum number of cores to be the maximum of the instances we validate on
    instance_sizes = []
    # Get instance set sizes
    for instance_set_name, inst_type in [(instance_set_train_name, "train"),
                                         (instance_set_test_name, "test")]:
        if instance_set_name is not None:
            smac_instance_file = (f"{sgh.smac_dir}{scenario_dir}/{instance_set_name}_"
                                  f"{inst_type}.txt")
            if Path(smac_instance_file).is_file():
                instance_count = sum(1 for _ in open(smac_instance_file, "r"))
                instance_sizes.append(instance_count)

    # Adjust cpus when nessacery
    if len(instance_sizes) > 0:
        max_instance_count = (max(*instance_sizes) if len(instance_sizes) > 1
                              else instance_sizes[0])
        n_cpus = min(n_cpus, max_instance_count)

    # Extend sbatch options
    cpus = "--cpus-per-task=" + str(n_cpus)
    sbatch_options_list.append(cpus)
    sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(get_slurm_sbatch_user_options_list())

    # Set srun options
    srun_options_str = "--nodes=1 --ntasks=1 --cpus-per-task " + str(n_cpus)
    srun_options_str = srun_options_str + " " + get_slurm_srun_user_options_str()

    result, msg = check_slurm_option_compatibility(srun_options_str)

    if not result:
        print(f"Slurm config Error: {msg}")
        sys.exit()

    # Create target call
    target_call_str = ("./smac-validate --use-scenario-outdir true --num-run 1 "
                       f"--cli-cores {str(n_cpus)}")

    # Remove possible old results
    for result_output_file in job_output_list:
        sfh.rmfile(Path(result_output_file))

    # Generate script
    generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                   job_params_list, srun_options_str, target_call_str,
                                   job_output_list)

    return sbatch_script_name


def generate_sbatch_script_for_feature_computation(
        n_jobs: int,
        feature_data_csv_path: str,
        list_jobs: list[str]) -> tuple[str, str]:
    """Generate a Slurm batch script for feature computation.

    Args:
      n_jobs: The number of jobs.
      feature_data_csv_path: Path to the feature data in CSV format.
      list_jobs: List of job IDs.

    Returns:
      A 2-tuple: Name of the generated Slurm batch script file and the full path
      to this file.
    """
    # Set script name and path
    sbatch_script_name = (f"computing_features_sbatch_shell_script_{str(n_jobs)}_"
                          f"{sbh.get_time_pid_random_string()}.sh")
    sbatch_script_dir = sgh.sparkle_tmp_path
    sbatch_script_path = sbatch_script_dir + sbatch_script_name

    # Set sbatch options
    max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
    num_jobs = n_jobs
    if num_jobs < max_jobs:
        max_jobs = num_jobs
    job_name = "--job-name=" + sbatch_script_name
    output = "--output=" + sbatch_script_path + ".txt"
    error = "--error=" + sbatch_script_path + ".err"
    array = "--array=0-" + str(num_jobs - 1) + "%" + str(max_jobs)

    sbatch_options_list = [job_name, output, error, array]
    sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(get_slurm_sbatch_user_options_list())

    # Create job list
    job_params_list = []

    for i in range(0, num_jobs):
        instance_path = list_jobs[i][0]
        extractor_path = list_jobs[i][1]
        job_params = (f"--instance {instance_path} --extractor {extractor_path} "
                      f"--feature-csv {feature_data_csv_path}")
        job_params_list.append(job_params)

    # Set srun options
    srun_options_str = "-N1 -n1"
    srun_options_str = srun_options_str + " " + get_slurm_srun_user_options_str()

    # Create target call
    target_call_str = "Commands/sparkle_help/compute_features_core.py"

    # Generate script
    generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                   job_params_list, srun_options_str, target_call_str)

    return sbatch_script_name, sbatch_script_dir


def submit_sbatch_script(sbatch_script_name: str,
                         command_name: CommandName,
                         execution_dir: str | None = None) -> str:
    """Submit a Slurm batch script.

    Args:
      sbatch_script_name: Name of the batch script.
      command_name: Command name.
      execution_dir: Optionallly the directory from which the batch script is
        to be executed.

    Returns:
      String job identifier or empty string if the job was not submitted
      successfully. Defaults to the SMAC directory.
    """
    if execution_dir is None:
        execution_dir = sgh.smac_dir

    sbatch_script_path = sbatch_script_name
    ori_path = Path.cwd()
    os.system(f"cd {execution_dir} ; chmod a+x {sbatch_script_path} ; cd {ori_path}")
    # unset fix https://bugs.schedmd.com/show_bug.cgi?id=14298
    command = f"cd {execution_dir} ; unset SLURM_CPU_BIND;" \
              f"sbatch {sbatch_script_path} ; cd {ori_path}"

    output_list = os.popen(command).readlines()

    jobid = ""
    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(jobid, command_name)

    return jobid


def generate_validation_callback_script(solver: Path,
                                              instance_set_train: Path,
                                              instance_set_test: Path,
                                              dependency: str,
                                              run_on: Runner = Runner.SLURM) -> str:
    """Generate a callback Slurm batch script for validation.

    Args:
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      dependency: String of job dependencies.

    Returns:
      String job identifier.
    """
    command_line = "echo $(pwd) $(date)\n"
    command_line += "srun -N1 -n1 " if run_on == Runner.SLURM else ""
    command_line += ("./Commands/validate_configured_vs_default.py "
                     "--settings-file Settings/latest.ini")
    command_line += f" --solver {solver}"
    command_line += f" --instance-set-train {instance_set_train}"
    command_line += f" --run_on {run_on}"
    if instance_set_test is not None:
        command_line += f" --instance-set-test {instance_set_test}"
    
    if run_on == Runner.SLURM:
        jobid = generate_generic_callback_slurm_script(
            "validation", solver, instance_set_train, instance_set_test, dependency,
            command_line, CommandName.VALIDATE_CONFIGURED_VS_DEFAULT)
    else:
        jobid = generate_generic_callback_local_script(
            "validation", solver, instance_set_train, instance_set_test, dependency,
            command_line, CommandName.VALIDATE_CONFIGURED_VS_DEFAULT)

    return jobid


def generate_ablation_callback_slurm_script(solver: Path,
                                            instance_set_train: Path,
                                            instance_set_test: Path,
                                            dependency: str,
                                            run_on: Runner = Runner.SLURM) -> str:
    """Generate a callback Slurm batch script for ablation.

    Args:
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      dependency: String of job dependencies.

    Returns:
      String job identifier.
    """
    command_line = "echo $(pwd) $(date)\n"
    command_line += "srun -N1 -n1 " if run_on == Runner.SLURM else ""
    command_line += "./Commands/run_ablation.py --settings-file Settings/latest.ini" 
    command_line += f" --solver {solver}"
    command_line += f" --instance-set-train {instance_set_train}"
    command_line += f" --run_on {run_on}"

    if instance_set_test is not None:
        command_line += f" --instance-set-test {instance_set_test}"

    jobid = generate_generic_callback_slurm_script(
        "ablation", solver, instance_set_train, instance_set_test,
        dependency, command_line, CommandName.RUN_ABLATION)

    return jobid


def create_generic_callback_options_list(name: str,
                                         solver: Path,
                                         instance_set_train: Path,
                                         instance_set_test: Path) -> (str, list):
    """Create the options for the callback script
    
    Args:
      name: Name of the script (used as prefix for the file name).
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      
    Returns:
      str: The delayed job file path
      list: List of strings containing the job options"""
    delayed_job_file_name = f"delayed_{name}_{solver.name}_{instance_set_train.name}"

    if instance_set_test is not None:
        delayed_job_file_name += f"_{instance_set_test.name}"

    delayed_job_file_name += "_script.sh"

    sparkle_tmp_path = Path(sgh.sparkle_tmp_path)
    sparkle_tmp_path.mkdir(parents=True, exist_ok=True)
    delayed_job_file_path = sparkle_tmp_path / delayed_job_file_name
    delayed_job_output = f"{delayed_job_file_path}.txt"
    delayed_job_error = f"{delayed_job_file_path}.err"

    job_name = f"--job-name={delayed_job_file_name}"
    output = f"--output={delayed_job_output}"
    error = f"--error={delayed_job_error}"

    sl.add_output(str(delayed_job_file_path), f"Delayed {name} script")
    sl.add_output(delayed_job_output, f"Delayed {name} standard output")
    sl.add_output(delayed_job_error, f"Delayed {name} error output")

    return delayed_job_file_path, [job_name, output, error]


def generate_generic_callback_local_script(name: str,
                                           solver: Path,
                                           instance_set_train: Path,
                                           instance_set_test: Path,
                                           dependency: str,
                                           command_line: str,
                                           command_name: CommandName,
                                           run_on: Runner = Runner.LOCAL) -> str:
    """Generate a generic callback script to be executed locally

    TODO: Currently does not use the first four parameters (Original slurm).
          How should these be used? Were made(?) for creating .sh name

    Args:
      name: Name of the script (used as prefix for the file name).
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      dependency: String of job dependencies.
      command_line: String representation of the actual command line
        that is to be executed.
      command_name: Command name for job that shall be exectuted if the
        job was successfully submitted to the batch system.

    Returns:
      String job identifier.
    """
    sparkle_tmp_path = Path(sgh.sparkle_tmp_path)

    run = rrr.add_to_queue(runner=run_on,
                           cmd=command_line,
                           name=command_name,
                           dependencies=dependency,
                           base_dir=sparkle_tmp_path)

    return run.run_id


def generate_generic_callback_slurm_script(name: str,
                                           solver: Path,
                                           instance_set_train: Path,
                                           instance_set_test: Path,
                                           dependency: str,
                                           command_line: str,
                                           command_name: CommandName) -> str:
    """Generate a generic callback Slurm batch script.

    Args:
      name: Name of the script (used as prefix for the file name).
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      dependency: String of job dependencies.
      command_line: String representation of the actual command line
        that is to be executed.
      command_name: Command name for job that shall be exectuted if the
        job was successfully submitted to the batch system.

    Returns:
      String job identifier.
    """
    delayed_job_file_path, sbatch_options_list =\
      create_generic_callback_options_list(name=name,
                                           solver=solver,
                                           instance_set_train=instance_set_train,
                                           instance_set_test=instance_set_test)
    sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(get_slurm_sbatch_user_options_list())

    # Only overwrite task specific arguments
    sbatch_options_list.append(f"--dependency=afterany:{dependency}")
    sbatch_options_list.append("--nodes=1")
    sbatch_options_list.append("--ntasks=1")
    sbatch_options_list.append("-c1")

    fout = Path(delayed_job_file_path).open("w")
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

    jobid = ""
    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(jobid, command_name)

    print(f"Callback script to launch {name} is placed at {delayed_job_file_path}")
    print(f"Once configuration is finished, {name} will automatically start as a Slurm "
          f"job: {jobid}")

    return jobid
