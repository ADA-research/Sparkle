#!/usr/bin/env python3
"""Sparkle command to display the status of the Sparkle platform."""

import sys
import argparse

from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import system_status as sssh
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.platform.settings_objects import Settings


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
    gv.settings = Settings()
    check_for_initialise()

    print("Reporting current system status of Sparkle ...")
    sssh.print_sparkle_list([s for s in gv.settings.DEFAULT_solver_dir.iterdir()],
                            "Solver", args.verbose)
    sssh.print_sparkle_list([e for e in gv.extractor_dir.iterdir()],
                            "Extractor", args.verbose)
    sssh.print_sparkle_list([i for i in gv.instance_dir.iterdir()],
                            "Instance", args.verbose)
    sssh.print_feature_computation_jobs(
        gv.feature_data_csv_path, args.verbose
    )
    sssh.print_performance_computation_jobs(
        gv.performance_data_csv_path, args.verbose
    )

    # scan configurator log files for warnings
    configurator = gv.settings.get_general_sparkle_configurator()
    configurator.get_status_from_logs()

    print("\nCurrent system status of Sparkle reported!")
