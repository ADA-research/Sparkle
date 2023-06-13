#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_snapshot_help
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

    print("Cleaning existing Sparkle platform ...")
    sparkle_record_help.remove_current_sparkle_platform()
    command_line = "rm -f Components/Sparkle-latex-generator/Sparkle_Report.pdf"
    os.system(command_line)
    print("Existing Sparkle platform cleaned!")

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("Start initialising Sparkle platform ...")

    sgh.snapshot_dir.mkdir(exist_ok=True)

    sfh.create_temporary_directories()

    pap_sbatch_path = Path(sgh.sparkle_tmp_path) / "SBATCH_Parallel_Portfolio_Jobs"

    pap_sbatch_path.mkdir(exist_ok=True)

    my_flag_anyone = sparkle_snapshot_help.detect_current_sparkle_platform_exists()

    if my_flag_anyone:
        sparkle_snapshot_help.save_current_sparkle_platform()
        sparkle_snapshot_help.remove_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    sfh.create_temporary_directories()
    sgh.test_data_dir.mkdir()
    sgh.instance_dir.mkdir()
    sgh.solver_dir.mkdir()
    sgh.extractor_dir.mkdir()
    sgh.reference_list_dir.mkdir()
    sgh.sparkle_portfolio_selector_dir.mkdir()
    sgh.sparkle_parallel_portfolio_dir.mkdir()
    Path(f"{sgh.ablation_dir}scenarios/").mkdir()
    scsv.SparkleCSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(sgh.performance_data_csv_path)
    sgh.pap_performance_data_tmp_path.mkdir()
    print("New Sparkle platform initialised!")
