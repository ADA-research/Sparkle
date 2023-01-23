#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for job execution and maintenance."""

from pathlib import Path
import subprocess
import csv
import time
import sys

try:
    from sparkle_help.sparkle_command_help import CommandName
    from sparkle_help.sparkle_command_help import COMMAND_DEPENDENCIES
except ImportError:
    from sparkle_command_help import CommandName
    from sparkle_command_help import COMMAND_DEPENDENCIES


__active_jobs_path = Path("Output/active_jobs.csv")
__active_jobs_csv_header = ["job_id", "command"]


def get_num_of_total_job_from_list(list_jobs):
    """Return the total number of jobs."""
    num = 0
    for i in range(0, len(list_jobs)):
        num += len(list_jobs[i][1])
    return num


def expand_total_job_from_list(list_jobs):
    """Transform a given job list."""
    total_job_list = []
    for i in range(0, len(list_jobs)):
        first_item = list_jobs[i][0]
        second_item_list = list_jobs[i][1]
        len_second_item_list = len(second_item_list)
        for j in range(0, len_second_item_list):
            second_item = second_item_list[j]
            total_job_list.append([first_item, second_item])
    return total_job_list


def check_active_jobs_exist() -> bool:
    """Return whether there are any active jobs."""
    exist = False
    # Cleanup to make sure completed jobs are removed
    cleanup_active_jobs()
    jobs_list = get_active_job_ids()

    if len(jobs_list) > 0:
        exist = True

    return exist


def check_job_is_done(job_id: str) -> bool:
    """Check whether a job is done."""
    # TODO: Handle other cases than slurm when they are implemented
    done = False
    done = check_job_is_done_slurm(job_id)

    return done


# TODO: Move to sparkle_slurm_help
def check_job_is_done_slurm(job_id: str) -> bool:
    """Check whether a Slurm job is done and update the active job file as needed."""
    done = False
    result = subprocess.run(["squeue", "-j", job_id], capture_output=True, text=True)

    id_not_found_str = "slurm_load_jobs error: Invalid job id specified"

    # If the ID is invalid, the job is (long) done
    if result.stderr.strip() == id_not_found_str:
        done = True
    # If there is only one line (the squeue header) without a list of jobs,
    # the job is done
    elif len(result.stdout.strip().split("\n")) < 2:
        done = True

    if done:
        delete_active_job(job_id)

    return done


def sleep(n_seconds: int):
    """Sleep for a given number of seconds."""
    if n_seconds > 0:
        time.sleep(n_seconds)

    return


# Wait until all dependencies of the command to run are completed
def wait_for_dependencies(command_to_run: CommandName):
    """Wait for all dependencies of a given command to finish executing."""
    dependencies = COMMAND_DEPENDENCIES[command_to_run]
    dependent_job_ids = []

    for dependency in dependencies:
        dependent_job_ids.extend(get_job_ids_for_command(dependency))

    for job_id in dependent_job_ids:
        wait_for_job(job_id)

    return


def wait_for_job(job_id: str):
    """Wait for a given job to finish executing."""
    done = check_job_is_done(job_id)
    n_seconds = 10

    while not done:
        sleep(n_seconds)
        done = check_job_is_done(job_id)

    print("Job with ID", job_id, "done!", flush=True)

    return


def wait_for_all_jobs():
    """Wait for all active jobs to finish executing."""
    remaining_jobs = cleanup_active_jobs()
    n_seconds = 10
    print("Waiting for", remaining_jobs, "jobs...", flush=True)

    while remaining_jobs > 0:
        sleep(n_seconds)
        remaining_jobs = cleanup_active_jobs()

    print("All jobs done!")

    return


def write_active_job(job_id: str, command: CommandName) -> None:
    """Write a given command and job ID combination to the active jobs file."""
    path = __active_jobs_path

    # Write header if the file does not exist
    if not path.is_file():
        with open(path, "w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(__active_jobs_csv_header)

    # Write job row if it did not finish yet
    if not check_job_is_done(job_id) and not check_job_exists(job_id, command):
        with open(path, "a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([job_id, command.name])

    return


def check_job_exists(job_id: str, command: CommandName) -> bool:
    """Check whether a job for a given command and ID combination exists."""
    jobs_list = read_active_jobs()

    for job in jobs_list:
        if job["job_id"] == job_id and job["command"] == command.name:
            return True

    return False


def read_active_jobs() -> list[dict[str, str]]:
    """Read active jobs from file and return them as list of [job_id, command] dicts."""
    jobs = []
    path = __active_jobs_path
    try:
        with open(path, "r", newline="") as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                jobs.append(row)
    except EnvironmentError:
        print("No jobs yet submitted to wait for ! ")
        sys.exit()
    return jobs


def get_active_job_ids() -> list[str]:
    """Return the IDs of all active jobs."""
    job_ids = []
    jobs_list = read_active_jobs()

    for job in jobs_list:
        job_ids.append(job["job_id"])

    return job_ids


def get_job_ids_for_command(command: CommandName) -> list[str]:
    """Return the IDs of active jobs for a given command."""
    jobs_list = read_active_jobs()
    job_ids = []

    for job in jobs_list:
        if job["command"] == command.name:
            job_ids.append(job["job_id"])

    return job_ids


def delete_active_job(job_id: str):
    """Remove the specified job from the active jobs file."""
    delete_active_jobs([job_id])

    return


def delete_active_jobs(job_ids: list[str]):
    """Remove the specified jobs from the active jobs file."""
    inpath = __active_jobs_path
    outpath = __active_jobs_path.with_suffix(".tmp")

    with (open(inpath, "r", newline="") as infile,
          open(outpath, "w", newline="") as outfile):
        writer = csv.writer(outfile)
        writer.writerow(__active_jobs_csv_header)
        reader = csv.DictReader(infile)

        for row in reader:
            # Only keep entries with a job ID other than the one to be removed
            if row["job_id"] not in job_ids:
                writer.writerow([row["job_id"], row["command"]])

    # Replace the old CSV
    outpath.rename(inpath)

    return


def cleanup_active_jobs() -> int:
    """Remove completed jobs from the active jobs file, return the number remaining."""
    jobs_list = read_active_jobs()
    delete_ids = []
    remaining_jobs = 0

    for job in jobs_list:
        job_id = job["job_id"]

        if check_job_is_done(job_id):
            delete_ids.append(job_id)
        else:
            remaining_jobs += 1

    delete_active_jobs(delete_ids)

    return remaining_jobs
