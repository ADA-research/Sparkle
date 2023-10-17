#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a configured solver."""

import sys
from pathlib import Path

from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_run_solvers_help as srsh
from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help import sparkle_configure_solver_help as scsh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help import sparkle_instances_help as sih

from sparkle.slurm_parsing import SlurmBatch
import runrunner as rrr
from runrunner.base import Runner


def call_configured_solver(instance_path_list: list[Path],
                           parallel: bool,
                           run_on: Runner = Runner.SLURM) -> str:
    """Create list of instance path lists, and call solver in parallel or sequential."""
    job_id_str = None

    # If directory, get instance list from directory as list[list[Path]]
    if len(instance_path_list) == 1 and instance_path_list[0].is_dir():
        instance_directory_path = instance_path_list[0]
        list_all_filename = sih.get_instance_list_from_path(instance_directory_path)

        # Create an instance list keeping in mind possible multi-file instances
        instances_list = []

        for filename_str in list_all_filename:
            instances_list.append([instance_directory_path / name
                                  for name in filename_str.split()])
    # Else single instance turn it into list[list[Path]]
    else:
        instances_list = [instance_path_list]
    
    # If parallel, pass instances list to parallel function
    if parallel:
        job_id_str = call_configured_solver_parallel(instances_list, run_on=run_on)
    # Else, pass instances list to sequential function
    else:
        call_configured_solver_sequential(instances_list)

    return job_id_str


def call_configured_solver_sequential(instances_list: list[list[Path]],
                                      run_on: Runner = Runner.SLURM) -> None:
    """Prepare to run and run the latest configured solver sequentially on instances."""
    for instance_path_list in instances_list:
        # Use original path for output string
        instance_path_str = " ".join([str(path) for path in instance_path_list])

        # Extend paths to work from execution directory under Tmp/
        instance_path_list = ["../../" / instance for instance in instance_path_list]

        # Run the configured solver
        print(f"c Start running the latest configured solver to solve instance "
              f"{instance_path_str} ...")
        run_configured_solver(instance_path_list)

    return


def generate_sbatch_script_for_configured_solver(num_jobs: int,
                                                 instance_list: list[str]) -> Path:
    """Return the path to a Slurm batch script to run the solver on all instances."""
    # Set script name and path
    solver_name, _ = get_latest_configured_solver_and_configuration()
    sbatch_script_name = (f"run_{solver_name}_configured_sbatch_"
                          f"{sbh.get_time_pid_random_string()}.sh")
    sbatch_script_path = Path(f"{sgh.sparkle_tmp_path}{sbatch_script_name}")

    job = "run_configured_solver"
    sbatch_options_list = ssh.get_sbatch_options_list(sbatch_script_path, num_jobs, job,
                                                      smac=False)
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    job_params_common = ("--performance-measure "
                         f"{sgh.settings.get_general_performance_measure().name}")
    job_params_list = [f"--instance {instance} {job_params_common}"
                       for instance in instance_list]

    srun_options_str = f"--nodes=1 --ntasks=1 {ssh.get_slurm_srun_user_options_str()}"

    target_call_str = (f"{sgh.python_executable} "
                       "Commands/sparkle_help/run_configured_solver_core.py")

    ssh.generate_sbatch_script_generic(str(sbatch_script_path), sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_path


def call_configured_solver_parallel(instances_list: list[list[Path]],
                                    run_on: Runner = Runner.SLURM) -> str:
    """Run the latest configured solver in parallel on all given instances."""
    # Create an instance list[str] keeping in mind possible multi-file instances
    instance_list = []

    for instance_path_list in instances_list:
        instance_list.append(" ".join([str(path) for path in instance_path_list]))

    # Prepare batch script
    num_jobs = len(instance_list)
    sbatch_script_path = generate_sbatch_script_for_configured_solver(
        num_jobs, instance_list)

    # Run batch script
    cmd_name = CommandName.RUN_CONFIGURED_SOLVER
    exec_dir = "./"
    jobid_str = ""
    if run_on == Runner.SLURM:
        jobid_str = ssh.submit_sbatch_script(sbatch_script_name=str(sbatch_script_path),
                                             command_name=cmd_name,
                                             execution_dir=exec_dir)
        print("Submitted sbatch script for configured solver, "
              "output and results will be written to: "
              f"{sbatch_script_path}.txt")
    else:
        # Remove the below if block once runrunner works satisfactorily
        if run_on == Runner.SLURM_RR:
            run_on = Runner.SLURM

        batch = SlurmBatch(sbatch_script_path)
        cmd_list = [f"{batch.cmd} {param}" for param in batch.cmd_params]
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd_list,
            name=cmd_name,
            base_dir=exec_dir,
            sbatch_options=batch.sbatch_options,
            srun_options=batch.srun_options)
        #jobid_str = run.run_id
        print(f"Configured solver added to {run_on} queue.")
        
        # Remove the below if block once runrunner works satisfactorily
        if run_on == Runner.SLURM:
            run_on = Runner.SLURM_RR

    return jobid_str


def get_latest_configured_solver_and_configuration() -> (str, str):
    """Return the name and parameter string of the latest configured solver."""
    # Get latest configured solver + instance set
    solver_name = sfh.get_last_level_directory_name(
        str(sgh.latest_scenario.get_config_solver()))
    instance_set_name = sfh.get_last_level_directory_name(
        str(sgh.latest_scenario.get_config_instance_set_train()))

    if solver_name is None or instance_set_name is None:
        # Print error and stop execution
        print("ERROR: No configured solver found! Stopping execution.")
        sys.exit()

    # Get optimised configuration
    config_str = scsh.get_optimised_configuration_params(solver_name, instance_set_name)

    return solver_name, config_str


def run_configured_solver(instance_path_list: list[Path],
                          run_on: Runner = Runner.SLURM) -> None:
    """Run the latest configured solver on the given instance."""
    # Get latest configured solver and the corresponding optimised configuration
    solver_name, config_str = get_latest_configured_solver_and_configuration()
    # a) Create cmd_solver_call that could call sparkle_smac_wrapper
    instance_path_str = " ".join([str(path) for path in instance_path_list])
    # Set specifics to the unique string 'rawres' to request sparkle_smac_wrapper to
    # write a '.rawres' file with raw solver output in the tmp/ subdirectory of the
    # execution directory:
    specifics = "rawres"
    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    run_length = "2147483647"  # Arbitrary, not used in the SMAC wrapper
    seed_str = str(sgh.get_seed())
    cmd_solver_call = (f"{sgh.sparkle_smac_wrapper} {instance_path_str} {specifics} "
                       f"{cutoff_time_str} {run_length} {seed_str} {config_str}")
    
    # Prepare paths
    solver_path = Path(f"Solvers/{solver_name}")
    instance_name = "_".join([path.name for path in instance_path_list])
    raw_result_path = Path(f"{sgh.sparkle_tmp_path}{solver_path.name}_"
                           f"{instance_name}_{sbh.get_time_pid_random_string()}.rawres")
    runsolver_values_path = Path(str(raw_result_path).replace(".rawres", ".val"))
    
    # b) Run the solver
    rawres_solver = srsh.run_solver_on_instance_with_cmd(solver_path, cmd_solver_call,
                                                         raw_result_path,
                                                         runsolver_values_path,
                                                         is_configured=True)

    # Process 'Result for SMAC' line from raw_result_path
    with Path(raw_result_path).open("r") as infile:
        results_good = False

        for line in infile:
            if "Result for SMAC:" in line:
                results_good = True
                words = line.strip().split()

                # Check the result line has the correct number of words
                if len(words) != 9:
                    print('ERROR: Invalid number of words in "result for SMAC" line.')
                    results_good = False
                    break

                # Skip runsolver time measurement and the words 'Result for SMAC:'
                # Retrieve result information
                status = words[4].strip(",")
                runtime = words[5].strip(",")
                # Unused parts of the result string:
                # runlength = words[6].strip(',')
                # quality = words[7].strip(',')
                # seed = words[8]
                break
            elif "EOF" in line:
                # Handle the timeout case
                results_good = True
                status = "TIMEOUT"
                _, wc_time = srsh.get_runtime_from_runsolver(str(runsolver_values_path))
                runtime = wc_time

        if not results_good:
            print(f"ERROR: Results in {str(raw_result_path)} appear to be faulty. "
                  "Stopping execution!")
            sys.exit(0)

    # Output results to user, including path to rawres_solver (e.g. SAT solution)
    output_msg = (f"Execution on instance {instance_name} completed with status {status}"
                  f" in {runtime} seconds.")

    if status == "SUCCESS":
        output_msg += (" Solver output of the results can be found at: "
                       f"{str(rawres_solver)}")

    print(output_msg)

    return
