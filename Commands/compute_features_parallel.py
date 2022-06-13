#!/usr/bin/env python3

import sys
import argparse
import compute_features as cf
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


def parser_function():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="re-run feature extractor for instances with previously computed features",
    )
    return parser


if __name__ == r"__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    my_flag_recompute = args.recompute

    # Start compute features parallel
    print("c Start computing features ...")

    cf.compute_features_parallel(my_flag_recompute)
