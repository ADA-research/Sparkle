#!/usr/bin/env python3

import sys
import argparse

from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_job_help as sjh
from sparkle_help.sparkle_command_help import CommandName

def parser_function():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--job-id",
        required=False,
        type=str,
        default=None,
        help="job ID to wait for"
    )
    group.add_argument(
        "--command",
        required=False,
        choices=CommandName.__members__,
        default=None,
        help=("command you want to run. Sparkle will wait for the dependencies of this "
              "command to be completed"),
    )
    return parser

if __name__ == r"__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    job_id = args.job_id
    command = CommandName.from_str(args.command)

    if job_id is not None:
        sjh.wait_for_job(job_id)
    elif command is not None:
        sjh.wait_for_dependencies(command)
    else:
        sjh.wait_for_all_jobs()
