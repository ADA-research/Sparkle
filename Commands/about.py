#!/usr/bin/env python3

import sys
import argparse
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_global_help as sgh

__description__ = 'Platform for evaluating empirical algorithms/solvers'
__version__ = sgh.sparkle_version
__licence__ = 'MIT'
__authors__ = [
    # Alphabetical order on family name first
    'Koen van der Blom',
    'Jeremie Gobeil',
    'Holger H. Hoos',
    'Chuan Luo',
    'Richard Middelkoop',
    'Jeroen Rook']

__contact__ = 'k.van.der.blom@liacs.leidenuniv.nl'


def parser_function():
    parser = argparse.ArgumentParser()
    return parser


if __name__ == '__main__':
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print('\n'.join([
        f'Sparkle ({__description__})',
        f'Version: {__version__}',
        f'Licence: {__licence__}',
        f'Written by {", ".join(__authors__[:-1])}, and {__authors__[-1]}',
        f'Contact: {__contact__}',
        'For more details see README.md']))
