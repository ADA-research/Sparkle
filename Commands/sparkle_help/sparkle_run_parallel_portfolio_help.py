#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a parallel portfolio."""

import shutil
import os
import subprocess
import datetime
import fcntl
import glob
import sys
from pathlib import Path
from pathlib import PurePath

from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_logging as slog
from Commands.sparkle_help import sparkle_job_help as sjh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure, ProcessMonitoring
from Commands.sparkle_help.sparkle_command_help import CommandName

from sparkle.slurm_parsing import SlurmBatch
import runrunner as rrr
from runrunner.base import Runner

import functools
print = functools.partial(print, flush=True)


def jobtime_to_seconds(jobtime: str) -> int:
    """Convert a jobtime string to an integer number of seconds.

    Args:
        jobtime: Running time of a job in squeue (Slurm) format.

    Returns:
        An int indicating the number of seconds.
    """
    seconds = int(sum(int(x) * 60 ** i for i, x in enumerate(
        reversed(jobtime.split(":")))))

    return seconds


def add_log_statement_to_file(log_file: str, line: str, jobtime: str) -> None:
    """Log the starting time, end time and job number to a given file.

    Args:
        log_file: Path to the log file.
        line: A str of the form "sleep {str(sleep_time)}; scancel {str(jobid)}"
        jobtime: Running time of a job in squeue (Slurm) format.
    """
    now = datetime.datetime.now()
    job_duration_seconds = jobtime_to_seconds(jobtime)
    job_running_time = datetime.timedelta(seconds=job_duration_seconds)

    if line.rfind(";") != -1:
        sleep_seconds = line[:line.rfind(";")]
        sleep_seconds = int(sleep_seconds[sleep_seconds.rfind(" ") + 1:])
        now = now + datetime.timedelta(seconds=sleep_seconds)
        job_running_time = job_running_time + datetime.timedelta(seconds=sleep_seconds)
        job_nr = line[line.rfind(";") + 2:]
    else:
        # TODO: Not sure what the intend of checking job numbers in this function was.
        # TODO: Writing a warning as job_nr for now, since this is a logging function,
        # TODO: this issue should be of no harm to the functionality.
        job_nr = "WARNING: No job_nr found in function add_log_statement_to_file"

    current_time = now.strftime("%H:%M:%S")
    job_starting_time = now - job_running_time
    start_time_formatted = job_starting_time.strftime("%H:%M:%S")

    with Path(log_file).open("a+") as outfile:
        fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
        outfile.write(f"starting time: {start_time_formatted} end time: {current_time} "
                      f"job number: {job_nr}\n")


def log_computation_time(log_file: str, job_nr: str, job_duration: str) -> None:
    """Log the job number and job duration.

    Args:
        log_file: Path to the log file.
        job_nr: Job number as str.
        job_duration: Job duration as str.
    """
    if ":" in job_duration:
        job_duration = str(jobtime_to_seconds(job_duration))

    if "_" in job_nr:
        job_nr = job_nr[job_nr.rfind("_") + 1:]

    with Path(log_file).open("a+") as outfile:
        fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
        outfile.write(f"{job_nr}:{job_duration}\n")


def check_sbatch_for_errors(sbatch_script_path: Path) -> None:
    """Check sbatch files for errors. If found, stop execution.

    Args:
        sbatch_script_path: Path to the sbatch script.
    """
    error_lines = [ \
        # ERROR: [...] not found [...]
        "ERROR: "]

    sbatch_script_path.with_suffix(".txt")

    # Find lines containing an error
    with sbatch_script_path.open("r") as infile:
        for current_line in infile:
            for error in error_lines:
                if error in current_line:
                    print(f"ERROR detected in {sbatch_script_path}\n"
                          f"involving {current_line}\n"
                          "Stopping execution!")
                    sys.exit(-1)


def remove_temp_files_unfinished_solvers(solver_instance_list: list[str],
                                         sbatch_script_path: Path,
                                         temp_solvers: list[str]) -> None:
    """Remove temporary files and directories, and move result files.

    Args:
        solver_instance_list: List of solver instances.
        sbatch_script_path: Path to the sbatch script.
        temp_solvers: A list of temporary solvers.
    """
    tmp_dir = sgh.sparkle_tmp_path

    # Removes statusinfo files
    for solver_instance in solver_instance_list:
        commandline = (f"rm -rf {sgh.pap_sbatch_tmp_path}/"
                       f"{solver_instance}*")
        os.system(commandline)

    # Validate no known errors occurred in the sbatch
    check_sbatch_for_errors(sbatch_script_path)

    # Removes the generated sbatch files
    commandline = f"rm -rf {sbatch_script_path}*"
    os.system(commandline)

    # Removes the directories generated for the solver instances
    for temp_solver in temp_solvers:
        for directories in os.listdir(tmp_dir):
            directories_path = f"{tmp_dir}{directories}"

            for solver_instance in solver_instance_list:
                if (Path(directories_path).is_dir()
                        and directories.startswith(
                            solver_instance[:len(temp_solver) + 1])):
                    shutil.rmtree(directories_path)

    # Removes or moves all remaining files
    list_of_paths = os.listdir(tmp_dir)
    to_be_deleted = list()
    to_be_moved = list()

    for file in list_of_paths:
        file_path = f"{tmp_dir}{file}"

        if not Path(file_path).is_dir():
            tmp_file = file[:file.rfind(".")]
            tmp_file = f"{tmp_file}.val"

            if tmp_file not in list_of_paths:
                to_be_deleted.append(file)
            else:
                to_be_moved.append(file)

    for file in to_be_deleted:
        commandline = f"rm -rf {tmp_dir}{file}"
        os.system(commandline)

    for file in to_be_moved:
        if ".val" in file:
            path_from = f"{tmp_dir}{file}"
            path_to = f"{str(sgh.pap_performance_data_tmp_path)}/{file}"

            try:
                shutil.move(path_from, path_to)
            except shutil.Error:
                print(f"the {str(sgh.pap_performance_data_tmp_path)} directory already "
                      "contains a file with the same name, it will be skipped")

            commandline = f"rm -rf {path_from}"
            os.system(commandline)


def find_finished_time_finished_solver(solver_instance_list: list[str],
                                       finished_job_array_nr: str) -> str:
    """Return the time at which a solver finished.

    Args:
        solver_instance_list: List of solver instances.
        finished_job_array_nr: The Slurm array number of the finished job.

    Returns:
        A formatted string that represents the finishing time of a solver.
    """
    # If there is a solver that ended but did not make a result file this means that it
    # was manually cancelled or it gave an error the template will ensure that all
    # solver on that instance will be cancelled.
    time_in_format_str = "-1:00"
    solutions_dir = f"{str(sgh.pap_performance_data_tmp_path)}/"
    results = sfh.get_list_all_result_filename(solutions_dir)

    for result in results:
        if "_" in finished_job_array_nr:
            finished_job_array_nr = finished_job_array_nr[
                finished_job_array_nr.rfind("_") + 1:]

        if result.startswith(solver_instance_list[int(finished_job_array_nr)]):
            result_file_path = solutions_dir + result

            with Path(result_file_path).open("r") as result_file:
                result_lines = result_file.readlines()
                result_time = int(float(result_lines[2].strip()))
                time_in_format_str = str(datetime.timedelta(seconds=result_time))

    return time_in_format_str


def cancel_remaining_jobs(logging_file: str, job_id: str,
                          finished_solver_id_list: list[str],
                          portfolio_size: int, solver_instance_list: list[str],
                          pending_job_with_new_cutoff: dict[str, int] = {}
                          ) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Cancel jobs past the cutoff, update cutoff time for jobs that should continue.

    Args:
        logging_file: Path to the logging file.
        job_id: Job ID as str.
        finished_solver_id_list: List of str typed job IDs of finished solvers.
        portfolio_size: Size of parallel algorithm portfolio.
        solver_instance_list: List of solver instances as str.
        pending_job_with_new_cutoff: Dict with jobid str as key, and cutoff_seconds int
            as value. Defaults to an empty dict.

    Returns:
        remaining_jobs: A dict containing a jobid str as key, and a (two
            element) list of str with the jobtime and jobstatus.
        pending_job_with_new_cutoff: A dict of pending jobs with new cutoff time
            (jobid str as key, and cutoff_seconds int as value).
    """
    # Find all job_array_numbers that are currently running
    # This is specific to Slurm
    result = subprocess.run(["squeue", "--array", "--jobs", job_id,
                             "--format", "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"],
                            capture_output=True, text=True)
    remaining_jobs = {}

    for jobs in result.stdout.strip().split("\n"):
        jobid = jobs.strip().split()[0]  # First squeue column is JOBID
        jobtime = jobs.strip().split()[5]  # Sixth squeue column is TIME
        jobstatus = jobs.strip().split()[4]  # Fifth squeue column is ST (status)

        # If option extended is used some jobs are not directly cancelled to allow all
        # jobs to compute for at least the same running time.
        if (sgh.settings.get_paraport_process_monitoring()
                == ProcessMonitoring.EXTENDED):
            # If a job in a portfolio with a finished solver starts running its timelimit
            # needs to be updated.
            if jobid in pending_job_with_new_cutoff and jobstatus == "R":
                current_seconds = jobtime_to_seconds(jobtime)
                sleep_time = pending_job_with_new_cutoff[jobid] - current_seconds
                command_line = f"sleep {str(sleep_time)}; scancel {str(jobid)}"
                add_log_statement_to_file(logging_file, command_line, jobtime)
                pending_job_with_new_cutoff.pop(jobid)

        if jobid.startswith(str(job_id)):
            remaining_jobs[jobid] = [jobtime, jobstatus]

    for job in remaining_jobs:
        # Update all jobs in the same array segment as the finished job with its
        # finishing time
        for finished_solver_id in finished_solver_id_list:
            # if job in the same array segment
            if (int(int(job[job.find("_") + 1:]) / portfolio_size)
                    == int(int(finished_solver_id) / portfolio_size)):
                # If option extended is used some jobs are not directly cancelled to
                # allow all jobs to compute for at least the same running time.
                if (sgh.settings.get_paraport_process_monitoring()
                        == ProcessMonitoring.EXTENDED):
                    # Update the cutofftime of the to be cancelled job, if job if
                    # already past that it automatically stops.
                    new_cutoff_time = find_finished_time_finished_solver(
                        solver_instance_list, finished_solver_id)
                    current_seconds = jobtime_to_seconds(remaining_jobs[job][0])
                    cutoff_seconds = jobtime_to_seconds(new_cutoff_time)
                    actual_cutofftime = sgh.settings.get_general_target_cutoff_time()

                    if (remaining_jobs[job][1] == "R"
                            and int(cutoff_seconds) < int(actual_cutofftime)):
                        if int(current_seconds) < int(cutoff_seconds):
                            sleep_time = int(cutoff_seconds) - int(current_seconds)
                            command_line = f"sleep {str(sleep_time)}; scancel {str(job)}"
                            add_log_statement_to_file(logging_file, command_line,
                                                      remaining_jobs[job][0])
                        else:
                            command_line = f"scancel {str(job)}"
                            add_log_statement_to_file(logging_file, command_line,
                                                      remaining_jobs[job][0])
                            logging_file2 = (
                                f'{logging_file[:logging_file.rfind(".")]}2.txt')
                            log_computation_time(logging_file2, job, cutoff_seconds)
                        # Shell is needed for admin rights to do scancel
                        subprocess.Popen(command_line, shell=True)  # noqa # nosec
                    else:
                        pending_job_with_new_cutoff[job] = cutoff_seconds
                else:
                    command_line = f"scancel {str(job)}"
                    add_log_statement_to_file(logging_file, command_line,
                                              remaining_jobs[job][0])
                    logging_file2 = logging_file[:logging_file.rfind(".")] + "2.txt"
                    log_computation_time(logging_file2, job, "-1")
                    # Shell is needed for admin rights to do scancel
                    subprocess.Popen(command_line, shell=True)  # noqa # nosec

    return remaining_jobs, pending_job_with_new_cutoff


def wait_for_finished_solver(
        logging_file: str,
        job_id: str,
        solver_instance_list: list[str],
        remaining_job_dict: dict[str, list[str]],
        pending_job_with_new_cutoff: dict[str, int],
        started: bool,
        portfolio_size: int) -> tuple[list[str], dict[str, int], bool]:
    """Wait for a solver to finish, then return which finished and which may still run.

    Args:
        logging_file: Path to the logging file.
        job_id: Job ID as string.
        solver_instance_list: List of solver instances.
        remaining_job_dict: Dict of remaining jobs (jobid str as key, and a list of str
            as value).
        pending_job_with_new_cutoff: Dict of pending jobs with new cutoff time
            (jobid str as key, and cutoff_seconds int as value).
        started: Boolean indicating whether the portfolio has started running.
        portfolio_size: Size of the portfolio.

    Returns:
        finished_solver_list: A list of str typed job IDs of finished solvers.
        pending_job_with_new_cutoff: A dict with jobid str as key, and cutoff_seconds int
            as value.
        started: A bool indicating whether the PAP (parallel algorithm portfolio) has
            started running.
    """
    number_of_solvers = len(remaining_job_dict) if remaining_job_dict else portfolio_size
    n_seconds = 1
    done = False
    # TODO: Fix weird situation. This starts as dict, later becomes a list...
    current_solver_list = remaining_job_dict
    finished_solver_list = list()

    while not done:
        # Ask the cluster for a list of all jobs which are currently running
        result = subprocess.run(["squeue", "--array", "--jobs", job_id,
                                 "--format", "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"],
                                capture_output=True, text=True)

        # If none of the jobs on the cluster are running then nothing has to done yet,
        # check back in n_seconds
        if " R " not in str(result):
            if len(result.stdout.strip().split("\n")) == 1:
                done = True  # No jobs are remaining
                break

            sjh.sleep(n_seconds)  # No jobs have started yet;
        # If the results are less than the number of solvers then this means that there
        # are finished solvers(+1 becuase of the header of results)
        elif len(result.stdout.strip().split("\n")) < (1 + number_of_solvers):
            if started is False:  # Log starting time
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")

                with Path(logging_file).open("a+") as outfile:
                    fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
                    outfile.write(f"starting time of portfolio: {current_time}\n")

                started = True

            unfinished_solver_list = list()

            for jobs in result.stdout.strip().split("\n"):
                jobid = jobs.strip().split()[0]

                if jobid.startswith(job_id):
                    unfinished_solver_list.append(jobid[jobid.find("_") + 1:])

            finished_solver_list = [item for item in current_solver_list
                                    if item not in unfinished_solver_list]

            for finished_solver in finished_solver_list:
                new_cutoff_time = find_finished_time_finished_solver(
                    solver_instance_list, finished_solver)

                if new_cutoff_time != "-1:00":
                    log_statement = (f"{finished_solver} finished succesfully or "
                                     "has reached the cutoff time")
                    add_log_statement_to_file(logging_file, log_statement,
                                              str(new_cutoff_time))
                    logging_file2 = logging_file[:logging_file.rfind(".")] + r"2.txt"
                    log_computation_time(logging_file2, finished_solver, new_cutoff_time)

            done = True
        # No jobs have finished but some jobs are running
        else:
            if started is False:  # Log starting time
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")

                with Path(logging_file).open("a+") as outfile:
                    fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
                    outfile.write(f"starting time of portfolio: {current_time}\n")

                started = True

            sjh.sleep(n_seconds)
            current_solver_list = list()

            # Check if the running jobs are from a portfolio which contain an already
            # finished solver
            for jobs in result.stdout.strip().split("\n"):
                jobid = jobs.strip().split()[0]
                jobtime = jobs.strip().split()[5]
                jobstatus = jobs.strip().split()[4]

                # If option extended is used some jobs are not directly cancelled to
                # allow all jobs to compute for at least the same running time.
                if (sgh.settings.get_paraport_process_monitoring()
                        == ProcessMonitoring.EXTENDED):
                    if jobid in pending_job_with_new_cutoff and jobstatus == "R":
                        # Job is in a portfolio with a solver that already has finished
                        # and has to be cancelled in the finishing time of that solver
                        current_seconds = jobtime_to_seconds(jobtime)
                        sleep_time = pending_job_with_new_cutoff[jobid] - current_seconds
                        command_line = f"sleep {str(sleep_time)}; scancel {str(jobid)}"
                        add_log_statement_to_file(logging_file, command_line, jobtime)
                        pending_job_with_new_cutoff.pop(jobid)

                if (jobid.startswith(job_id)):
                    # add the job to the current solver list
                    current_solver_list.append(jobid[jobid.find("_") + 1:])

    return finished_solver_list, pending_job_with_new_cutoff, started


def generate_parallel_portfolio_sbatch_script(parameters: list[str],
                                              num_jobs: int) -> Path:
    """Generate an sbatch script for the PAP (parallel algorithm portfolio).

    Args:
        parameters: List of str parameters for the Slurm batch job.
        num_jobs: Number of jobs.

    Returns:
        Path to the generated sbatch script.
    """
    # Set script name and path
    sbatch_script_name = (f"parallel_portfolio_sbatch_shell_script_{str(num_jobs)}_"
                          f"{sbh.get_time_pid_random_string()}.sh")
    sbatch_script_path = Path(f"{sgh.sparkle_tmp_path}{sbatch_script_name}")

    # Set sbatch options
    job = "run_parallel_portfolio"
    sbatch_options_list = ssh.get_sbatch_options_list(sbatch_script_path, num_jobs, job,
                                                      smac=False)
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    # Create job list
    job_params_list = parameters

    # Set srun options
    srun_options_str = f"--nodes=1 --ntasks=1 {ssh.get_slurm_srun_user_options_str()}"

    # Create target call
    target_call_str = ("Commands/sparkle_help/run_solvers_core.py --run-status-path "
                       f"{str(sgh.pap_sbatch_tmp_path)}")

    # Generate script
    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_path


def generate_sbatch_job_list(
        solver_list: list[str],
        instance_path_list: list[str],
        num_jobs: int) -> tuple[list[str], int, list[str], list[str]]:
    """Generate a list of jobs to be executed in the sbatch script.

    Args:
        solver_list: List of solvers.
        instance_path_list: List of instance paths.
        num_jobs: Number of jobs.

    Returns:
        A list of parameters used in the sbatch script.
        Number of new jobs.
        A list of solver instances.
        A list of temp solver instances.
    """
    # The function generates the parameters used in the SBATCH script of the portfolio
    parameters = list()
    new_num_jobs = num_jobs
    solver_instance_list = list()
    tmp_solver_instances = list()
    performance_measure = sgh.settings.get_general_performance_measure()

    # Adds all the jobs of instances and their portfolio to the parameter list
    for instance_path in instance_path_list:
        for solver in solver_list:
            if " " in solver:
                solver_path, seed = solver.strip().split()
                solver_name = Path(solver_path).name
                tmp_solver_instances.append(f"{solver_name}_seed_")
                new_num_jobs = new_num_jobs + int(seed) - 1

                for instance in range(1, int(seed) + 1):
                    commandline = (f"--instance {str(instance_path)} --solver "
                                   f"{str(solver_path)} --performance-measure "
                                   f"{performance_measure.name} --seed {str(instance)}")
                    parameters.append(commandline)
                    instance_name = Path(instance_path).name
                    solver_instance_list.append(
                        f"{solver_name}_seed_{str(instance)}_{instance_name}")
            else:
                solver_path = Path(solver)
                solver_name = solver_path.name
                instance_name = Path(instance_path).name
                solver_instance_list.append(f"{solver_name}_{instance_name}")
                commandline = (f"--instance {str(instance_path)} --solver "
                               f"{str(solver_path)} --performance-measure "
                               f"{performance_measure.name}")
                parameters.append(commandline)

    temp_solvers = list(dict.fromkeys(tmp_solver_instances))

    return (parameters, new_num_jobs, solver_instance_list, temp_solvers)


def handle_waiting_and_removal_process(
        instances: list[str],
        logging_file: str,
        job_id: str,
        solver_instance_list: list[str],
        sbatch_script_path: Path,
        portfolio_size: int,
        remaining_job_dict: dict[str, list[str]] = None,
        finished_instances_dict: dict[str, list[str, int]] = None,
        pending_job_with_new_cutoff: dict[str, int] = None,
        started: bool = False) -> bool:
    """Wait for solvers to finish running, and clean up after them.

    Args:
        instances: A list of instances.
        logging_file: Path to the logging file.
        job_id: Job ID as string.
        solver_instance_list: A list of solver instances.
        sbatch_script_path: Path to sbatch script.
        portfolio_size: Size of the portfolio.
        remaining_job_dict: A dictionary of remaining jobs. Defaults to None.
        finished_instances_dict: A dictionary of finished instances. Defaults to None.
        pending_job_with_new_cutoff: A dictionary of pending jobs with new cutoff time.
            Defaults to None.
        started: A boolean value indicating whether the process has started. Defaults to
            False.

    Returns:
        True on success, may stop program execution early for failure.
    """
    if remaining_job_dict is None:
        remaining_job_dict = dict()

    if finished_instances_dict is None:
        finished_instances_dict = {}

    if pending_job_with_new_cutoff is None:
        pending_job_with_new_cutoff = {}

    if len(remaining_job_dict) > 0:
        print(f"A job has ended, remaining jobs = {str(len(remaining_job_dict))}")

    if finished_instances_dict == {}:
        for instance in instances:
            instance = sfh.get_last_level_directory_name(instance)
            finished_instances_dict[instance] = ["UNSOLVED", 0]

    perf_data_tmp_path = sgh.pap_performance_data_tmp_path

    # For each finished instance
    for instance in finished_instances_dict:
        # Only look at solvers for this instance
        current_sol_inst_list = [si for si in solver_instance_list if instance in si]
        # Check results for each solver
        for solver_instance in current_sol_inst_list:
            finished_solver_files = glob.glob(f"{str(perf_data_tmp_path)}/*"
                                              f"{solver_instance}*result")

            # If there is more than one result file for this solver-instance combination
            # something went wrong (probably during cleanup).
            if len(finished_solver_files) > 1:
                print(f"ERROR: {str(len(finished_solver_files))} result files found for"
                      f" {solver_instance} while there should be only one!")
                sys.exit()

            for finished_solver_file in finished_solver_files:
                file_path = finished_solver_file

                with Path(file_path).open("r") as infile:
                    content = infile.readlines()

                solving_time = float(content[2].strip())

                # A new instance is solved
                if (finished_instances_dict[instance][1] == float(0)):
                    finished_instances_dict[instance][1] = solving_time

                    if (solving_time
                            > float(sgh.settings.get_general_target_cutoff_time())):
                        print(f"{str(instance)} has reached the cutoff time without "
                              "being solved.")
                    else:
                        print(f"{str(instance)} has been solved in "
                              f"{str(solving_time)} seconds!")

                        temp_files = glob.glob(f"{sgh.sparkle_tmp_path}{solver_instance}"
                                               f"*.rawres")

                        for rawres_file_path in temp_files:
                            with Path(rawres_file_path).open("r") as rawres_file:
                                raw_content = rawres_file.readlines()

                            nr_of_lines_raw_content = len(raw_content)

                            for lines in range(0, nr_of_lines_raw_content):
                                if "\ts " in raw_content[
                                        nr_of_lines_raw_content - lines - 1]:
                                    results_line = raw_content[
                                        nr_of_lines_raw_content - lines - 1]
                                    print("result = " + str(results_line[
                                        results_line.find("s") + 2:].strip()))
                                    finished_instances_dict[instance][0] = str(
                                        results_line[results_line.find("s") + 2:].strip()
                                    )
                                    break

                # A solver has an improved performance time on an instance
                elif (float(finished_instances_dict[instance][1]) > solving_time):
                    finished_instances_dict[instance][1] = solving_time
                    print(f"{str(instance)} has been solved with an improved solving "
                          f"time of {str(solving_time)} seconds!")
    
    # Monitors the running jobs waiting for a solver that finishes
    finished_solver_id_list, pending_job_with_new_cutoff, started = (
        wait_for_finished_solver(
            logging_file, job_id, solver_instance_list, remaining_job_dict,
            pending_job_with_new_cutoff, started, portfolio_size))

    # Handles the updating of all jobs within the portfolios of which contain a finished
    # job
    remaining_job_dict, pending_job_with_new_cutoff = cancel_remaining_jobs(
        logging_file, job_id, finished_solver_id_list, portfolio_size,
        solver_instance_list, pending_job_with_new_cutoff)

    # If there are still unfinished jobs recursively handle the remaining jobs.
    if len(remaining_job_dict) > 0:
        handle_waiting_and_removal_process(instances, logging_file, job_id,
                                           solver_instance_list, sbatch_script_path,
                                           portfolio_size, remaining_job_dict,
                                           finished_instances_dict,
                                           pending_job_with_new_cutoff, started)

    return True


def remove_result_files(instances: list[str]) -> None:
    """Remove existing results for given instances.

    Args:
        instances: List of instance names.
    """
    for instance in instances:
        instance = Path(instance).name
        cmd_line = f"rm -f {str(sgh.pap_performance_data_tmp_path)}/*_{instance}_*.*"
        os.system(cmd_line)
        cmd_line = f"rm -f {str(sgh.sparkle_tmp_path)}*_{instance}_*.*"
        os.system(cmd_line)


def run_parallel_portfolio(instances: list[str],
                           portfolio_path: Path,
                           run_on: Runner = Runner.SLURM) -> bool:
    """Run the parallel algorithm portfolio and return whether this was successful.

    Args:
        instances: List of instance names.
        portfolio_path: Path to the parallel portfolio.

    Returns:
        True if successful; False otherwise.
    """
    # Remove existing result files
    remove_result_files(instances)

    solver_list = sfh.get_solver_list_from_parallel_portfolio(portfolio_path)
    num_jobs = len(solver_list) * len(instances)

    # Makes SBATCH scripts for all individual solvers in a list
    parameters, num_jobs, solver_instance_list, temp_solvers = generate_sbatch_job_list(
        solver_list, instances, num_jobs)
    # Generates a SBATCH script which uses the created parameters
    sbatch_script_path = generate_parallel_portfolio_sbatch_script(parameters, num_jobs)

    # Run the script and cancel the remaining solvers if a solver finishes before the
    # end of the cutoff_time
    file_path_output1 = str(PurePath(sgh.sparkle_global_output_dir / slog.caller_out_dir
                            / "Log/logging.txt"))
    sfh.create_new_empty_file(file_path_output1)

    try:
        command_name = CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO
        execution_dir = "./"
        job_id = ""
        if run_on == Runner.SLURM:
            job_id = ssh.submit_sbatch_script(str(sbatch_script_path), command_name,
                                              execution_dir)
        else:
            # Remove the below if block once runrunner works satisfactorily
            if run_on == Runner.SLURM_RR:
                run_on = Runner.SLURM

            batch = SlurmBatch(sbatch_script_path)
            cmd_list = [f"{batch.cmd} {param}" for param in batch.cmd_params]

            run = rrr.add_to_queue(
                runner=run_on,
                cmd=cmd_list,
                name=command_name,
                path=execution_dir,
                sbatch_options=batch.sbatch_options,
                srun_options=batch.srun_options)
            
            if hasattr(run, "run_id"):
                job_id = run.run_id

            # Remove the below if block once runrunner works satisfactorily
            if run_on == Runner.SLURM_RR:
                run_on = Runner.SLURM

        # TODO: Should the IF statement below be considering local as well?
        # As running runtime based performance may be less relevant
        if ( run_on == Runner.SLURM and sgh.settings.get_general_performance_measure()
              == PerformanceMeasure.RUNTIME):
            handle_waiting_and_removal_process(instances, file_path_output1, job_id,
                                               solver_instance_list, sbatch_script_path,
                                               num_jobs / len(instances))
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")

            with Path(file_path_output1).open("a+") as outfile:
                fcntl.flock(outfile.fileno(), fcntl.LOCK_EX)
                outfile.write(f"ending time of portfolio: {current_time}\n")

            # After all jobs have finished remove/extract the files in temp only needed
            # for the running of the portfolios.
            remove_temp_files_unfinished_solvers(solver_instance_list,
                                                 sbatch_script_path,
                                                 temp_solvers)
        elif run_on == Runner.SLURM:
            done = False
            wait_cutoff_time = False
            n_seconds = 4

            while not done:
                # Ask the cluster for a list of all jobs which are currently running
                result = subprocess.run(["squeue", "--array",
                                         "--jobs", job_id,
                                         "--format",
                                         "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"],
                                        capture_output=True, text=True)

                # If none of the jobs on the cluster are running then nothing has to done
                # yet, check back in n_seconds
                if " R " not in str(result):
                    if len(result.stdout.strip().split("\n")) == 1:
                        done = True  # No jobs are remaining
                        break
                else:
                    # Wait until the last few seconds before checking often
                    if not wait_cutoff_time:
                        n_seconds = sgh.settings.get_general_target_cutoff_time() - 6
                        sjh.sleep(n_seconds)
                        wait_cutoff_time = True
                        n_seconds = 1  # Start checking often

                sjh.sleep(n_seconds)
        else:
            run.wait()

        finished_instances_dict = {}

        for instance in instances:
            instance = sfh.get_last_level_directory_name(instance)
            finished_instances_dict[instance] = ["UNSOLVED", 0]

        tmp_res_files = glob.glob(f"{str(sgh.pap_performance_data_tmp_path)}/*.result")
        for finished_solver_files in tmp_res_files:
            for instance in finished_instances_dict:
                if str(instance) in str(finished_solver_files):
                    file_path = f"{str(finished_solver_files)}"

                    with Path(file_path).open("r") as infile:
                        content = infile.readlines()

                    # A new instance is solved
                    if (finished_instances_dict[instance][0] == "UNSOLVED"):
                        finished_instances_dict[instance][1] = float(content[2].strip())
                        finished_instances_dict[instance][0] = "SOLVED"
                    elif (float(finished_instances_dict[instance][1])
                            > float(content[2].strip())):
                        finished_instances_dict[instance][1] = float(content[2].strip())

        for instances in finished_instances_dict:
            if (finished_instances_dict[instances][0] == "SOLVED"
                    and float(finished_instances_dict[instances][1]) > 0):
                # To filter out constraint files
                if "e" not in str(finished_instances_dict[instances][1]):
                    print(f"{str(instances)} was solved with the result: "
                          f"{str(finished_instances_dict[instances][1])}")
            else:
                print(f"{str(instances)} was not solved in the given cutoff-time.")
    except Exception as except_msg:
        import time
        time.sleep(8.0)
        print(except_msg)
        sys.exit(-1)
        return False
    return True
