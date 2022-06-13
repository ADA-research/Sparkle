#!/usr/bin/env python3

import os
import sys
import argparse

from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_logging as sl
import cleanup_temporary_files as ctf


def parser_function():
    parser = argparse.ArgumentParser()

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("c Cleaning existing Sparkle platform ...")
    sparkle_record_help.cleanup_current_sparkle_platform()
    ctf.remove_temporary_files()
    command_line = "rm -f Components/Sparkle-latex-generator/Sparkle_Report.pdf"
    os.system(command_line)
    print("c Existing Sparkle platform cleaned!")
