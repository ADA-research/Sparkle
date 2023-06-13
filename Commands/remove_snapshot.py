#!/usr/bin/env python3
"""Sparkle command to delete a recorded Sparkle platform."""

import sys
import argparse
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_snapshot_help as snh


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
    snh.remove_snapshot(args.snapshot_file_path)
