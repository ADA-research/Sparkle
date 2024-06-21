#!/usr/bin/env python3
"""Sparkle command to display the status of the Sparkle platform."""

import sys
import argparse

import global_variables as gv
from sparkle.platform import system_status as sssh
import sparkle_logging as sl
from CLI.help import argparse_custom as ac
from sparkle.platform import settings_help


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.VerboseArgument.names,
                        **ac.VerboseArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    global settings
    gv.settings = settings_help.Settings()

    print("Reporting current system status of Sparkle ...")
    sssh.print_sparkle_list(gv.solver_list, "Solver", args.verbose)
    sssh.print_sparkle_list(gv.extractor_list, "Extractor", args.verbose)
    sssh.print_sparkle_list(gv.instance_list, "Instance", args.verbose)
    sssh.print_list_remaining_feature_computation_job(
        gv.feature_data_csv_path, args.verbose
    )
    sssh.print_list_remaining_performance_computation_job(
        gv.performance_data_csv_path, args.verbose
    )

    # scan configurator log files for warnings
    configurator = gv.settings.get_general_sparkle_configurator()
    configurator.get_status_from_logs()

    print("\nCurrent system status of Sparkle reported!")
