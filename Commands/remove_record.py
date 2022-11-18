#!/usr/bin/env python3
"""Sparkle command to delete a recorded Sparkle platform."""

import os
import sys
import argparse
from sparkle_help import sparkle_logging as sl


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'record_file_path',
        metavar='record-file-path',
        type=str,
        help='path to the record file',
    )

    return parser


if __name__ == '__main__':
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    record_file_name = args.record_file_path
    if not os.path.exists(record_file_name):
        print('Record file ' + record_file_name + ' does not exist!')
        sys.exit()

    print('Removing record file ' + record_file_name + ' ...')
    command_line = 'rm -rf ' + record_file_name
    os.system(command_line)
    print('Record file ' + record_file_name + ' removed!')
