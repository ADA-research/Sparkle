#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import argparse
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_file_help as sfh


def parser_function():
    """Parse CLI arguments for the initialise command."""
    parser = argparse.ArgumentParser(
        description=("Initialise the Sparkle platform, this command does not have any "
                     "arguments."))
    return parser


if __name__ == "__main__":

    sfh.initialise_sparkle()

    # Log command call
    sl.log_command(sys.argv)
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args()


