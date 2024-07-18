#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Execute Sparkle portfolio, only for internal calls from Sparkle."""
import argparse

import CLI.help.global_variables as gv
from sparkle.platform.settings_objects import Settings
from CLI.support import run_portfolio_selector_help as srpsh


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = Settings()

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

    # Run portfolio selector
    srpsh.call_sparkle_portfolio_selector_solve_instance(instance_path,
                                                         args.performance_data_csv)
