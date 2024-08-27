#!/usr/bin/env python3
"""Command to remove temporary files not affecting the platform state."""
import sys
import argparse
import shutil

from sparkle.CLI.help import logging as sl
import sparkle.CLI.help.global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    return parser


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    shutil.rmtree(gv.settings().DEFAULT_tmp_output, ignore_errors=True)
    shutil.rmtree(gv.settings().DEFAULT_log_output, ignore_errors=True)
    gv.settings().DEFAULT_tmp_output.mkdir()
    gv.settings().DEFAULT_log_output.mkdir()


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    remove_temporary_files()
    print("Cleaned platform of temporary files!")
