#!/usr/bin/env python3
"""Sparkle command to remove temporary files.

Only removes files not affecting the sparkle state.
"""

import os
import shutil
from pathlib import Path
import sys
import argparse
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_logging as sl


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    return parser


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    command_line = "rm -rf Commands/sparkle_help/*.pyc"
    os.system(command_line)
    shutil.rmtree(Path("Tmp/"))
    shutil.rmtree(Path("Tmp/SBATCH_Extractor_Jobs/"))
    shutil.rmtree(Path("Tmp/SBATCH_Solver_Jobs/"))
    shutil.rmtree(Path("Tmp/SBATCH_Portfolio_Jobs/"))
    shutil.rmtree(Path("Tmp/SBATCH_Report_Jobs/"))
    shutil.rmtree(Path("Tmp/SBATCH_Parallel_Portfolio_Jobs/"))
    shutil.rmtree(Path("Feature_Data/Tmp/"))
    shutil.rmtree(Path("Performance_Data/Tmp/"))
    shutil.rmtree(Path("Performance_Data/Tmp_PaP/"))
    shutil.rmtree(Path("Log/"))

    command_line = "rm -f slurm-*"
    os.system(command_line)

    shutil.rmtree(Path("Components/smac-v2.10.03-master-778/tmp/"))

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
