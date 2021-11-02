#!/usr/bin/env python3

import sys
import argparse
import random
from sparkle_help import sparkle_logging as sl

__description__ = "Platform for evaluating empirical algorithms/solvers"
__version__ = "0.2"
__licence__ = "MIT"
__authors__ = [
    "Koen van der Blom",
    "Jeremie Gobeil",
    "Holger H. Hoos",
    "Chuan Luo",
    "Richard Middelkoop",
    "Jeroen Rook",
]

__contact__ = "k.van.der.blom@liacs.leidenuniv.nl"

if __name__ == r"__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()

    # Process command line arguments
    args = parser.parse_args()

    print("c", "\nc ".join([
        f"Sparkle ({__description__})",
        f"Version: {__version__}",
        f"Licence: {__licence__}",
        f"Written by {', '.join(__authors__[:-1])}, and {__authors__[-1]}",
        f"Contact: {__contact__}",
        "For more details see README.md",
    ]))
