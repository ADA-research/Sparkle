#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import os
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

    print("Cleaning existing Sparkle platform ...")
    sparkle_record_help.remove_current_sparkle_platform()
    sfh.remove_temporary_files()
    command_line = "rm -f Components/Sparkle-latex-generator/Sparkle_Report.pdf"
    os.system(command_line)
    print("Existing Sparkle platform cleaned!")

    print("Start initialising Sparkle platform ...")

    Path("Records/").mkdir(exist_ok=True)

    sfh.create_temporary_directories()

    pap_sbatch_path = Path(sgh.sparkle_tmp_path) / "SBATCH_Parallel_Portfolio_Jobs"

    pap_sbatch_path.mkdir(exist_ok=True)

    Path("Log/").mkdir(exist_ok=True)

    my_flag_anyone = sparkle_record_help.detect_current_sparkle_platform_exists()

    if my_flag_anyone:
        my_suffix = sparkle_basic_help.get_time_pid_random_string()
        my_record_filename = f"Records/My_Record_{my_suffix}.zip"

        sparkle_record_help.save_current_sparkle_platform(my_record_filename)
        sparkle_record_help.remove_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    Path("Instances/").mkdir()
    Path("Solvers/").mkdir()
    Path("Extractors/").mkdir()
    Path("Reference_Lists/").mkdir()
    Path("Sparkle_Portfolio_Selector/").mkdir()
    sgh.sparkle_parallel_portfolio_dir.mkdir()
    Path("Feature_Data/Tmp/").mkdir(parents=True)
    Path("Performance_Data/Tmp/").mkdir(parents=True)
    scsv.SparkleCSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(sgh.performance_data_csv_path)
    sgh.pap_performance_data_tmp_path.mkdir()
    print("New Sparkle platform initialised!")
