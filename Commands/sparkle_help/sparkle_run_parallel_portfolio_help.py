#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
import shutil
import os
import subprocess
import math
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_run_solvers_help as srsh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_job_help as sjh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help.sparkle_settings import PerformanceMeasure

def remove_temp_files_unfinished_solvers(solver_array_list: list, unfinished_solver_list: list, sbatch_script_name: str, temp_solvers: list):
    print('DEBUG the unfinished solvers are: ')

    for unfinished_solver in unfinished_solver_list:
        print(unfinished_solver)
        solver_file_name = solver_array_list[int(unfinished_solver[unfinished_solver.find('_')+1:])] # THIS IS WRONG
        commandline = 'rm -rf Tmp/' + solver_file_name + '*'
        os.system(commandline)
        commandline = 'rm -rf Tmp/SBATCH_Parallel_Portfolio_Jobs/' + solver_file_name + '*'
        os.system(commandline)
        for temp_solver in temp_solvers:
            if solver_file_name.startswith(temp_solver):
                for directories in os.listdir(r'Tmp/'):
                    if os.path.isdir(directories) and directories.startswith(solver_file_name[:len(temp_solver)+1]):
                        commandline = 'Tmp/' + directories
                        shutil.rmtree(commandline)
   
    commandline = 'rm -rf Tmp/' + sbatch_script_name + '*'
    os.system(commandline)

    return

def cancel_remaining_jobs(job_id:str, to_be_cancelled_list: list, num_jobs: int, finished_job_array_nr: str, portfolio_size: int):
    sjh.sleep(2)
    result = subprocess.run(['squeue', '-j', job_id], capture_output=True, text=True)
    remaining_jobs = []
    cancelled_list = to_be_cancelled_list
    num_remaining_jobs = num_jobs - 1
    for ids in result.stdout.strip().split(' '):
        if str(job_id) in ids:
            remaining_jobs.append(ids)

    for job in remaining_jobs:
        # If job not in same array segment as finished job than skip this part and remove remaining_job list
        if int(int(job[job.find('_')+1:])/int(portfolio_size)) == int(int(finished_job_array_nr)/int(portfolio_size)):
            print('c Cancelling job ' + str(job) + ' because the instances has been solved.')
            command_line = 'scancel ' + str(job)
            os.system(command_line)
            cancelled_list.append(str(job))
            num_remaining_jobs = num_remaining_jobs - 1
    return cancelled_list, num_remaining_jobs


def wait_for_finished_solver(job_id: str, num_jobs):
    number_of_solvers = int(num_jobs)
    n_seconds = 1
    done = False
    current_solver_list = []
    finished_solver_list = []
    while not done:
        result = subprocess.run(['squeue', '-j', job_id], capture_output=True, text=True)
        if(' PD ' in str(result)):
            sjh.sleep(n_seconds) #The job is still pending;
        elif len(result.stdout.strip().split('\n')) < (1 + number_of_solvers):
            unfinished_solver_list = []
            for jobs in result.stdout.strip().split('\n'):
                jobid = jobs.strip().split()[0]
                if(jobid.startswith(str(job_id))):
                    unfinished_solver_list.append(jobid[jobid.find('_')+1:])
            finished_solver_list = [item for item in current_solver_list if item not in unfinished_solver_list]
            done = True
        else:
            sjh.sleep(n_seconds)
            current_solver_list = []
            for jobs in result.stdout.strip().split('\n'):
                jobid = jobs.strip().split()[0]
                if(jobid.startswith(str(job_id))):
                    current_solver_list.append(jobid[jobid.find('_')+1:])

            #print('Checking for a finished solver again in', n_seconds, 'seconds')

    if len(finished_solver_list):
        print('Job with ID', job_id, ' has a finished solver!')
    else:
        print('DEBUG first unfinished solver list then current solver list')
        print(unfinished_solver_list)
        print(current_solver_list)
        print('Job with ID', job_id, ' has a finished solver! (or cut-off time has been reached)')
    finished_solver = int(finished_solver_list[0])
    print('DEBUG finished solver: ' + str(finished_solver))
    return finished_solver

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
    target_call_str = 'Commands/sparkle_help/run_solvers_core.py --run-status-path Tmp/SBATCH_Parallel_Portfolio_Jobs/'

    ## Generate script
    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

    return sbatch_script_name, sbatch_script_dir

def generate_parameters(solver_list, instance_path_list, cutoff_time, performance, num_jobs):
    # TODO add cutoff_time
    parameters = list()
    new_num_jobs = num_jobs
    solver_array_list = []
    tmp_solver_instances = []
    for instance_path in instance_path_list:
        for solver in solver_list:
            if " " in solver:
                solver_path, seed = solver.strip().split()
                tmp_solver_instances.append(str(sfh.get_last_level_directory_name(str(solver_path))) + r'_seed_')
                new_num_jobs = new_num_jobs + int(seed) - 1
                for instance in range(1,int(seed)+1):
                    commandline = ' --instance ' + str(instance_path) + ' --solver ' + str(solver_path) + ' --performance-measure ' + str(performance) + ' --seed ' + str(instance)
                    parameters.append(str(commandline))
                    solver_array_list.append(str(sfh.get_last_level_directory_name(str(solver_path))) + r'_seed_' + str(instance)  + r'_' + str(sfh.get_last_level_directory_name(str(instance_path))))  
            else:
                solver_path = Path(solver)
                solver_array_list.append(str(sfh.get_last_level_directory_name(str(solver_path))) + r'_' + str(sfh.get_last_level_directory_name(str(instance_path))))
                commandline = ' --instance ' + str(instance_path) + ' --solver ' + str(solver_path) + ' --performance-measure ' + str(performance)
                parameters.append(str(commandline))
    
    return parameters, new_num_jobs, solver_array_list, tmp_solver_instances

def run_sbatch(sbatch_script_path,sbatch_script_name):
    sbatch_shell_script_path_str = str(sbatch_script_path) + str(sbatch_script_name)

    os.system('chmod a+x ' + sbatch_shell_script_path_str)
    command_line = 'sbatch ' + str(sbatch_shell_script_path_str)

    output_list = os.popen(command_line).readlines()
    if len(output_list) > 0 and len(output_list[0].strip().split())>0:
        run_job_parallel_jobid = output_list[0].strip().split()[-1]
        return run_job_parallel_jobid

    print('DEBUG INTO output_list not good')
    return ''

def handle_waiting_and_removal_process(job_number: str, num_jobs: int, solver_array_list: list, sbatch_script_name: str, temp_solvers: list, portfolio_size: int, to_be_cancelled_list: list = []):
    cancelled_jobs = to_be_cancelled_list
    print('DEBUG cancelled_jobs length = ' + str(len(cancelled_jobs)) + ' and num_jobs size = ' + str(num_jobs))
    finished_job_array_nr = wait_for_finished_solver(job_number, num_jobs)
    print('DEBUG after wait for finished solver')
    unfinished_solver_list, remaining_jobs = cancel_remaining_jobs(job_number, cancelled_jobs, num_jobs, finished_job_array_nr, portfolio_size)
    print('DEBUG cancel remaining jobs')
    if remaining_jobs > 0:
        handle_waiting_and_removal_process(job_number, remaining_jobs , solver_array_list, sbatch_script_name, temp_solvers, portfolio_size, unfinished_solver_list)
    remove_temp_files_unfinished_solvers(solver_array_list,unfinished_solver_list,sbatch_script_name, temp_solvers)
    return True

def run_parallel_portfolio(instances: list, portfolio_path: Path, cutoff_time: int)->bool:
    print('DEBUG cutoff_time: ' + str(cutoff_time))
    #TODO add functionality for nodes, differentiating starting times.

    #TODO add performance functionality
    if sgh.settings.get_general_performance_measure() == PerformanceMeasure.QUALITY_ABSOLUTE:
        performance = 'QUALITY_ABSOLUTE'
    else:
        performance = 'RUNTIME'

    solver_list = sfh.get_solver_list_from_parallel_portfolio(portfolio_path)
    num_jobs = len(solver_list) * len(instances)

    # Makes SBATCH scripts for all individual solvers in a list
    parameters, num_jobs, solver_array_list, temp_solvers = generate_parameters(solver_list, instances, cutoff_time, performance, num_jobs)
    
    # Generates a SBATCH script which uses the created parameters
    sbatch_script_name,sbatch_script_path = generate_sbatch_script(parameters, num_jobs)
    # Runs the script and cancels the remaining scripts if a script finishes before the end of the cutoff_time
    try:
        job_number = run_sbatch(sbatch_script_path,sbatch_script_name)
        print('DEBUG job_number: ' + job_number)
        
        if(performance == 'RUNTIME'):
            handle_waiting_and_removal_process(job_number, num_jobs, solver_array_list, sbatch_script_name, temp_solvers, num_jobs/len(instances))
            
        else:
            print('c the sbatch job has been generated and submitted,')
            

    except Exception as e:
        # DEBUG
        print(e)
        print('c an error occurred when running the portfolio')
        return False

    return True