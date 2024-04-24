#!/usr/bin/env python3
"""Sparkle command to load a Sparkle platform from a .zip file."""

import sys
import argparse

from sparkle.platform import snapshot_help
import sparkle_logging as sl


def parser_function() -> argparse.ArgumentParser:
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
    snapshot_help.load_snapshot(args.snapshot_file_path)
