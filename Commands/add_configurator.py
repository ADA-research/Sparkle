#!/usr/bin/env python3
"""Sparkle command to add a configurator to the Sparkle platform."""

import shutil
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_logging as sl


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a configurator to the Sparkle platform.",
        epilog="")
    parser.add_argument(
        "--configurator",
        type=Path,
        required=True,
        help="path to the configurator"
    )

    return parser


if __name__ == "__main__":
    sl.log_command(sys.argv)

    parser = parser_function()

    args = parser.parse_args()
    configurator_path = args.configurator

    try:
        shutil.copytree(configurator_path, Path("Configurators", configurator_path.name))
        print("Configurator added to Sparkle.")
    except FileExistsError:
        print("ERROR: The configurator already exists. Nothing changed")
