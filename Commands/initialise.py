#!/usr/bin/env python3
"""Command to initialise a Sparkle platform."""

import os
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_snapshot_help as snh
from sparkle_help import sparkle_csv_help as scsv
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


