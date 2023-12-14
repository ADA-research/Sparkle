#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import sys
import argparse

from Commands.sparkle_help import sparkle_file_help as sfh


def parser_function() -> argparse.ArgumentParser:
    """Parse CLI arguments for the initialise command."""
    parser = argparse.ArgumentParser(
        description=("Initialise the Sparkle platform, this command does not have any "
                     "arguments."))
    return parser


if __name__ == "__main__":
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args()

    sfh.initialise_sparkle(sys.argv)
