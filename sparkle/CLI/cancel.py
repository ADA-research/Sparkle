#!/usr/bin/env python3
"""Command to cancel async jobs."""
import sys
import argparse
import signal

from runrunner.base import Status

from sparkle.CLI.help import logging
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import jobs as jobs_help
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Create parser for the cancel command."""
    parser = argparse.ArgumentParser(description="Sparkle cancel command.")
    parser.add_argument(*ac.JobIDsArgument.names, **ac.JobIDsArgument.kwargs)
    parser.add_argument(*ac.AllJobsArgument.names, **ac.AllJobsArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the cancel command."""
    # Log command call
    logging.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    # Filter jobs on relevant status
    path = gv.settings().DEFAULT_log_output
    jobs = [run for run in jobs_help.get_runs_from_file(path)
            if run.status == Status.WAITING or run.status == Status.RUNNING]

    if args.all or args.job_ids:
        killed_jobs = []
        for j in jobs:
            if args.all or j.run_id in args.job_ids:
                j.kill()
                killed_jobs.append(j)
        if len(killed_jobs) == 0:
            if args.all:
                print("No jobs to cancel.")
                sys.exit()
            else:
                print(f"ERROR: No jobs with ids {args.job_ids} to cancel.")
                # NOTE: Should we raise an error here instead?
                sys.exit(-1)
        else:
            print(f"Canceled {len(killed_jobs)} jobs with IDs: "
                  f"{', '.join([j.run_id for j in killed_jobs])}.")
    else:
        def signal_handler(num: int, _: any) -> None:
            """Create clean exit for CTRL + C."""
            if num == signal.SIGINT:
                sys.exit()
        signal.signal(signal.SIGINT, signal_handler)

        print("Select a job to cancel:")
        while any(j.status == Status.WAITING or j.status == Status.RUNNING
                  for j in jobs):
            table = jobs_help.create_jobs_table(jobs)
            print(table)

            # TODO: Handle input for selecting jobs

            # Clears the table for the new table to be printed
            lines = table.count("\n") + 1
            # \033 is the escape character (ESC),
            # [{lines}A is the escape sequence that moves the cursor up.
            print(f"\033[{lines}A", end="")
            # [J is the escape sequence that clears the console from the cursor down
            print("\033[J", end="")

    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
