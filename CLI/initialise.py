#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

from sparkle.platform import file_help as sfh
from CLI.help.command_help import CommandName
from CLI.help import snapshot_help as srh
from CLI.help import snapshot_help as snh
from sparkle.platform import settings_help
from sparkle.structures import csv_help as scsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
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

    (gv.ablation_dir / "scenarios/").mkdir(exist_ok=True)
    scsv.SparkleCSV.create_empty_csv(gv.feature_data_csv_path)
    # Initialise the Performance DF with the static dimensions
    # TODO: We have many sparkle settings values regarding ``number of runs''
    # E.g. configurator, parallel portfolio, and here too. Should we unify this more, or
    # just make another setting that does this specifically for performance data?
    PerformanceDataFrame(gv.performance_data_csv_path,
                         objectives=gv.settings.get_general_sparkle_objectives(),
                         n_runs=1)

    # Check that Runsolver is compiled, otherwise, compile
    if not gv.runsolver_path.exists():
        print("Runsolver does not exist, trying to compile...")
        if not (gv.runsolver_dir / "Makefile").exists():
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
    # Check that java is available
    if shutil.which("java") is None:
        # NOTE: An automatic resolution of Java at this point would be good
        # However, loading modules from Python has thusfar not been successfull.
        print("Could not find Java as an executable!")
    print("New Sparkle platform initialised!")


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser(
        description=("Initialise the Sparkle platform, this command does not have any "
                     "arguments."))
    # Process command line arguments
    args = parser.parse_args()
    global settings
    gv.settings = settings_help.Settings()

    initialise_sparkle(sys.argv)
