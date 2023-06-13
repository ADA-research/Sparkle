#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_snapshot_help
from sparkle_help import sparkle_csv_help as scsv
from sparkle_help import sparkle_logging as sl


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

    if not Path("Snapshots/").exists():
        output = sgh.snapshot_dir.mkdir()

    if not Path("Tmp/").exists():
        output = Path("Tmp/").mkdir()
        sl.add_output("Tmp/", "Directory with temporary files")

    if not Path("Tmp/SBATCH_Extractor_Jobs/").exists():
        output = Path("Tmp/SBATCH_Extractor_Jobs/").mkdir()

    if not Path("Tmp/SBATCH_Solver_Jobs/").exists():
        output = Path("Tmp/SBATCH_Solver_Jobs/").mkdir()

    if not Path("Tmp/SBATCH_Portfolio_Jobs/").exists():
        output = Path("Tmp/SBATCH_Portfolio_Jobs/").mkdir()

    if not Path("Tmp/SBATCH_Report_Jobs/").exists():
        output = Path("Tmp/SBATCH_Report_Jobs/").mkdir()

    pap_sbatch_path = Path(sgh.sparkle_tmp_path) / "SBATCH_Parallel_Portfolio_Jobs"

    if not pap_sbatch_path.exists():
        pap_sbatch_path.mkdir()

    if not Path("Log/").exists():
        output = Path("Log/").mkdir()

    my_flag_anyone = sparkle_snapshot_help.detect_current_sparkle_platform_exists()

    if my_flag_anyone:
        sparkle_snapshot_help.save_current_sparkle_platform()
        sparkle_snapshot_help.cleanup_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    output = Path("Instances/").mkdir()
    output = Path("Solvers/").mkdir()
    output = Path("Extractors/").mkdir()
    output = Path("Feature_Data/").mkdir()
    output = Path("Performance_Data/").mkdir()
    output = Path("Reference_Lists/").mkdir()
    output = Path("Sparkle_Portfolio_Selector/").mkdir()
    sgh.sparkle_parallel_portfolio_dir.mkdir()
    scsv.SparkleCSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(sgh.performance_data_csv_path)
    output = Path("Feature_Data/Tmp/").mkdir()
    output = Path("Performance_Data/Tmp/").mkdir()
    sgh.pap_performance_data_tmp_path.mkdir()
    print("New Sparkle platform initialised!")
