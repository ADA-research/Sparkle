#!/usr/bin/env python3
"""Sparkle command to remove temporary files.

Only removes files not affecting the sparkle state.
"""

import sys
import argparse

from sparkle.platform import file_help as sfh
import sparkle_logging as sl


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("Cleaning temporary files ...")
    sfh.remove_temporary_files()
    sfh.create_temporary_directories()
    print("Temporary files cleaned!")
