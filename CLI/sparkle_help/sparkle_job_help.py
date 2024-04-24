#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for job execution and maintenance."""
from __future__ import annotations

from pathlib import Path
import time

from runrunner import SlurmRun
from runrunner.base import Status

from CLI.help.sparkle_command_help import CommandName
from CLI.help.sparkle_command_help import COMMAND_DEPENDENCIES
from CLI.sparkle_help import sparkle_global_help as sgh


def get_num_of_total_job_from_list(list_jobs: list) -> int:
    """Return the total number of jobs.

    Args:
      list_jobs: List of jobs. Each entry is a list itself where the type
      of the entries depends on the job type (e.g., feature computation job).

    Returns:
      The total number of jobs.
    """
    num = 0
    for job in list_jobs:
        num += len(job[1])
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
    for job in list_jobs:
        first_item = job[0]
        for second_item in job[1]:
            total_job_list.append([first_item, second_item])
    return total_job_list


def check_job_is_done(job_id: str) -> bool:
    """Check whether a job is done.

    Args:
      job_id: String job identifier.

    Returns:
      Boolean indicating whether the job has finished.
    """
    # TODO: Handle other cases than slurm when they are implemented
    jobs = get_runs_from_file()
    for j in jobs:
        if j.run_id == job_id:
            if j.status == Status.COMPLETED:
                return True
            return False
    # Should this not be an error? Job not found
    return False


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


def wait_for_job(job: str | SlurmRun) -> None:
    """Wait for a given Slurm job to finish executing.

    Args:
      job: String job identifier.
    """
    if isinstance(job, str):
        job = find_run(job)
    job.wait()

    print(f"Job with ID {job.run_id} done!", flush=True)


def find_run(job_id: str, path: Path = Path(sgh.sparkle_tmp_path))\
        -> SlurmRun:
    """Retrieve a specific RunRunner Slurm run using the job_id.

    Args:
        job_id: String identifier of the job
        path: The Path where to look for the stored jobs. Sparkle's Tmp path by default.

    Returns:
        The SlurmRun with the matching run_id, None if no match.
    """
    for run in get_runs_from_file(path=path):
        if run.run_id == job_id:
            return run
    return None


def get_runs_from_file(path: Path = Path(sgh.sparkle_tmp_path))\
        -> list[SlurmRun]:
    """Retrieve all run objects from file storage.

    Args:
        path: Path object where to look for the files.

    Returns:
        List of all found SlumRun objects.
    """
    runs, ignores = [], []
    if not path.exists():
        return runs
    for file in path.iterdir():
        if file.suffix == ".json":
            # TODO: RunRunner should be adapted to have more general methods for runs
            # So this method can work for both local and slurm
            try:
                run_obj = SlurmRun.from_file(file)
                runs.append(run_obj)
            except Exception:
                # TODO: When we have a more sophisticated version of managing/
                # remembering runs, we might as well remember which files to ignore.
                ignores.append(file)
    return runs


def get_running_jobs() -> list[SlurmRun]:
    """Returns all waiting or running jobs."""
    return [run for run in get_runs_from_file()
            if run.status == Status.WAITING or run.status == Status.RUNNING]


def wait_for_all_jobs() -> None:
    """Wait for all active jobs to finish executing."""
    running_jobs = get_running_jobs()
    prev_jobs = len(running_jobs) + 1
    while len(running_jobs) > 0:
        if len(running_jobs) < prev_jobs:
            print(f"Waiting for {len(running_jobs)} jobs...", flush=True)
        time.sleep(10.0)
        prev_jobs = len(running_jobs)
        running_jobs = [run for run in running_jobs
                        if run.status == Status.WAITING or run.status == Status.RUNNING]

    print("All jobs done!")


def get_active_jobs() -> list[dict[str, str, str]]:
    """Get active jobs from file and return them as list of [job_id, command, status].

    Returns:
      List of dictionaries with string keys and dict values.
    """
    jobs = get_running_jobs()
    return [{"job_id": j.run_id, "command": j.name, "status": j.status} for j in jobs]


def get_job_ids_for_command(command: CommandName) -> list[str]:
    """Return the IDs of active jobs for a given command.

    Args:
      command: Command name.

    Returns:
      List of job IDs (in string format).
    """
    jobs_list = get_active_jobs()
    job_ids = []

    for job in jobs_list:
        if job["command"] == command.name:
            job_ids.append(job["job_id"])

    return job_ids
