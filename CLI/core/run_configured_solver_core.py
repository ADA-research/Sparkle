#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a configured solver on an instance, only for internal calls from Sparkle."""
#Team2

import argparse
from pathlib import Path
from pathlib import PurePath

from CLI.sparkle_help import sparkle_global_help as sgh
from CLI.sparkle_help import sparkle_settings
from CLI.sparkle_help import sparkle_run_configured_solver_help as srcsh
from sparkle.types.sparkle_objective import PerformanceMeasure


if __name__ == "__main__":
    # Initialise settings
    global settings
    file_path_latest = Path("Settings/latest.ini")
    sgh.settings = sparkle_settings.Settings(file_path_latest)
    perf_measure = sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, type=Path, nargs="+",
                        help="path to instance to run on")
    parser.add_argument("--performance-measure", choices=PerformanceMeasure.__members__,
                        default=perf_measure,
                        help="the performance measure, e.g. runtime")

    # Process command line arguments
    args = parser.parse_args()
    performance_measure = PerformanceMeasure.from_str(args.performance_measure)

    # Run configured solver
    srcsh.call_configured_solver_sequential([args.instance])
