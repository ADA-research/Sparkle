#!/usr/bin/env python3
"""Sparkle command to show information about Sparkle."""

import sys
import argparse
from Commands.sparkle_help import sparkle_logging as sl

__description__ = "Platform for evaluating empirical algorithms/solvers"
__version__ = 0.3
__licence__ = "MIT"
__authors__ = [
    # Alphabetical order on family name first
    "Koen van der Blom",
    "Jeremie Gobeil",
    "Holger H. Hoos",
    "Chuan Luo",
    "Richard Middelkoop",
    "Jeroen Rook"]

__contact__ = "k.van.der.blom@liacs.leidenuniv.nl"


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
      The argument parser.
    """
    parser = argparse.ArgumentParser()
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("\n".join([
        f"Sparkle ({__description__})",
        f"Version: {__version__}",
        f"Licence: {__licence__}",
        f'Written by {", ".join(__authors__[:-1])}, and {__authors__[-1]}',
        f"Contact: {__contact__}",
        "For more details see README.md"]))
