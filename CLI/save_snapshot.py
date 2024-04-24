#!/usr/bin/env python3
"""Sparkle command to save the current Sparkle platform in a .zip file."""

import sys
import argparse

from sparkle.platform import snapshot_help
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

    snapshot_help.save_current_sparkle_platform()
