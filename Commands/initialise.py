#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_csv_help as scsv
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_file_help as sfh


def parser_function():
    """Parse CLI arguments for the initialise command."""
    parser = argparse.ArgumentParser(
        description=("Initialise the Sparkle platform, this command does not have any "
                     "arguments."))
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("Start initialising Sparkle platform ...")

    if not Path("Records/").exists():
        Path("Records/").mkdir()

    sfh.create_temporary_directories()

    pap_sbatch_path = Path(sgh.sparkle_tmp_path) / "SBATCH_Parallel_Portfolio_Jobs"

    if not pap_sbatch_path.exists():
        pap_sbatch_path.mkdir()

    if not Path("Log/").exists():
        Path("Log/").mkdir()

    my_flag_anyone = sparkle_record_help.detect_current_sparkle_platform_exists()

    if my_flag_anyone:
        my_suffix = sparkle_basic_help.get_time_pid_random_string()
        my_record_filename = f"Records/My_Record_{my_suffix}.zip"

        sparkle_record_help.save_current_sparkle_platform(my_record_filename)
        sparkle_record_help.cleanup_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    Path("Instances/").mkdir()
    Path("Solvers/").mkdir()
    Path("Extractors/").mkdir()
    Path("Feature_Data/").mkdir()
    Path("Performance_Data/").mkdir()
    Path("Reference_Lists/").mkdir()
    Path("Sparkle_Portfolio_Selector/").mkdir()
    sgh.sparkle_parallel_portfolio_dir.mkdir()
    scsv.SparkleCSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(sgh.performance_data_csv_path)
    Path("Feature_Data/Tmp/").mkdir()
    Path("Performance_Data/Tmp/").mkdir()
    sgh.pap_performance_data_tmp_path.mkdir()
    print("New Sparkle platform initialised!")
