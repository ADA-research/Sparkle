#!/usr/bin/env python3
"""Command to display the status of the platform."""
import sys
import argparse

from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import system_status as sssh
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Display the status of the platform.")
    parser.add_argument(*ac.VerboseArgument.names,
                        **ac.VerboseArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the status command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    print("Reporting current system status of Sparkle ...")
    sssh.print_sparkle_list([s for s in gv.settings().DEFAULT_solver_dir.iterdir()],
                            "Solver", args.verbose)
    sssh.print_sparkle_list([e for e in gv.settings().DEFAULT_extractor_dir.iterdir()],
                            "Extractor", args.verbose)
    sssh.print_sparkle_list([i for i in gv.settings().DEFAULT_instance_dir.iterdir()],
                            "Instance Set", args.verbose)

    sssh.print_feature_computation_jobs(
        gv.settings().DEFAULT_feature_data_path, args.verbose
    )
    sssh.print_performance_computation_jobs(
        gv.settings().DEFAULT_performance_data_path, args.verbose
    )

    # scan configurator log files for warnings
    configurator = gv.settings().get_general_sparkle_configurator()
    configurator.get_status_from_logs()

    print("\nCurrent system status of Sparkle reported!")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
