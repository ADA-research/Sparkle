#!/usr/bin/env python3

import os
import sys
import argparse
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_logging as sl


if __name__ == r"__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "record_file_path",
        metavar="record-file-path",
        type=str,
        help="path to the record file",
    )

    # Process command line arguments
    args = parser.parse_args()
    record_file_name = args.record_file_path
    if not os.path.exists(record_file_name):
        print(r"c Record file " + record_file_name + r" does not exist!")
        sys.exit()

    print(r"c Cleaning existing Sparkle platform ...")
    sparkle_record_help.cleanup_current_sparkle_platform()
    print(r"c Existing Sparkle platform cleaned!")

    print(r"c Loading record file " + record_file_name + " ...")
    sparkle_record_help.extract_sparkle_record(record_file_name)
    print(r"c Record file " + record_file_name + r" loaded successfully!")
