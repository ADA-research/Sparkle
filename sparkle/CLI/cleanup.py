#!/usr/bin/env python3
"""Command to remove temporary files not affecting the platform state."""
import sys
import argparse
import shutil

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import snapshot_help as snh


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.CleanupArgumentAll.names, **ac.CleanupArgumentAll.kwargs)
    parser.add_argument(*ac.CleanupArgumentRemove.names,
                        **ac.CleanupArgumentRemove.kwargs)
    return parser


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    shutil.rmtree(gv.settings().DEFAULT_log_output, ignore_errors=True)
    gv.settings().DEFAULT_log_output.mkdir()


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    if args.all:
        shutil.rmtree(gv.settings().DEFAULT_output, ignore_errors=True)
        snh.create_working_dirs()
        print("Removed all output files from the platform!")
    elif args.remove:
        snh.remove_current_platform()
        snh.create_working_dirs()
        print("Cleaned platform of all files!")
    else:
        remove_temporary_files()
        print("Cleaned platform of temporary files!")
