#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
import shutil
import os
import subprocess
import datetime
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

def remove_temp_files_unfinished_solvers(solver_array_list: list, sbatch_script_name: str, temp_solvers: list):

    # Removes statusinfo files
    for solver_instance in solver_array_list:
        commandline = 'rm -rf Tmp/SBATCH_Parallel_Portfolio_Jobs/' + solver_instance + '*'
        os.system(commandline)    

    # Removes the generated sbatch files   
    commandline = 'rm -rf Tmp/' + sbatch_script_name + '*'
    os.system(commandline)

    # Removes generated the directories for the solver instances
    for temp_solver in temp_solvers:
            for directories in os.listdir(r'Tmp/'):
                directories_path = 'Tmp/' + directories
                for solver_instance in solver_array_list:
                    if os.path.isdir(directories_path) and directories.startswith(solver_instance[:len(temp_solver)+1]):
                        shutil.rmtree(directories_path)

    # Removes / Extracts all remaining files
    list_of_dir = os.listdir(r'Tmp/')
    to_be_deleted = []
    to_be_moved = []

    for files in list_of_dir:
        files_path = 'Tmp/' + files
        if not os.path.isdir(files_path):
            file = files[:files.rfind('.')]
            file = file + '.val'
            if file not in list_of_dir:
                to_be_deleted.append(files)
            else:
                to_be_moved.append(files)
                
    for files in to_be_deleted:
        commandline = 'rm -rf Tmp/' + files
        os.system(commandline)

    for files in to_be_moved:
        if sfh.get_file_least_extension(files) == '.val':
            commandline_from = 'Tmp/' + files
            commandline_to = 'Performance_Data/Tmp_PaP/' + files
            try:
                shutil.move(commandline_from, commandline_to)
            except:
                print('c the Tmp_PaP already contains a file with the same name, it will be skipped')
        else:
            commandline = 'rm -rf Tmp/' + files
            os.system(commandline)
    return

def find_finished_time_finished_solver(solver_array_list: list, finished_job_array_nr: int):
    # If there is a solver that ended but did not make a result file this means that it was manually cancelled
    # or it gave an error the template will ensure that all solver on that instance will be cancelled. 
    time_in_format_str = r'1:00' 
    solutions_dir  = r'Performance_Data/Tmp_PaP/'
    results = sfh.get_list_all_result_filename(solutions_dir)

    for result in results:
        if result.startswith(str(solver_array_list[int(finished_job_array_nr)])):
            result_file_path = solutions_dir + result
            result_file = open(result_file_path, 'r')
            result_lines = result_file.readlines()
            result_time = int(float(result_lines[2].strip()))
            time_in_format_str = str(datetime.timedelta(seconds = result_time))

    return time_in_format_str

def cancel_remaining_jobs(job_id:str, finished_job_array: list, portfolio_size: int, solver_array_list: list, pending_job_with_new_cutoff: dict = {}):
    # Find all job_array_numbers that are currently running
    result = subprocess.run(['squeue', '-r', '-j', job_id], capture_output=True, text=True)
    remaining_jobs = {}
    for jobs in result.stdout.strip().split('\n'):
            jobid = jobs.strip().split()[0]
            jobtime = jobs.strip().split()[5]
            jobstatus = jobs.strip().split()[4]
            if jobid in pending_job_with_new_cutoff and jobstatus == 'R':
                current_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(jobtime.split(':'))))
                sleep_time = int(pending_job_with_new_cutoff[jobid]) - int(current_seconds)
                command_line = r'sleep ' + str(sleep_time) + r'; scancel ' + str(jobid)
                pending_job_with_new_cutoff.pop(jobid)
            if jobid.startswith(str(job_id)):
                remaining_jobs[jobid] = [jobtime, jobstatus]

    for job in remaining_jobs:
        # Update all jobs in the same array segment as the finished job with its finishing time
        for finished_job in finished_job_array:
            # if job in the same array segment
            if (int(int(job[job.find('_')+1:])/int(portfolio_size)) == int(int(finished_job)/int(portfolio_size))):
                # Update the cutofftime of the to be cancelled job, if job if already past that it automatically stops.
                newCutoffTime = find_finished_time_finished_solver(solver_array_list, finished_job)
                current_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(remaining_jobs[job][0].split(':'))))
                cutoff_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(newCutoffTime.split(':'))))
                actual_cutofftime = sgh.settings.get_general_target_cutoff_time()
                if remaining_jobs[job][1] == 'R' and int(cutoff_seconds) < int(actual_cutofftime):
                    if  int(current_seconds) < int(cutoff_seconds):
                        sleep_time = int(cutoff_seconds) - int(current_seconds)
                        command_line = r'sleep ' + str(sleep_time) + r'; scancel ' + str(job)
                        print(command_line)
                    else:
                        command_line = r'scancel ' + str(job)
                        print(command_line)
                    process = subprocess.Popen(command_line, shell=True)
                else:
                    pending_job_with_new_cutoff[job] = cutoff_seconds
    
    return remaining_jobs, pending_job_with_new_cutoff


def wait_for_finished_solver(job_id: str, remaining_job_list: list, pending_job_with_new_cutoff = dict):
    number_of_solvers = len(remaining_job_list)
    n_seconds = 1
    done = False
    current_solver_list = remaining_job_list
    finished_solver_list = []
    while not done:
        result = subprocess.run(['squeue', '-r', '-j', job_id], capture_output=True, text=True)
        if ' R ' not in str(result):
            if len(result.stdout.strip().split('\n')) == 1:
                done = True
                break
            sjh.sleep(n_seconds) #No jobs have started yet;
        elif len(result.stdout.strip().split('\n')) < (1 + number_of_solvers):
            unfinished_solver_list = []
            for jobs in result.stdout.strip().split('\n'):
                jobid = jobs.strip().split()[0]
                if jobid.startswith(str(job_id)):
                    unfinished_solver_list.append(jobid[jobid.find('_')+1:])
            finished_solver_list = [item for item in current_solver_list if item not in unfinished_solver_list]
            done = True
        else:
            sjh.sleep(n_seconds)
            current_solver_list = []
            for jobs in result.stdout.strip().split('\n'):
                jobid = jobs.strip().split()[0]
                jobtime = jobs.strip().split()[5]
                jobstatus = jobs.strip().split()[4]
                if jobid in pending_job_with_new_cutoff and jobstatus == 'R':
                    current_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(jobtime.split(':'))))
                    sleep_time = int(pending_job_with_new_cutoff[jobid]) - int(current_seconds)
                    command_line = r'sleep ' + str(sleep_time) + r'; scancel ' + str(jobs)
                    pending_job_with_new_cutoff.pop(jobid)
                if(jobid.startswith(str(job_id))):
                    current_solver_list.append(jobid[jobid.find('_')+1:])
            number_of_solvers = len(current_solver_list)

    return finished_solver_list, pending_job_with_new_cutoff

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
    
    return parameters, new_num_jobs, solver_array_list, list(dict.fromkeys(tmp_solver_instances))

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

def handle_waiting_and_removal_process(job_number: str, solver_array_list: list, sbatch_script_name: str, portfolio_size: int, remaining_job_list: list, pending_job_with_new_cutoff: dict):

    if len(remaining_job_list): 
        print('c a job has ended, remaining jobs = ' + str(len(remaining_job_list)))
    finished_jobs, pending_job_with_new_cutoff = wait_for_finished_solver(job_number, remaining_job_list, pending_job_with_new_cutoff)
    
    # Handles the updating of all jobs within the portfolios of which contain a finished job
    remaining_job_list, pending_job_with_new_cutoff = cancel_remaining_jobs(job_number, finished_jobs, portfolio_size, solver_array_list, pending_job_with_new_cutoff)

    # If there are still unfinished jobs recursively handle the remaining jobs.
    if len(remaining_job_list):
        handle_waiting_and_removal_process(job_number, solver_array_list, sbatch_script_name, portfolio_size, remaining_job_list, pending_job_with_new_cutoff)

    return True

def run_parallel_portfolio(instances: list, portfolio_path: Path, cutoff_time: int)->bool:
    print('DEBUG cutoff_time: ' + str(cutoff_time))

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
        
        if(performance == 'RUNTIME'):
            handle_waiting_and_removal_process(job_number, solver_array_list, sbatch_script_name, num_jobs/len(instances), [], {})
            
            # After all jobs have finished remove/extract the files in temp only needed for the running of the portfolios.
            remove_temp_files_unfinished_solvers(solver_array_list,sbatch_script_name, temp_solvers)

        else:
            print('c the sbatch job has been generated and submitted,')
            

    except Exception as e:
        # DEBUG
        print(e)
        print('c an error occurred when running the portfolio')
        return False

    return True