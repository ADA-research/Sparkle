#!/usr/bin/env python3
"""Sparkle command to print the status of possibly running jobs."""

import sys
import argparse

from sparkle.platform import run_status_help
import sparkle_logging as sl


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="output run status in verbose mode"
    )
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("Reporting current running status of Sparkle ...")
    run_status_help.print_running_solver_jobs()
    run_status_help.print_running_configuration_jobs()
    run_status_help.print_running_parallel_portfolio_construction_jobs()
    run_status_help.print_running_portfolio_selector_construction_jobs()
    run_status_help.print_running_generate_report_jobs()
    print("Current running status of Sparkle reported!")
