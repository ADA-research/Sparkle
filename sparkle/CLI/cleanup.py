#!/usr/bin/env python3
"""Command to remove temporary files not affecting the platform state."""

import re
import sys
import argparse
import shutil

from sparkle.structures import PerformanceDataFrame

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import snapshot_help as snh
from sparkle.CLI.help import jobs as jobs_help


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to clean files from the platform."
    )
    parser.add_argument(*ac.CleanupArgumentAll.names, **ac.CleanupArgumentAll.kwargs)
    parser.add_argument(
        *ac.CleanupArgumentRemove.names, **ac.CleanupArgumentRemove.kwargs
    )
    parser.add_argument(
        *ac.CleanUpPerformanceDataArgument.names,
        **ac.CleanUpPerformanceDataArgument.kwargs,
    )
    return parser


def check_logs_performance_data(performance_data: PerformanceDataFrame) -> int:
    """Check if the performance data is missing values that can be extracted from the logs.

    Args:
        performance_data (PerformanceDataFrame): The performance data.

    Returns:
        int: The number of updated values.
    """
    # empty_indices = performance_data.empty_indices
    pattern = re.compile(
        r"^(?P<objective>\S+)\s*,\s*"
        r"(?P<instance>\S+)\s*,\s*"
        r"(?P<run_id>\S+)\s*\|\s*"
        r"(?P<solver>\S+)\s*,\s*"
        r"(?P<config_id>\S+)\s*:\s*"
        r"(?P<target_value>\S+)$"
    )
    import math

    # Only iterate over slurm log files
    log_files = [
        f
        for f in gv.settings().DEFAULT_log_output.glob("**/*")
        if f.is_file() and f.suffix == ".out"
    ]
    count = 0
    for log in log_files:
        for line in log.read_text().splitlines():
            match = pattern.match(line)
            if match:
                objective = match.group("objective")
                instance = match.group("instance")
                run_id = int(match.group("run_id"))
                solver = match.group("solver")
                config_id = match.group("config_id")
                target_value = match.group("target_value")
                current_value = performance_data.get_value(
                    solver, instance, config_id, objective, run_id
                )
                # TODO: Would be better to extract all nan indices from PDF and check against this?
                if (
                    (
                        isinstance(current_value, (int, float))
                        and math.isnan(current_value)
                    )
                    or isinstance(current_value, str)
                    and current_value == "nan"
                ):
                    performance_data.set_value(
                        target_value, solver, instance, config_id, objective, run_id
                    )
                    count += 1
    if count:
        performance_data.save_csv()
    return count


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    shutil.rmtree(gv.settings().DEFAULT_log_output, ignore_errors=True)
    gv.settings().DEFAULT_log_output.mkdir()


def main(argv: list[str]) -> None:
    """Main function of the cleanup command."""
    # Log command call
    sl.log_command(sys.argv, gv.settings().random_state)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    if args.performance_data:
        # Check if we can cleanup the PerformanceDataFrame if necessary
        from runrunner.base import Status

        running_jobs = jobs_help.get_runs_from_file(
            gv.settings().DEFAULT_log_output, filter=[Status.WAITING, Status.RUNNING]
        )
        if len(running_jobs) > 0:
            print("WARNING: There are still running jobs! Continue cleaning? [y/n]")
            a = input()
            if a != "y":
                sys.exit(0)

        performance_data = PerformanceDataFrame(
            gv.settings().DEFAULT_performance_data_path
        )
        count = check_logs_performance_data(performance_data)
        print(
            f"Extracted {count} values from the logs and placed them in the PerformanceDataFrame."
        )

        # Remove empty configurations
        removed_configurations = 0
        for solver, configurations in performance_data.configurations.items():
            for config_id, config in configurations.items():
                if config_id == PerformanceDataFrame.default_configuration:
                    continue
                if not config:  # Empty configuration, remove
                    performance_data.remove_configuration(solver, config_id)
                    removed_configurations += 1
        if removed_configurations:
            performance_data.save_csv()
        print(
            f"Removed {removed_configurations} empty configurations from the "
            "Performance DataFrame."
        )

        index_num = len(performance_data.index)
        # We only clean lines that are completely empty
        performance_data.remove_empty_runs()
        performance_data.save_csv()
        print(
            f"Removed {index_num - len(performance_data.index)} rows from the "
            f"Performance DataFrame, leaving {len(performance_data.index)} rows."
        )

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
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
