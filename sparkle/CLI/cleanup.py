#!/usr/bin/env python3
"""Command to remove temporary files not affecting the platform state."""
import sys
import argparse
import shutil

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import snapshot_help as snh
from sparkle.CLI.help import jobs as jobs_help


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Command to clean files from the "
                                                 "platform.")
    parser.add_argument(*ac.CleanupArgumentAll.names, **ac.CleanupArgumentAll.kwargs)
    parser.add_argument(*ac.CleanupArgumentRemove.names,
                        **ac.CleanupArgumentRemove.kwargs)
    parser.add_argument(*ac.CleanUpPerformanceDataArgument.names,
                        **ac.CleanUpPerformanceDataArgument.kwargs)
    return parser


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    shutil.rmtree(gv.settings().DEFAULT_log_output, ignore_errors=True)
    gv.settings().DEFAULT_log_output.mkdir()


def main(argv: list[str]) -> None:
    """Main function of the cleanup command."""
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    if args.all:
        shutil.rmtree(gv.settings().DEFAULT_output, ignore_errors=True)
        snh.create_working_dirs()
        print("Removed all output files from the platform!")
    elif args.remove:
        snh.remove_current_platform()
        snh.create_working_dirs()
        print("Cleaned platform of all files!")
    else:
        remove_temporary_files()
        print("Cleaned platform of temporary files!")
    if args.performance_data:
        # Check if we can cleanup the PerformanceDataFrame if necessary
        from runrunner.base import Status
        running_jobs = jobs_help.get_runs_from_file(gv.settings().DEFAULT_log_output,
                                                    filter=[Status.WAITING,
                                                            Status.RUNNING])
        if len(running_jobs) > 0:
            print("WARNING: There are still running jobs! Continue cleaning? [y/n]")
            a = input()
            if a != "y":
                sys.exit(0)
        from sparkle.structures import PerformanceDataFrame
        performance_data = PerformanceDataFrame(
            gv.settings().DEFAULT_performance_data_path)
        index_num = len(performance_data.index)
        # We only clean lines that are completely empty
        performance_data.remove_empty_runs()
        performance_data.save_csv()
        print(f"Removed {index_num - len(performance_data.index)} rows from the "
              f"Performance DataFrame, leaving {len(performance_data.index)} rows.")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
