#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for job execution and maintenance."""

from pathlib import Path
import subprocess
import csv
import time
from enum import Enum

from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help.sparkle_command_help import COMMAND_DEPENDENCIES


class JobState(Enum):
    """enum for indicating different states of a job."""
    RUNNING = "RUNNING"
    DONE = "DONE"


__jobs_path = Path("Output/jobs.csv")
__jobs_csv_header = ["job_id", "command", "state"]


def get_num_of_total_job_from_list(list_jobs: list) -> int:
    """Return the total number of jobs.

    Args:
      list_jobs: List of jobs. Each entry is a list itself where the type
      of the entries depends on the job type (e.g., feature computation job).

    Returns:
      The total number of jobs.
    """
    num = 0
    for i in range(0, len(list_jobs)):
        num += len(list_jobs[i][1])
    return num


def expand_total_job_from_list(list_jobs: list) -> list:
    """Expand job list.

    Args:
      list_jobs: List of jobs. Each entry is a list itself where the type
      of the entries depends on the job type (e.g., feature computation job).

    Returns:
      Expanded job list.
    """
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
    # Cleanup to make sure completed jobs are removed
    cleanup_active_jobs()
    return len(get_active_job_ids()) > 0


def check_job_is_done(job_id: str) -> bool:
    """Check whether a job is done.

    Args:
      job_id: String job identifier.

    Returns:
      Boolean indicating whether the job has finished.
    """
    # TODO: Handle other cases than slurm when they are implemented
    return check_job_is_done_slurm(job_id)


# TODO: Move to sparkle_slurm_help
def check_job_is_done_slurm(job_id: str) -> bool:
    """Check whether a Slurm job is done and update the active job file as needed.

    Args:
      job_id: String job identifier.

    Returns:
      Boolean indicating whether the job has finished.
    """
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
        change_job_state(job_id)

    return done


def sleep(n_seconds: int) -> None:
    """Sleep for a given number of seconds.

    Args:
      n_seconds: The number of the system should sleep.
    """
    if n_seconds > 0:
        time.sleep(n_seconds)


# Wait until all dependencies of the command to run are completed
def wait_for_dependencies(command_to_run: CommandName) -> None:
    """Wait for all dependencies of a given command to finish executing.

    Args:
      command_to_run: Command name.
    """
    dependencies = COMMAND_DEPENDENCIES[command_to_run]
    dependent_job_ids = []

    for dependency in dependencies:
        dependent_job_ids.extend(get_job_ids_for_command(dependency))

    for job_id in dependent_job_ids:
        wait_for_job(job_id)


def wait_for_job(job_id: str) -> None:
    """Wait for a given job to finish executing.

    Args:
      job_id: String job identifier.
    """
    done = check_job_is_done(job_id)
    n_seconds = 10

    while not done:
        sleep(n_seconds)
        done = check_job_is_done(job_id)

    print("Job with ID", job_id, "done!", flush=True)


def wait_for_all_jobs() -> None:
    """Wait for all active jobs to finish executing."""
    remaining_jobs = cleanup_active_jobs()
    n_seconds = 10
    print("Waiting for", remaining_jobs, "jobs...", flush=True)

    while remaining_jobs > 0:
        sleep(n_seconds)
        remaining_jobs = cleanup_active_jobs()

    print("All jobs done!")


def write_active_job(job_id: str, command: CommandName) -> None:
    """Write a given command and job ID combination to the active jobs file.

    Args:
      job_id: String job identifier.
      command: Command name.
    """
    path = __jobs_path

    # Write header if the file does not exist
    if not path.is_file():
        with Path(path).open("w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(__jobs_csv_header)

    # Write job row if it did not finish yet
    if not check_job_is_done(job_id) and not check_job_exists(job_id, command):
        with Path(path).open("a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([job_id, command.name, JobState.RUNNING])

    return


def check_job_exists(job_id: str, command: CommandName) -> bool:
    """Check whether a job for a given command and ID combination exists.

    Args:
      job_id: String job identifier.
      command_to_run: Command name.

    Returns:
      Boolean indicating whether the respective command and ID combination
      exists.
    """
    jobs_list = read_active_jobs()

    for job in jobs_list:
        if job["job_id"] == job_id and job["command"] == command.name:
            return True

    return False


def read_active_jobs() -> list[dict[str, str, str]]:
    """Read active jobs from file and return them as list of [job_id, command, state].

    Returns:
      List of dictionaries with string keys and dict values.
    """
    jobs = []
    path = __jobs_path
    Path(path).touch(exist_ok=True)
    with Path(path).open("r", newline="") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            if row["state"] == JobState.RUNNING:
                jobs.append(row)
    return jobs


def get_active_job_ids() -> list[str]:
    """Return the IDs of all active jobs.

    Returns:
      List of job IDs (in string format).
    """
    job_ids = []
    jobs_list = read_active_jobs()

    for job in jobs_list:
        job_ids.append(job["job_id"])

    return job_ids


def get_job_ids_for_command(command: CommandName) -> list[str]:
    """Return the IDs of active jobs for a given command.

    Args:
      command_to_run: Command name.

    Returns:
      List of job IDs (in string format).
    """
    jobs_list = read_active_jobs()
    job_ids = []

    for job in jobs_list:
        if job["command"] == command.name:
            job_ids.append(job["job_id"])

    return job_ids


def change_job_state(job_id: str) -> None:
    """Changes the state of the specified job.

    Args:
      job_id: String job identifier.
    """
    change_job_states([job_id])


def change_job_states(job_ids: list[str]) -> None:
    """Change the state of the specified jobs.

    Args:
      job_ids: List of string job identifiers.
    """
    inpath = __jobs_path
    outpath = __jobs_path.with_suffix(".tmp")

    with (Path(inpath).open("r", newline="") as infile,
          Path(outpath).open("w", newline="") as outfile):
        writer = csv.writer(outfile)
        writer.writerow(__jobs_csv_header)
        reader = csv.DictReader(infile)

        for row in reader:
            # Only keep entries with a job ID other than the one to be removed
            if row["job_id"] not in job_ids:
                writer.writerow([row["job_id"], row["command"], JobState.DONE])

    # Replace the old CSV
    outpath.rename(inpath)


def cleanup_active_jobs() -> int:
    """Change the state of completed jobs to done.

    Returns:
      Number of active jobs (after changing the state of the completed jobs).
    """
    jobs_list = read_active_jobs()
    change_ids = []
    remaining_jobs = 0

    for job in jobs_list:
        job_id = job["job_id"]

        if check_job_is_done(job_id):
            change_ids.append(job_id)
        else:
            remaining_jobs += 1

    change_job_states(change_ids)

    return remaining_jobs
