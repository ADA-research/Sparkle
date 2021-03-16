#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
import os
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_run_solvers_help as srsh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_job_help as sjh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_slurm_help as ssh

def generate_sbatch_script(parameters, num_jobs):
    # Set script name and path
    sbatch_script_name = 'parallel_portfolio_sbatch_shell_script_' + str(num_jobs) + '_' + sbh.get_time_pid_random_string() + '.sh'
    sbatch_script_dir = sgh.sparkle_tmp_path
    sbatch_script_path = sbatch_script_dir + sbatch_script_name

    ## Set sbatch options
    max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
    if num_jobs < max_jobs:
        max_jobs = num_jobs
    job_name = '--job-name=' + sbatch_script_name
    output = '--output=' + sbatch_script_path + '.txt'
    error = '--error=' + sbatch_script_path + '.err'
    array = '--array=0-' + str(num_jobs-1) + '%' + str(max_jobs)

    sbatch_options_list = [job_name, output, error, array]
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list()) # Get user options second to overrule defaults

    # Create job list
    job_params_list = parameters

    ## Set srun options
    srun_options_str = '-N1 -n1'
    srun_options_str = srun_options_str + ' ' + ssh.get_slurm_srun_user_options_str()

    ## Create target call
    target_call_str = 'Commands/sparkle_help/run_solvers_core.py'
    
    ## Generate script
    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

    return sbatch_script_name, sbatch_script_dir


def generate_parameters(solver_list, instance_path, cutoff_time):
    
    parameters = list()
    for solver in solver_list:
        solver_path = Path(solver)
        # TODO add cutoff_time
        commandline = ' --instance ' + str(instance_path) + ' --solver ' + str(solver_path)
        parameters.append(str(commandline))
    return parameters

def run_sbatch(sbatch_script_path,sbatch_script_name):
    sbatch_shell_script_path_str = str(sbatch_script_path) + str(sbatch_script_name)
    print('DEBUG ' + sbatch_shell_script_path_str)
    os.system('chmod a+x ' + sbatch_shell_script_path_str)
    command_line = 'sbatch ' + str(sbatch_shell_script_path_str)
    
    os.system(command_line)

    return True

def run_parallel_portfolio(instances: list, portfolio_path: Path, cutoff_time: int)->bool:
    print('DEBUG instances: ' + str(instances))
    print('DEBUG portfolio_path: ' + str(portfolio_path))
    print('DEBUG cutoff_time: ' + str(cutoff_time))
    #TODO add functionality for multiple instances
    # Something with generate_running_solvers_sbatch_shell_script + total jobs is parallel jobs * nr of instances
    if(len(instances) > 1): 
        print('c running on multiple instances is not yet supported, aborting the process')
        return False

    solver_list = sfh.get_solver_list_from_parallel_portfolio(portfolio_path)
    num_jobs = len(solver_list)
    print('c there are ' + str(num_jobs) + ' jobs, this requires a total of ' + str(num_jobs*3) + ' gb')

    # Makes SBATCH scripts for all individual solvers in a list
    parameters = generate_parameters(solver_list, Path(instances[0]), cutoff_time)
    #print('DEBUG parameters ' + str(parameters))
    
    # Generates a SBATCH script which uses the created parameters
    sbatch_script_name,sbatch_script_path = generate_sbatch_script(parameters, num_jobs)
    print('DEBUG ' + str(sbatch_script_path) + ' + ' + str(sbatch_script_name))

    # Runs the script and cancels the remaining scripts if a script finishes before the end of the cutoff_time
    try:
        run_sbatch(sbatch_script_path,sbatch_script_name)
    except:
        print('c an error occurred when running the portfolio')
        return False

    return True