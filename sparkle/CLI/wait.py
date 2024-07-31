#!/usr/bin/env python3
"""Sparkle command to wait for one or more other commands to complete execution."""

import sys
import argparse

from sparkle.CLI.help import sparkle_logging as sl
from sparkle.CLI.support import sparkle_job_help as sjh
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(*ac.JobIdArgument.names,
                       **ac.JobIdArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.job_id is not None:
        sjh.wait_for_job(args.job_id, path=gv.settings().DEFAULT_tmp_output)
    else:
        sjh.wait_for_all_jobs(path=gv.settings().DEFAULT_tmp_output)
