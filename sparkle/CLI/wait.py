#!/usr/bin/env python3
"""Sparkle command to wait for one or more other commands to complete execution."""
import sys
import signal
import time
import argparse
from pathlib import Path

from runrunner.slurm import SlurmRun
from runrunner.base import Status
from tabulate import tabulate

from sparkle.platform.cli_types import VerbosityLevel, TEXT
from sparkle.CLI.help import logging
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.JobIDsArgument.names, **ac.JobIDsArgument.kwargs)
    return parser


def get_runs_from_file(path: Path, print_error: bool = False) -> list[SlurmRun]:
    """Retrieve all run objects from file storage.

    Args:
        path: Path object where to look recursively for the files.

    Returns:
        List of all found SlumRun objects.
    """
    runs = []
    for file in path.rglob("*.json"):
        # TODO: RunRunner should be adapted to have more general methods for runs
        # So this method can work for both local and slurm
        try:
            run_obj = SlurmRun.from_file(file)
            runs.append(run_obj)
        except Exception as ex:
            # Not a (correct) RunRunner JSON file
            if print_error:
                print(f"[WARNING] Could not load file: {file}. Exception: {ex}")
    return runs


def wait_for_jobs(path: Path,
                  check_interval: int,
                  verbosity: VerbosityLevel = VerbosityLevel.STANDARD,
                  filter: list[str] = None) -> None:
    """Wait for all active jobs to finish executing.

    Args:
        path: The Path where to look for the stored jobs.
        check_interval: The time in seconds between updating the jobs.
        verbosity: Amount of information shown.
            The lower verbosity means lower computational load.
        filter: If present, only show the given job ids.
    """
    # Filter jobs on relevant status
    jobs = [run for run in get_runs_from_file(path)
            if run.status == Status.WAITING or run.status == Status.RUNNING]

    if filter is not None:
        jobs = [job for job in jobs if job.run_id in filter]

    running_jobs = jobs

    def signal_handler(num: int, _: any) -> None:
        """Create clean exit for CTRL + C."""
        if num == signal.SIGINT:
            sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    # If verbosity is quiet there is no need for further information
    if verbosity == VerbosityLevel.QUIET:
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
    elif verbosity == VerbosityLevel.STANDARD:
        # Order in which to display the jobs
        status_order = {Status.COMPLETED: 0, Status.RUNNING: 1, Status.WAITING: 2}
        while len(running_jobs) > 0:
            # Information to be printed to the table
            information = [["RunId", "Name", "Partition", "Status",
                            "Dependencies", "Finished Jobs", "Run Time"]]
            running_jobs = [run for run in running_jobs
                            if run.status == Status.WAITING
                            or run.status == Status.RUNNING]
            sorted_jobs = sorted(
                jobs, key=lambda job: (status_order.get(job.status, 4), job.run_id))
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
                     job.partition,
                     status_text,
                     "None" if len(job.dependencies) == 0
                        else ", ".join(job.dependencies),
                     f"{finished_jobs_count}/{len(job.all_status)}",
                     job.runtime])
            # Print the table
            table = tabulate(information, headers="firstrow", tablefmt="grid")
            print(table)
            time.sleep(check_interval)

            # Clears the table for the new table to be printed
            lines = table.count("\n") + 1
            # \033 is the escape character (ESC),
            # [{lines}A is the escape sequence that moves the cursor up.
            print(f"\033[{lines}A", end="")
            # [J is the escape sequence that clears the console from the cursor down
            print("\033[J", end="")

    print("All jobs done!")


if __name__ == "__main__":
    # Log command call
    logging.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    check_interval = gv.settings().get_general_check_interval()
    verbosity = gv.settings().get_general_verbosity()

    wait_for_jobs(path=gv.settings().DEFAULT_log_output,
                  check_interval=check_interval,
                  verbosity=verbosity,
                  filter=args.job_ids)
