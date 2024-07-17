#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for job execution and maintenance."""
from __future__ import annotations

from pathlib import Path
import time
import json

from runrunner.slurm import SlurmRun
from runrunner.base import Status
from tabulate import tabulate

from CLI.help.command_help import CommandName
from CLI.help.command_help import COMMAND_DEPENDENCIES
import global_variables as gv
from sparkle.platform.cli_types import VerbosityLevel, TEXT


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


def find_run(job_id: str, path: Path = gv.sparkle_tmp_path)\
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


def get_runs_from_file(path: Path = gv.sparkle_tmp_path)\
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


def get_dependencies(jobs: list[SlurmRun]) -> list[SlurmRun]:
    """Adds Dependencies. Should be removed once RunRunner provides this feature."""
    for job in jobs:
        with job.json_filepath.open() as file:
            data = json.load(file)
        if len(data["dependencies"]) > 0:
            job_ids = [dep["run_id"] for dep in data["dependencies"]]
        else:
            job_ids = []
        job.dependencies = job_ids
    return jobs


def clear_console_lines(lines: int) -> None:
    """Clears the last lines of the console."""
    # \033 is the escape character (ESC) in ASCII
    # [{lines}A is the escape sequence that moves the cursor up.
    print(f"\033[{lines}A", end="")
    # [J is the exape sequence that clears the console from the cursor down
    print("\033[J", end="")


def wait_for_all_jobs() -> None:
    """Wait for all active jobs to finish executing."""
    jobs = get_running_jobs()
    verbosity_setting = gv.settings.get_general_verbosity()
    running_jobs = jobs
    # Interval at which to refresh the table
    check_interval = gv.settings.get_general_check_interval()
    # If verbosity is quiet there is no need for further information
    if verbosity_setting == VerbosityLevel.QUIET:
        prev_jobs = len(running_jobs) + 1
        while len(running_jobs) > 0:
            if len(running_jobs) < prev_jobs:
                print(f"Waiting for {len(running_jobs)} jobs...", flush=True)
            time.sleep(check_interval)
            prev_jobs = len(running_jobs)
            running_jobs = [run for run in running_jobs
                            if run.status == Status.WAITING
                            or run.status == Status.RUNNING]

    # If verbosity is standard the command will print a table with relevant information
    elif verbosity_setting == VerbosityLevel.STANDARD:
        # Collect dependencies and partitions for each job
        jobs = get_dependencies(jobs)
        # Order in which to display the jobs
        priority = {Status.COMPLETED: 0, Status.RUNNING: 1, Status.WAITING: 2}
        while len(running_jobs) > 0:
            # Information to be printed to the table
            information = [["RunId", "Name", "Status", "Dependencies", "Finished Jobs"]]
            running_jobs = [run for run in running_jobs
                            if run.status == Status.WAITING
                            or run.status == Status.RUNNING]
            sorted_jobs = sorted(jobs, key=lambda job: priority[job.status])
            for job in sorted_jobs:
                # Count number of jobs that have finished
                finished_jobs_count = sum(1 for status in job.all_status
                                          if status == Status.COMPLETED)
                # Format job.status
                status_text = \
                    TEXT.format_text([TEXT.BOLD], job.status) \
                    if job.status == Status.RUNNING else \
                    (TEXT.format_text([TEXT.ITALIC], job.status)
                        if job.status == Status.COMPLETED else job.status)
                information.append(
                    [job.run_id,
                     job.name,
                     status_text,
                     "None" if len(job.dependencies) == 0
                        else ", ".join(job.dependencies),
                     f"{finished_jobs_count}/{len(job.all_status)}"])
            # Print the table
            table = tabulate(information, headers="firstrow", tablefmt="grid")
            print(table)
            time.sleep(check_interval)

            # Clears the table for the new table to be printed
            lines = table.count("\n") + 1
            clear_console_lines(lines)

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
