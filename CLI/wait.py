#!/usr/bin/env python3
"""Sparkle command to wait for one or more other commands to complete execution."""

import sys
import argparse

import sparkle_logging as sl
from CLI.support import sparkle_job_help as sjh
from CLI.help.command_help import CommandName


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
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


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.job_id is not None:
        sjh.wait_for_job(args.job_id)
    elif args.command is not None:
        command = CommandName.from_str(args.command)
        sjh.wait_for_dependencies(command)
    else:
        sjh.wait_for_all_jobs()
