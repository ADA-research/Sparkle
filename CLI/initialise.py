#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import subprocess
import argparse
from pathlib import Path


from sparkle.platform import file_help as sfh
from CLI.help.command_help import CommandName
from sparkle.platform import snapshot_help as srh
from sparkle.platform import snapshot_help as snh
from sparkle.structures import csv_help as scsv
import global_variables as gv
import sparkle_logging as sl


def parser_function() -> argparse.ArgumentParser:
    """Parse CLI arguments for the initialise command."""
    parser = argparse.ArgumentParser(
        description=("Initialise the Sparkle platform, this command does not have any "
                     "arguments."))
    return parser


def check_for_initialise(argv: list[str], requirements: list[CommandName] = None)\
        -> None:
    """Function to check if initialize command was executed and execute it otherwise.

    Args:
        argv: List of the arguments from the caller.
        requirements: The requirements that have to be executed before the calling
            function.
    """
    if not srh.detect_current_sparkle_platform_exists(check_all_dirs=True):
        print("-----------------------------------------------")
        print("No Sparkle platform found; "
              + "The platform will now be initialized automatically")
        if requirements is not None:
            if len(requirements) == 1:
                print(f"The command {requirements[0]} has \
                      to be executed before executing this command.")
            else:
                print(f"""The commands {", ".join(requirements)} \
                      have to be executed before executing this command.""")
        print("-----------------------------------------------")
        initialise_sparkle(argv)


def initialise_sparkle(argv: list[str]) -> None:
    """Initialize a new Sparkle platform.

    Args:
        argv: The argument list for the log_command
    """
    print("Start initialising Sparkle platform ...")

    gv.snapshot_dir.mkdir(exist_ok=True)

    if snh.detect_current_sparkle_platform_exists(check_all_dirs=False):
        snh.save_current_sparkle_platform()
        snh.remove_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    # Log command call
    sl.log_command(argv)

    sfh.create_temporary_directories()
    for working_dir in gv.working_dirs:
        working_dir.mkdir(exist_ok=True)

    Path(f"{gv.ablation_dir}scenarios/").mkdir(exist_ok=True)
    scsv.SparkleCSV.create_empty_csv(gv.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(gv.performance_data_csv_path)
    gv.pap_performance_data_tmp_path.mkdir(exist_ok=True)

    # Check that Runsolver is compiled, otherwise, compile
    if not Path(gv.runsolver_path).exists():
        print("Runsolver does not exist, trying to compile...")
        if not Path(gv.runsolver_dir + "Makefile").exists():
            print("WARNING: Runsolver executable doesn't exist and cannot find makefile."
                  f" Please verify the contents of the directory: {gv.runsolver_dir}")
        else:
            compile_runsolver = subprocess.run(["make"],
                                               cwd=gv.runsolver_dir,
                                               capture_output=True)
            if compile_runsolver.returncode != 0:
                print("WARNING: Compilation of Runsolver failed with the folowing msg:"
                      f"[{compile_runsolver.returncode}] {compile_runsolver.stderr}")
            else:
                print("Runsolver compiled successfully!")

    print("New Sparkle platform initialised!")


if __name__ == "__main__":
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args()

    initialise_sparkle(sys.argv)
