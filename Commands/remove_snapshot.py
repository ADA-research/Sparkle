#!/usr/bin/env python3
"""Sparkle command to delete a recorded Sparkle platform."""

import os
import sys
import argparse
from pathlib import Path
from sparkle_help import sparkle_logging as sl


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "snapshot_file_path",
        metavar="snapshot-file-path",
        type=str,
        help="path to the snapshot file",
    )

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    snapshot_file_name = args.snapshot_file_path
    if not Path(snapshot_file_name).exists():
        print("Snapshot file " + snapshot_file_name + " does not exist!")
        sys.exit()

    print("Removing snapshot file " + snapshot_file_name + " ...")
    command_line = "rm -rf " + snapshot_file_name
    os.system(command_line)
    print("Snapshot file " + snapshot_file_name + " removed!")
