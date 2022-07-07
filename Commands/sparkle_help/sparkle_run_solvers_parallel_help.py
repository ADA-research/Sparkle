#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_job_help as sjh
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_logging as sl
from sparkle_help.sparkle_command_help import CommandName


def generate_running_solvers_sbatch_shell_script(total_job_num: int,
                                                 num_job_in_parallel: int, total_job_list
                                                 ) -> (str, str, str):
    sbatch_script_name = ('running_solvers_sbatch_shell_script_'
                          f'{sbh.get_time_pid_random_string()}.sh')
    sbatch_script_path = 'Tmp/' + sbatch_script_name
    job_name = '--job-name=' + sbatch_script_name
    std_out_path = sbatch_script_path + '.txt'
    std_err_path = sbatch_script_path + '.err'
    output = '--output=' + std_out_path
    error = '--error=' + std_err_path
    array = '--array=0-' + str(total_job_num-1) + '%' + str(num_job_in_parallel)

    sbatch_options_list = [job_name, output, error, array]
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())
    job_params_list = []

    for job in total_job_list:
        instance_path = job[0]
        solver_path = job[1]
        performance_measure = sgh.settings.get_general_performance_measure()
        job_params_list.append(f'--instance {instance_path} --solver {solver_path}'
                               f' --performance-measure {performance_measure.name}')

    srun_options_str = '-N1 -n1'
    srun_options_str = srun_options_str + ' ' + ssh.get_slurm_srun_user_options_str()
    target_call_str = 'Commands/sparkle_help/run_solvers_core.py'

    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_path, std_out_path, std_err_path


def running_solvers_parallel(performance_data_csv_path, num_job_in_parallel, mode):
    ####
    # This function is used for running solvers in parallel.
    # The 1st argument (performance_data_csv_path) specifies the path of the csv file
    # where the resulting performance data would be placed.
    # The 2nd argument (num_job_in_parallel) specifies the number of jobs that will be
    # executing in parallel.
    # The 3nd argument (mode) specifies the mode of computation. It has 2 possible values
    # (1 or 2). If this value is 1, it means that this function will compute the
    # remaining jobs for performance computation. Otherwise (if this value is 2), it
    # means that this function will re-compute all jobs for performance computation.
    ####

    # Open the csv file in terms of performance data
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)

    if mode == 1:
        # The value of mode is 1, so the list of computation jobs is the list of the
        # remaining jobs
        list_performance_computation_job = (
            performance_data_csv.get_list_remaining_performance_computation_job())
    elif mode == 2:
        # The value of mode is 2, so the list of computation jobs is the list of all jobs
        # (recomputing)
        list_performance_computation_job = (
            performance_data_csv.get_list_recompute_performance_computation_job())
    else:  # The abnormal case, exit
        print('Running solvers mode error!')
        print('Do not run solvers')
        sys.exit()

    # Print the information about the cutoff time
    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    print(f'Cutoff time for each run on solving an instance is set to {cutoff_time_str}'
          ' seconds')

    ####
    # expand the job list
    total_job_num = sjh.get_num_of_total_job_from_list(list_performance_computation_job)
    print('The number of total running jobs: ' + str(total_job_num))
    total_job_list = sjh.expand_total_job_from_list(list_performance_computation_job)
    ####

    # If there are no jobs, stop
    if len(total_job_list) == 0:
        return ''
    # If there are jobs update performance data ID
    else:
        srs.update_performance_data_id()

    sbatch_script_path, std_out_path, std_err_path = (
        generate_running_solvers_sbatch_shell_script(total_job_num, num_job_in_parallel,
                                                     total_job_list))
    command_line = 'sbatch ' + sbatch_script_path
    ####

    # Log output paths
    sl.add_output(sbatch_script_path, 'Slurm batch script to run solvers in parallel')
    sl.add_output(std_out_path,
                  'Standard output of Slurm batch script to run solvers in parallel')
    sl.add_output(std_err_path,
                  'Error output of Slurm batch script to run solvers in parallel')

    # Execute the sbatch script via slurm
    output_list = os.popen(command_line).readlines()
    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        run_solvers_parallel_jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(run_solvers_parallel_jobid, CommandName.RUN_SOLVERS)
    else:
        run_solvers_parallel_jobid = ''

    return run_solvers_parallel_jobid
