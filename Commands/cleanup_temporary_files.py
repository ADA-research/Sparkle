#!/usr/bin/env python3

import os
import sys
import argparse
from sparkle_help import sparkle_logging as sl


def remove_temporary_files():
    command_line = "rm -rf Commands/sparkle_help/*.pyc"
    os.system(command_line)
    command_line = "rm -rf Tmp/*"
    os.system(command_line)
    command_line = "rm -rf Tmp/SBATCH_Extractor_Jobs/*"
    os.system(command_line)
    command_line = "rm -rf Tmp/SBATCH_Solver_Jobs/*"
    os.system(command_line)
    command_line = "rm -rf Tmp/SBATCH_Portfolio_Jobs/*"
    os.system(command_line)
    command_line = "rm -rf Tmp/SBATCH_Report_Jobs/*"
    os.system(command_line)
    command_line = "rm -rf Feature_Data/Tmp/*"
    os.system(command_line)
    command_line = "rm -rf Performance_Data/Tmp/*"
    os.system(command_line)
    command_line = "rm -rf Log/*"
    os.system(command_line)
    command_line = "rm -f slurm-*"
    os.system(command_line)
    command_line = "rm -rf Components/smac-v2.10.03-master-778/tmp/*"
    os.system(command_line)

    return


def create_temporary_directories():
    command_line = "mkdir -p Tmp/SBATCH_Extractor_Jobs/"
    os.system(command_line)
    command_line = "mkdir -p Tmp/SBATCH_Solver_Jobs/"
    os.system(command_line)
    command_line = "mkdir -p Tmp/SBATCH_Portfolio_Jobs/"
    os.system(command_line)
    command_line = "mkdir -p Tmp/SBATCH_Report_Jobs/"
    os.system(command_line)

    return


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()

    # Process command line arguments
    args = parser.parse_args()

    print("c Cleaning temporary files ...")
    remove_temporary_files()
    create_temporary_directories()
    print("c Temporary files cleaned!")
