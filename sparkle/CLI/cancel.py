"""Command to cancel async jobs."""
import sys
import argparse

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
        for j in jobs:
            if args.all or j.run_id in args.job_ids:
                j.kill()
    else:
        # TODO: Make selection table
        print("No jobs to cancel!")
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
