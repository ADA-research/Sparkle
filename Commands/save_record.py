#!/usr/bin/env python3

import sys
import argparse
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_logging as sl

def parser_function():
    parser = argparse.ArgumentParser()
    return parser

if __name__ == r"__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    my_suffix = sparkle_basic_help.get_time_pid_random_string()
    my_record_filename = "Records/My_Record_" + my_suffix + ".zip"

    sparkle_record_help.save_current_sparkle_platform(my_record_filename)

    print(r"c Record file " + my_record_filename + r" saved successfully!")
