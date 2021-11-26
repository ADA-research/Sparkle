#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import shutil
import os
import subprocess
import datetime
import fcntl
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as slog
from sparkle_help import sparkle_job_help as sjh
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help.sparkle_settings import PerformanceMeasure, ProcessMonitoring
from sparkle_help.sparkle_command_help import CommandName


def jobtime_to_seconds(jobtime: str) -> int:
    """Convert a jobtime string to an integer number of seconds."""
    seconds = int(sum(int(x) * 60 ** i for i, x in enumerate(
        reversed(jobtime.split(':')))))

    return seconds


def add_log_statement_to_file(log_file: str, line: str, jobtime: str):
    """Log the starting time, end time and job number to a given file."""
    now = datetime.datetime.now()
    job_duration_seconds = jobtime_to_seconds(jobtime)
    job_running_time = datetime.timedelta(seconds=job_duration_seconds)

    if line.rfind(';') != -1:
        sleep_seconds = line[:line.rfind(';')]
        sleep_seconds = int(sleep_seconds[sleep_seconds.rfind(' ')+1:])
        now = now + datetime.timedelta(seconds=sleep_seconds)
        job_running_time = job_running_time + datetime.timedelta(seconds=sleep_seconds)
        job_nr = line[line.rfind(';')+2:]

    current_time = now.strftime("%H:%M:%S")
    job_starting_time = now - job_running_time
    start_time_formatted = job_starting_time.strftime("%H:%M:%S")

    with open(log_file, 'a+') as outfile:
        fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
        outfile.write(f'starting time: {start_time_formatted} end time: {current_time} '
                      f'job number: {job_nr}\n')

    return


def log_computation_time(log_file: str, job_nr: str, job_duration: str):
    """Log the job number and job duration."""
    if ':' in job_duration:
        job_duration = str(jobtime_to_seconds(job_duration))

    if '_' in job_nr:
        job_nr = job_nr[job_nr.rfind('_')+1:]

    with open(log_file, 'a+') as outfile:
        fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
        outfile.write(f'{job_nr}:{job_duration}\n')

    return


def remove_temp_files_unfinished_solvers(solver_array_list: list,
                                         sbatch_script_path: Path, temp_solvers: list):
    # Removes statusinfo files
    for solver_instance in solver_array_list:
        commandline = f'rm -rf Tmp/SBATCH_Parallel_Portfolio_Jobs/{solver_instance}*'
        os.system(commandline)

    # Removes the generated sbatch files
    commandline = f'rm -rf {sbatch_script_path}*'
    os.system(commandline)

    # Removes the directories generated for the solver instances
    for temp_solver in temp_solvers:
        for directories in os.listdir('Tmp/'):
            directories_path = 'Tmp/' + directories

            for solver_instance in solver_array_list:
                if (os.path.isdir(directories_path)
                        and directories.startswith(
                            solver_instance[:len(temp_solver)+1])):
                    shutil.rmtree(directories_path)

    # Removes / Extracts all remaining files
    list_of_dir = os.listdir('Tmp/')
    to_be_deleted = []
    to_be_moved = []

    for files in list_of_dir:
        files_path = 'Tmp/' + files

        if not os.path.isdir(files_path):
            tmp_file = files[:files.rfind('.')]
            tmp_file = tmp_file + '.val'

            if tmp_file not in list_of_dir:
                to_be_deleted.append(files)
            else:
                to_be_moved.append(files)

    for files in to_be_deleted:
        commandline = 'rm -rf Tmp/' + files
        os.system(commandline)

    for files in to_be_moved:
        if '.val' in files:
            commandline_from = 'Tmp/' + files
            commandline_to = 'Performance_Data/Tmp_PaP/' + files

            try:
                shutil.move(commandline_from, commandline_to)
            except shutil.Error:
                print('c the Tmp_PaP already contains a file with the same name, it will'
                      ' be skipped')
            commandline = 'rm -rf Tmp/' + files
            os.system(commandline)

    return


# TODO: Investigate finished_job_array_nr, it is indicated to be an int, but also treated
# as str internally
def find_finished_time_finished_solver(solver_array_list: list,
                                       finished_job_array_nr: int) -> str:
    # If there is a solver that ended but did not make a result file this means that it
    # was manually cancelled or it gave an error the template will ensure that all
    # solver on that instance will be cancelled.
    time_in_format_str = '-1:00'
    solutions_dir = 'Performance_Data/Tmp_PaP/'
    results = sfh.get_list_all_result_filename(solutions_dir)

    for result in results:
        if '_' in str(finished_job_array_nr):
            finished_job_array_nr = finished_job_array_nr[
                finished_job_array_nr.rfind('_')+1:]

        if result.startswith(str(solver_array_list[int(finished_job_array_nr)])):
            result_file_path = solutions_dir + result

            with open(result_file_path, 'r') as result_file:
                result_lines = result_file.readlines()
                result_time = int(float(result_lines[2].strip()))
                time_in_format_str = str(datetime.timedelta(seconds=result_time))

    return time_in_format_str


def cancel_remaining_jobs(logging_file: str, job_id: str, finished_job_array: list,
                          portfolio_size: int, solver_array_list: list,
                          pending_job_with_new_cutoff: dict = {}):
    # Find all job_array_numbers that are currently running
    # This is specifically for Grace
    result = subprocess.run(['squeue', '--array', '--jobs', job_id], capture_output=True,
                            text=True)
    remaining_jobs = {}

    for jobs in result.stdout.strip().split('\n'):
        jobid = jobs.strip().split()[0]
        jobtime = jobs.strip().split()[5]
        jobstatus = jobs.strip().split()[4]

        # If option extended is used some jobs are not directly cancelled to allow all
        # jobs to compute for at least the same running time.
        if (sgh.settings.get_paraport_process_monitoring()
                == ProcessMonitoring.EXTENDED):
            # If a job in a portfolio with a finished solver starts running its timelimit
            # needs to be updated.
            if jobid in pending_job_with_new_cutoff and jobstatus == 'R':
                current_seconds = jobtime_to_seconds(jobtime)
                sleep_time = (int(pending_job_with_new_cutoff[jobid])
                              - int(current_seconds))
                command_line = f'sleep {str(sleep_time)}; scancel {str(jobid)}'
                add_log_statement_to_file(logging_file, command_line, jobtime)
                pending_job_with_new_cutoff.pop(jobid)

        if jobid.startswith(str(job_id)):
            remaining_jobs[jobid] = [jobtime, jobstatus]

    for job in remaining_jobs:
        # Update all jobs in the same array segment as the finished job with its
        # finishing time
        for finished_job in finished_job_array:
            # if job in the same array segment
            if (int(int(job[job.find('_')+1:])/int(portfolio_size))
                    == int(int(finished_job)/int(portfolio_size))):
                # If option extended is used some jobs are not directly cancelled to
                # allow all jobs to compute for at least the same running time.
                if (sgh.settings.get_paraport_process_monitoring()
                        == ProcessMonitoring.EXTENDED):
                    # Update the cutofftime of the to be cancelled job, if job if
                    # already past that it automatically stops.
                    newCutoffTime = find_finished_time_finished_solver(
                        solver_array_list, finished_job)
                    current_seconds = jobtime_to_seconds(remaining_jobs[job][0])
                    cutoff_seconds = jobtime_to_seconds(newCutoffTime)
                    actual_cutofftime = sgh.settings.get_general_target_cutoff_time()

                    if (remaining_jobs[job][1] == 'R'
                            and int(cutoff_seconds) < int(actual_cutofftime)):
                        if int(current_seconds) < int(cutoff_seconds):
                            sleep_time = int(cutoff_seconds) - int(current_seconds)
                            command_line = f'sleep {str(sleep_time)}; scancel {str(job)}'
                            add_log_statement_to_file(logging_file, command_line,
                                                      remaining_jobs[job][0])
                        else:
                            command_line = f'scancel {str(job)}'
                            add_log_statement_to_file(logging_file, command_line,
                                                      remaining_jobs[job][0])
                            logging_file2 = (
                                f"{logging_file[:logging_file.rfind('.')]}2.txt")
                            log_computation_time(logging_file2, job, cutoff_seconds)
                        subprocess.Popen(command_line, shell=True)
                    else:
                        pending_job_with_new_cutoff[job] = cutoff_seconds
                else:
                    command_line = f'scancel {str(job)}'
                    add_log_statement_to_file(logging_file, command_line,
                                              remaining_jobs[job][0])
                    logging_file2 = logging_file[:logging_file.rfind('.')] + '2.txt'
                    log_computation_time(logging_file2, job, '-1')
                    subprocess.Popen(command_line, shell=True)

    return remaining_jobs, pending_job_with_new_cutoff


def wait_for_finished_solver(logging_file: str, job_id: str, solver_array_list: list,
                             remaining_job_list: list,
                             pending_job_with_new_cutoff=dict, started=bool):
    number_of_solvers = len(remaining_job_list)
    n_seconds = 1
    done = False
    current_solver_list = remaining_job_list
    finished_solver_list = []

    while not done:
        # Ask the cluster for a list of all jobs which are currently running
        result = subprocess.run(['squeue', '--array', '--jobs', job_id],
                                capture_output=True, text=True)

        # If none of the jobs on the cluster are running then nothing has to done yet,
        # check back in n_seconds
        if ' R ' not in str(result):
            if len(result.stdout.strip().split('\n')) == 1:
                done = True  # No jobs are remaining
                break
            sjh.sleep(n_seconds)  # No jobs have started yet;
        # If the results are less than the number of solvers then this means that the are
        # finished solvers(+1 becuase of the header of results)
        elif len(result.stdout.strip().split('\n')) < (1 + number_of_solvers):
            if started is False:  # Log starting time
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")

                with open(logging_file, 'a+') as outfile:
                    fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
                    outfile.write(f'starting time of portfolio: {current_time}\n')

                started = True
            unfinished_solver_list = []

            for jobs in result.stdout.strip().split('\n'):
                jobid = jobs.strip().split()[0]

                if jobid.startswith(str(job_id)):
                    unfinished_solver_list.append(jobid[jobid.find('_')+1:])

            finished_solver_list = [item for item in current_solver_list
                                    if item not in unfinished_solver_list]

            for finished_solver in finished_solver_list:
                newCutoffTime = find_finished_time_finished_solver(solver_array_list,
                                                                   finished_solver)

                if newCutoffTime != '-1:00':
                    log_statement = (f'{str(finished_solver)} finished succesfully or '
                                     'has reached the cutoff time')
                    add_log_statement_to_file(logging_file, log_statement,
                                              str(newCutoffTime))
                    logging_file2 = logging_file[:logging_file.rfind('.')] + r'2.txt'
                    log_computation_time(logging_file2, finished_solver, newCutoffTime)

            done = True
        # No jobs have finished but some jobs are running
        else:
            if started is False:  # Log starting time
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")

                with open(logging_file, 'a+') as outfile:
                    fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
                    outfile.write(f'starting time of portfolio: {current_time}\n')

                started = True

            sjh.sleep(n_seconds)
            current_solver_list = []

            # Check if the running jobs are from a portfolio which contain an already
            # finished solver
            for jobs in result.stdout.strip().split('\n'):
                jobid = jobs.strip().split()[0]
                jobtime = jobs.strip().split()[5]
                jobstatus = jobs.strip().split()[4]

                # If option extended is used some jobs are not directly cancelled to
                # allow all jobs to compute for at least the same running time.
                if (sgh.settings.get_paraport_process_monitoring() ==
                        ProcessMonitoring.EXTENDED):
                    if jobid in pending_job_with_new_cutoff and jobstatus == 'R':
                        # Job is in a portfolio with a solver that already has finished
                        # and has to be cancelled in the finishing time of that solver
                        current_seconds = jobtime_to_seconds(jobtime)
                        sleep_time = (int(pending_job_with_new_cutoff[jobid])
                                      - int(current_seconds))
                        command_line = f'sleep {str(sleep_time)}; scancel {str(jobid)}'
                        add_log_statement_to_file(logging_file, command_line, jobtime)
                        pending_job_with_new_cutoff.pop(jobid)

                if(jobid.startswith(str(job_id))):
                    # add the job to the current solver list
                    current_solver_list.append(jobid[jobid.find('_')+1:])

    return finished_solver_list, pending_job_with_new_cutoff, started


def generate_parallel_portfolio_sbatch_script(parameters, num_jobs) -> Path:
    # Set script name and path
    sbatch_script_name = (f'parallel_portfolio_sbatch_shell_script_{str(num_jobs)}_'
                          f'{sbh.get_time_pid_random_string()}.sh')
    sbatch_script_path = Path(f'{sgh.sparkle_tmp_path}{sbatch_script_name}')

    # Set sbatch options
    job = 'run_parallel_portfolio'
    sbatch_options_list = ssh.get_sbatch_options_list(sbatch_script_path, num_jobs, job,
                                                      smac=False)
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    # Create job list
    job_params_list = parameters

    # Set srun options
    srun_options_str = f'--nodes=1 --ntasks=1 {ssh.get_slurm_srun_user_options_str()}'

    # Create target call
    target_call_str = ('Commands/sparkle_help/run_solvers_core.py --run-status-path '
                       'Tmp/SBATCH_Parallel_Portfolio_Jobs/')

    # Generate script
    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_path


def generate_SBATCH_job_list(solver_list, instance_path_list, num_jobs: int):
    # The function generates the parameters used in the SBATCH script of the portfolio
    parameters = list()
    new_num_jobs = num_jobs
    solver_array_list = []
    tmp_solver_instances = []
    performance_measure = sgh.settings.get_general_performance_measure()

    # Adds all the jobs of instances and their portfolio to the parameter list
    for instance_path in instance_path_list:
        for solver in solver_list:
            if " " in solver:
                solver_path, seed = solver.strip().split()
                solver_name = Path(solver_path).name
                tmp_solver_instances.append(f'{solver_name}_seed_')
                new_num_jobs = new_num_jobs + int(seed) - 1

                for instance in range(1, int(seed)+1):
                    commandline = (f' --instance {str(instance_path)} --solver '
                                   f'{str(solver_path)} --performance-measure '
                                   f'{performance_measure.name} --seed {str(instance)}')
                    parameters.append(str(commandline))
                    instance_name = Path(instance_path).name
                    solver_array_list.append(
                        f'{solver_name}_seed_{str(instance)}_{instance_name}')
            else:
                solver_path = Path(solver)
                solver_name = solver_path.name
                instance_name = Path(instance_path).name
                solver_array_list.append(f'{solver_name}_{instance_name}')
                commandline = (f' --instance {str(instance_path)} --solver '
                               f'{str(solver_path)} --performance-measure '
                               f'{performance_measure.name}')
                parameters.append(str(commandline))

    return (parameters, new_num_jobs, solver_array_list,
            list(dict.fromkeys(tmp_solver_instances)))


def handle_waiting_and_removal_process(instances: list, logging_file: str,
                                       job_id: str, solver_array_list: list,
                                       sbatch_script_path: Path, portfolio_size: int,
                                       remaining_job_list: list,
                                       finished_instances_dict: dict,
                                       pending_job_with_new_cutoff: dict,
                                       started: bool) -> bool:
    if len(remaining_job_list):
        print(f'c a job has ended, remaining jobs = {str(len(remaining_job_list))}')

    if finished_instances_dict == {}:
        for instance in instances:
            instance = sfh.get_last_level_directory_name(instance)
            finished_instances_dict[instance] = ['UNSOLVED', 0]

    for finished_solver_files in os.listdir('Performance_Data/Tmp_PaP/'):
        for instance in finished_instances_dict:
            if str(instance) in str(finished_solver_files):
                file_path = f'Performance_Data/Tmp_PaP/{str(finished_solver_files)}'

                with open(file_path, 'r') as infile:
                    content = infile.readlines()

                # A new instance is solved
                if (finished_instances_dict[instance][1] == float(0)):
                    if (float(content[2].strip()) >
                            float(sgh.settings.get_general_target_cutoff_time())):
                        print(f'c {str(instance)} has reached the cutoff time without '
                              'being solved.')
                        finished_instances_dict[instance][1] = float(content[2].strip())
                    else:
                        finished_instances_dict[instance][1] = float(content[2].strip())
                        print(f'c {str(instance)} has been solved in '
                              f'{str(content[2].strip())} seconds!')

                        for temp_files in os.listdir('Tmp/'):
                            temp_file_match = str(sfh.get_file_name(content[1].strip()))

                            if (temp_file_match in str(temp_files.strip()) and
                                    sfh.get_file_least_extension(str(temp_files.strip()))
                                    == 'rawres'):
                                rawres_file_path = 'Tmp/' + str(temp_files.strip())

                                with open(rawres_file_path, 'r') as rawres_file:
                                    raw_content = rawres_file.readlines()

                                nr_of_lines_raw_content = len(raw_content)

                                for lines in range(0, nr_of_lines_raw_content):
                                    if '\ts ' in raw_content[
                                            nr_of_lines_raw_content-lines-1]:
                                        results_line = raw_content[
                                            nr_of_lines_raw_content-lines-1]
                                        print('c result = ' + str(results_line[
                                            results_line.find('s')+2:].strip()))
                                        finished_instances_dict[instance][0] = str(
                                            results_line[
                                                results_line.find('s')+2:].strip())
                                        break

                # A solver has an improved performance time on an instance
                elif (float(finished_instances_dict[instance][1])
                        > float(content[2].strip())):
                    finished_instances_dict[instance][1] = float(content[2].strip())
                    print(f'c {str(instance)} has been solved with an improved solving '
                          f'time of {str(content[2].strip())} seconds!')

    # Monitors the running jobs waiting for a solver that finishes
    finished_jobs, pending_job_with_new_cutoff, started = wait_for_finished_solver(
        logging_file, job_id, solver_array_list, remaining_job_list,
        pending_job_with_new_cutoff, started)

    # Handles the updating of all jobs within the portfolios of which contain a finished
    # job
    remaining_job_list, pending_job_with_new_cutoff = cancel_remaining_jobs(
        logging_file, job_id, finished_jobs, portfolio_size, solver_array_list,
        pending_job_with_new_cutoff)

    # If there are still unfinished jobs recursively handle the remaining jobs.
    if len(remaining_job_list) > 0:
        handle_waiting_and_removal_process(instances, logging_file, job_id,
                                           solver_array_list, sbatch_script_path,
                                           portfolio_size, remaining_job_list,
                                           finished_instances_dict,
                                           pending_job_with_new_cutoff, started)

    return True


def run_parallel_portfolio(instances: list, portfolio_path: Path) -> bool:
    solver_list = sfh.get_solver_list_from_parallel_portfolio(portfolio_path)
    num_jobs = len(solver_list) * len(instances)

    # Makes SBATCH scripts for all individual solvers in a list
    parameters, num_jobs, solver_array_list, temp_solvers = generate_SBATCH_job_list(
        solver_list, instances, num_jobs)

    # Generates a SBATCH script which uses the created parameters
    sbatch_script_path = generate_parallel_portfolio_sbatch_script(parameters, num_jobs)

    # Runs the script and cancels the remaining scripts if a script finishes before the
    # end of the cutoff_time
    file_path_output1 = str(PurePath(sgh.sparkle_global_output_dir / slog.caller_out_dir
                            / "Log/logging.txt"))
    file_path_output2 = str(PurePath(sgh.sparkle_global_output_dir / slog.caller_out_dir
                            / "Log/logging2.txt"))
    sfh.create_new_empty_file(file_path_output1)
    sfh.create_new_empty_file(file_path_output2)

    try:
        command_name = CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO
        execution_dir = './'
        job_id = ssh.submit_sbatch_script(str(sbatch_script_path), command_name,
                                          execution_dir)

        if(sgh.settings.get_general_performance_measure() == PerformanceMeasure.RUNTIME):
            handle_waiting_and_removal_process(instances, file_path_output1, job_id,
                                               solver_array_list, sbatch_script_path,
                                               num_jobs/len(instances), [], {}, {},
                                               False)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")

            with open(file_path_output1, 'a+') as outfile:
                fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
                outfile.write(f'ending time of portfolio: {current_time}\n')

            # After all jobs have finished remove/extract the files in temp only needed
            # for the running of the portfolios.
            # remove_temp_files_unfinished_solvers(solver_array_list, sbatch_script_path,
            #                                      temp_solvers)
        else:
            done = False
            wait_cutoff_time = False
            n_seconds = 4

            while not done:
                # Ask the cluster for a list of all jobs which are currently running
                result = subprocess.run(['squeue', '--array', '--jobs', job_id],
                                        capture_output=True, text=True)

                # If none of the jobs on the cluster are running then nothing has to done
                # yet, check back in n_seconds
                if ' R ' not in str(result):
                    if len(result.stdout.strip().split('\n')) == 1:
                        done = True  # No jobs are remaining
                        break

                    sjh.sleep(n_seconds)  # No jobs have started yet;
                else:
                    # Wait until the last few seconds before checking often
                    if not wait_cutoff_time:
                        n_seconds = int(sgh.settings.get_general_target_cutoff_time())-6
                        sjh.sleep(n_seconds)
                        wait_cutoff_time = True
                        n_seconds = 1  # Start checking often

                    sjh.sleep(n_seconds)

        finished_instances_dict = {}

        for instance in instances:
            instance = sfh.get_last_level_directory_name(instance)
            finished_instances_dict[instance] = ['UNSOLVED', 0]

        for finished_solver_files in os.listdir('Performance_Data/Tmp_PaP/'):
            for instance in finished_instances_dict:
                if str(instance) in str(finished_solver_files):
                    file_path = (str('Performance_Data/Tmp_PaP/')
                                 + str(finished_solver_files))

                    with open(file_path, 'r') as infile:
                        content = infile.readlines()

                    # A new instance is solved
                    if (finished_instances_dict[instance][0] == 'UNSOLVED'):
                        finished_instances_dict[instance][1] = float(content[2].strip())
                        finished_instances_dict[instance][0] = 'SOLVED'
                    elif (float(finished_instances_dict[instance][1])
                            > float(content[2].strip())):
                        finished_instances_dict[instance][1] = float(content[2].strip())

        for instances in finished_instances_dict:
            if (finished_instances_dict[instances][0] == 'SOLVED'
                    and float(finished_instances_dict[instances][1]) > 0):
                # To filter out constraint files
                if 'e' not in str(finished_instances_dict[instances][1]):
                    print(f'c {str(instances)} was solved with a results: '
                          f'{str(finished_instances_dict[instances][1])}')
            else:
                print(f'c {str(instances)} was not solved in the given cutoff-time')
    except Exception as except_msg:
        print(except_msg)

        return False

    return True
