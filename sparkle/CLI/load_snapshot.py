#!/usr/bin/env python3
"""Sparkle command to load a Sparkle platform from a .zip file."""
import sys
import argparse
from pathlib import Path

from sparkle.CLI.help import snapshot_help
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.SnapshotArgument.names,
                        **ac.SnapshotArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args()
    snapshot_help.load_snapshot(Path(args.snapshot_file_path))
