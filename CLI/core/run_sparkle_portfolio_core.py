#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Execute Sparkle portfolio, only for internal calls from Sparkle."""
#Team2

import argparse
from pathlib import Path

from CLI.sparkle_help import sparkle_global_help as sgh
from sparkle.platform import settings_help
from CLI.sparkle_help import sparkle_run_portfolio_selector_help as srpsh


if __name__ == "__main__":
    # Initialise settings
    global settings
    file_path_latest = Path("Settings/latest.ini")
    sgh.settings = sparkle_settings.Settings(file_path_latest)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, type=str, nargs="+",
                        help="path to instance to run on")
    parser.add_argument("--performance-data-csv", required=True, type=str,
                        help="path to performance data csv")
    args = parser.parse_args()

    # Process command line arguments
    # Turn multiple instance files into a space separated string
    # NOTE: Not sure if this is actually supported
    instance_path = " ".join(args.instance)
    performance_data_csv_path = args.performance_data_csv

    # Run portfolio selector
    srpsh.call_sparkle_portfolio_selector_solve_instance(instance_path,
                                                         performance_data_csv_path)
