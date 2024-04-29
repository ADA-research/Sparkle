#!/usr/bin/env python3
"""Sparkle command to display the status of the Sparkle platform."""

import sys
import argparse

import global_variables as sgh
from sparkle.platform import system_status as sssh
import sparkle_logging as sl


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="output system status in verbose mode",
    )
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("Reporting current system status of Sparkle ...")
    sssh.print_sparkle_list(sgh.solver_list, "Solver", args.verbose)
    sssh.print_sparkle_list(sgh.extractor_list, "Extractor", args.verbose)
    sssh.print_sparkle_list(sgh.instance_list, "Instance", args.verbose)
    sssh.print_list_remaining_feature_computation_job(
        sgh.feature_data_csv_path, args.verbose
    )
    sssh.print_list_remaining_performance_computation_job(
        sgh.performance_data_csv_path, args.verbose
    )
    print("Current system status of Sparkle reported!")
