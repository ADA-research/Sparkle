#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
from pathlib import Path
from typing import List

try:
    from sparkle_help import sparkle_file_help as sfh
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_run_solvers_help as srsh
    from sparkle_help.sparkle_command_help import CommandName
    from sparkle_help import sparkle_configure_solver_help as scsh
    from sparkle_help import sparkle_basic_help as sbh
    from sparkle_help import sparkle_slurm_help as ssh
except ImportError:
    import sparkle_file_help as sfh
    import sparkle_global_help as sgh
    import sparkle_run_solvers_help as srsh
    from sparkle_command_help import CommandName
    import sparkle_configure_solver_help as scsh
    import sparkle_basic_help as sbh
    import sparkle_slurm_help as ssh


def call_configured_solver_for_instance(instance_path: str):
    # Create instance strings to accommodate multi-file instances
    instance_path_list = instance_path.split()
    instance_file_list = []

    for instance in instance_path_list:
        instance_file_list.append(f'../../{instance}')

    instance_files_str = " ".join(instance_file_list)

    # Run the configured solver
    print(f'c Start running the latest configured solver to solve instance '
          f'{instance_files_str} ...')
    run_configured_solver(instance_files_str)

    return


def generate_sbatch_script_for_configured_solver(num_jobs: int,
                                                 instance_list: List[str]) -> str:
    # Set script name and path
    solver_name, _ = get_latest_configured_solver_and_configuration()
    sbatch_script_name = (f'run_{solver_name}_configured_sbatch_'
                          f'{sbh.get_time_pid_random_string()}.sh')
    sbatch_script_path = sgh.sparkle_tmp_path + sbatch_script_name

    job = 'run_configured_solver'
    sbatch_options_list = ssh.get_sbatch_options_list(sbatch_script_path, num_jobs, job,
                                                      False)
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    job_params_list = []
    job_params_common = ('--performance-measure '
                         f'{sgh.settings.get_general_performance_measure().name}')

    for instance in instance_list:
        job_params = f'--instance {instance} {job_params_common}'
        job_params_list.append(job_params)

    srun_options_str = f'--nodes=1 --ntasks=1 {ssh.get_slurm_srun_user_options_str()}'

    target_call_str = (f'{sgh.python_executable} '
                       'Commands/sparkle_help/run_configured_solver_core.py')

    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_path


def call_configured_solver_for_instance_directory(instance_directory_path: str) -> str:
    if instance_directory_path[-1] != '/':
        instance_directory_path += '/'

    list_all_filename = sfh.get_instance_list_from_path(instance_directory_path)

    instance_list = []

    for filename in list_all_filename:
        paths = []

        for name in filename.split():
            path = instance_directory_path + name
            paths.append(path)

        filepath = " ".join(paths)
        instance_list.append(filepath)

    num_jobs = len(instance_list)
    sbatch_script_path = generate_sbatch_script_for_configured_solver(
        num_jobs, instance_list)
    command_name = CommandName.RUN_CONFIGURED_SOLVER
    execution_dir = './'
    jobid_str = ssh.submit_sbatch_script(sbatch_script_path, command_name, execution_dir)
    print('Submitted sbatch script for configured solver, '
          'output and results will be written to: '
          f'{sbatch_script_path}.txt')

    return jobid_str


def get_latest_configured_solver_and_configuration() -> (str, str):
    # Get latest configured solver + instance set
    solver_name = sfh.get_last_level_directory_name(
        str(sgh.latest_scenario.get_config_solver()))
    instance_set_name = sfh.get_last_level_directory_name(
        str(sgh.latest_scenario.get_config_instance_set_train()))

    if solver_name is None or instance_set_name is None:
        # Print error and stop execution
        print('ERROR: No configured solver found! Stopping execution.')
        sys.exit()

    # Get optimised configuration
    config_str = scsh.get_optimised_configuration_params(solver_name, instance_set_name)

    return solver_name, config_str


def run_configured_solver(instance_path: str):
    # Get latest configured solver and the corresponding optimised configuration
    solver_name, config_str = get_latest_configured_solver_and_configuration()

    # call smac wrapper OR call run_solver_on_instance...?
    # Single instance:
    # a) Create cmd_solver_call that could call smac wrapper
    # Unique string to request sparkle_smac_wrapper to write a '.rawres' file with raw
    # solver output in the tmp/ subdirectory of the execution directory:
    specifics = 'rawres'
    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    run_length = '2147483647'  # Arbitrary, not used in the SMAC wrapper
    seed_str = str(sgh.get_seed())
    cmd_solver_call = (f'{sgh.sparkle_smac_wrapper} {instance_path} {specifics} '
                       f'{cutoff_time_str} {run_length} {seed_str} {config_str}')
    # b) Call run_solver_cmd_on_instance (split run_solver_on_instance in two)
    solver_path = f'Solvers/{solver_name}'
    # Prepare paths
    instance_name = sfh.get_last_level_directory_name(instance_path)
    # TODO: Fix result path for multi-file instances (only a single file is part of the
    # result path)
    raw_result_path = (f'{sgh.sparkle_tmp_path}'
                       f'{sfh.get_last_level_directory_name(solver_path)}_'
                       f'{instance_name}_{sbh.get_time_pid_random_string()}.rawres')
    runsolver_values_path = raw_result_path.replace('.rawres', '.val')
    rawres_solver = srsh.run_solver_on_instance_with_cmd(solver_path, cmd_solver_call,
                                                         raw_result_path,
                                                         runsolver_values_path,
                                                         is_configured=True)

    # Process 'Result for SMAC' line from raw_result_path
    with open(Path(raw_result_path), 'r') as infile:
        results_good = False

        for line in infile:
            if 'Result for SMAC:' in line:
                results_good = True
                words = line.strip().split()

                # Check the result line has the correct number of words
                if len(words) != 9:
                    print('ERROR: Invalid number of words in \'result for SMAC\' line.')
                    results_good = False
                    break

                # Skip runsolver time measurement and the words 'Result for SMAC:'
                # Retrieve result information
                status = words[4].strip(',')
                runtime = words[5].strip(',')
                # Unused parts of the result string:
                # runlength = words[6].strip(',')
                # quality = words[7].strip(',')
                # seed = words[8]
                break
            elif 'EOF' in line:
                # Handle the timeout case
                results_good = True
                status = 'TIMEOUT'
                _, wc_time = srsh.get_runtime_from_runsolver(runsolver_values_path)
                runtime = wc_time

        if not results_good:
            print(f'ERROR: Results in {raw_result_path} appear to be faulty. '
                  'Stopping execution!')
            sys.exit(0)

    # Output results to user, including path to rawres_solver (e.g. SAT solution)
    output_msg = (f'Execution on instance {instance_name} completed with status {status}'
                  f' in {runtime} seconds.')

    if status == 'SUCCESS':
        output_msg += f' Solver output of the results can be found at: {rawres_solver}'

    print(output_msg)

    # Multi-instance:
    # a) Same?
    # b) Call running_solvers_parallel or run_solvers_core.py (somehow make them accept
    #    configured solver style input)

    # process output
    # write/print output
