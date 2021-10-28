#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help import sparkle_run_configured_solver_help as srcsh
from sparkle_help.reporting_scenario import ReportingScenario


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instance_path",
        type=Path,
        nargs="+",
        help="Path(s) to instance file(s) or instance directory")
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help="settings file to use instead of the default")
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_performance_measure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime")

    # Process command line arguments
    args = parser.parse_args()
    instance_path = args.instance_path

    if ac.set_by_user(args, "settings_file"):
        # Do first, so other command line options can override settings from the file
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE)

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Directory
    if len(instance_path) == 1 and instance_path[0].is_dir():
        job_id_str = srcsh.call_configured_solver_for_instance_directory(
            instance_path[0])
        print("c Running configured solver in parallel. Waiting for Slurm job(s) with "
              f"id(s): {job_id_str}")
    # Single instance (single-file or multi-file)
    elif [path.is_file() for path in instance_path]:
        srcsh.call_configured_solver_for_instance(instance_path)
        print("c Running configured solver done!")
    else:
        print("c Input instance or instance directory error!")

    # Write used settings to file
    sgh.settings.write_used_settings()
