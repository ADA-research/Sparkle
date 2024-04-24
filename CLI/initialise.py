#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import argparse

from sparkle.platform import file_help as sfh
from CLI.help.command_help import CommandName
from sparkle.platform import snapshot_help as srh


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
        sfh.initialise_sparkle(argv)


if __name__ == "__main__":
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args()

    sfh.initialise_sparkle(sys.argv)
