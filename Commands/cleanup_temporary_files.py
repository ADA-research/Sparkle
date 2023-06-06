#!/usr/bin/env python3
"""Sparkle command to remove temporary files."""

import os
import sys
import argparse
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_logging as sl


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    return parser


def remove_temporary_files() -> None:
    """Remove temporary files."""
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
    command_line = "rm -rf Tmp/SBATCH_Parallel_Portfolio_Jobs/*"
    os.system(command_line)
    command_line = "rm -rf Feature_Data/Tmp/*"
    os.system(command_line)
    command_line = "rm -rf Performance_Data/Tmp/*"
    os.system(command_line)
    command_line = "rm -rf Performance_Data/Tmp_PaP/*"
    os.system(command_line)
    command_line = "rm -rf Log/*"
    os.system(command_line)
    command_line = "rm -f slurm-*"
    os.system(command_line)
    command_line = "rm -rf Components/smac-v2.10.03-master-778/tmp/*"
    os.system(command_line)

    return


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("Cleaning temporary files ...")
    remove_temporary_files()
    sfh.create_temporary_directories()
    print("Temporary files cleaned!")
