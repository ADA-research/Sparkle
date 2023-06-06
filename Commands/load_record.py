#!/usr/bin/env python3
"""Sparkle command to load a Sparkle platform from a .zip file."""

import sys
import argparse
from pathlib import Path
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_logging as sl


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "record_file_path",
        metavar="record-file-path",
        type=str,
        help="path to the record file",
    )

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    record_file_name = args.record_file_path
    if not Path(record_file_name).exists():
        print("Record file " + record_file_name + " does not exist!")
        sys.exit()

    print("Cleaning existing Sparkle platform ...")
    sparkle_record_help.remove_current_sparkle_platform()
    print("Existing Sparkle platform cleaned!")

    print("Loading record file " + record_file_name + " ...")
    sparkle_record_help.extract_sparkle_record(record_file_name)
    print("Record file " + record_file_name + " loaded successfully!")
