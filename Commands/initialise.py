#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_csv_help as scsv
from sparkle_help import sparkle_logging as sl


if __name__ == r"__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()

    # Process command line arguments
    args = parser.parse_args()

    print("c Start initialising Sparkle platform ...")

    if not os.path.exists(r"Records/"):
        output = os.mkdir(r"Records/")

    if not os.path.exists(r"Tmp/"):
        output = os.mkdir(r"Tmp/")
        sl.add_output("Tmp/", "Directory with temporary files")

    if not os.path.exists(r"Tmp/SBATCH_Extractor_Jobs/"):
        output = os.mkdir(r"Tmp/SBATCH_Extractor_Jobs/")

    if not os.path.exists(r"Tmp/SBATCH_Solver_Jobs/"):
        output = os.mkdir(r"Tmp/SBATCH_Solver_Jobs/")

    if not os.path.exists(r"Tmp/SBATCH_Portfolio_Jobs/"):
        output = os.mkdir(r"Tmp/SBATCH_Portfolio_Jobs/")

    if not os.path.exists(r"Tmp/SBATCH_Report_Jobs/"):
        output = os.mkdir(r"Tmp/SBATCH_Report_Jobs/")

    pap_sbatch_path = Path(sgh.sparkle_tmp_path) / 'SBATCH_Parallel_Portfolio_Jobs'

    if not pap_sbatch_path.exists():
        pap_sbatch_path.mkdir()

    if not os.path.exists(r"Log/"):
        output = os.mkdir(r"Log/")

    my_flag_anyone = sparkle_record_help.detect_current_sparkle_platform_exists()

    if my_flag_anyone:
        my_suffix = sparkle_basic_help.get_time_pid_random_string()
        my_record_filename = "Records/My_Record_" + my_suffix + ".zip"

        sparkle_record_help.save_current_sparkle_platform(my_record_filename)
        sparkle_record_help.cleanup_current_sparkle_platform()

        print("c Current Sparkle platform found!")
        print("c Current Sparkle platform recorded!")

    output = os.mkdir(r"Instances/")
    output = os.mkdir(r"Solvers/")
    output = os.mkdir(r"Extractors/")
    output = os.mkdir(r"Feature_Data/")
    output = os.mkdir(r"Performance_Data/")
    output = os.mkdir(r"Reference_Lists/")
    output = os.mkdir(r"Sparkle_Portfolio_Selector/")
    sgh.sparkle_parallel_portfolio_dir.mkdir()
    scsv.Sparkle_CSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.Sparkle_CSV.create_empty_csv(sgh.performance_data_csv_path)
    output = os.mkdir(r"Feature_Data/Tmp/")
    output = os.mkdir(r"Performance_Data/Tmp/")
    sgh.pap_performance_data_tmp_path.mkdir()
    print("c New Sparkle platform initialised!")
