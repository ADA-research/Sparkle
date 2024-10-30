#!/usr/bin/env python3
"""Sparkle command to wait for one or more other commands to complete execution."""
import sys
import signal
import time
import argparse
from pathlib import Path

from runrunner.base import Status

from sparkle.platform.cli_types import VerbosityLevel
from sparkle.CLI.help import jobs as jobs_help
from sparkle.CLI.help import logging
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Wait for async jobs to finish. Gives periodic updates in table "
                    " format about each job.")
    parser.add_argument(*ac.JobIDsArgument.names, **ac.JobIDsArgument.kwargs)
    return parser


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
    jobs = [run for run in jobs_help.get_runs_from_file(path)
            if run.status == Status.WAITING or run.status == Status.RUNNING]

    if filter is not None:
        jobs = [job for job in jobs if job.run_id in filter]

    running_jobs = jobs

    def signal_handler(num: int, _: any) -> None:
        """Create clean exit for CTRL + C."""
        if num == signal.SIGINT:
            sys.exit()
    signal.signal(signal.SIGINT, signal_handler)

    # If verbosity is quiet there is no need for further information
    if verbosity == VerbosityLevel.QUIET:
        prev_jobs = len(running_jobs) + 1
        while len(running_jobs) > 0:
            if len(running_jobs) < prev_jobs:
                print(f"Waiting for {len(running_jobs)} jobs...", flush=False)
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
            for job in running_jobs:
                job.get_latest_job_details()
            running_jobs = [run for run in running_jobs
                            if run.status == Status.WAITING
                            or run.status == Status.RUNNING]
            sorted_jobs = sorted(
                jobs, key=lambda job: (status_order.get(job.status, 4), job.run_id))
            table = jobs_help.create_jobs_table(sorted_jobs)
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


def main(argv: list[str]) -> None:
    """Main function of the wait command."""
    # Log command call
    logging.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    check_interval = gv.settings().get_general_check_interval()
    verbosity = gv.settings().get_general_verbosity()

    wait_for_jobs(path=gv.settings().DEFAULT_log_output,
                  check_interval=check_interval,
                  verbosity=verbosity,
                  filter=args.job_ids)


if __name__ == "__main__":
    main(sys.argv[1:])
