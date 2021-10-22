#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
from pathlib import Path
from pathlib import PurePath

try:
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_settings
    from sparkle_help import sparkle_run_configured_solver_help as srcsh
    from sparkle_help.sparkle_settings import PerformanceMeasure
    from sparkle_help.reporting_scenario import ReportingScenario
except ImportError:
    import sparkle_global_help as sgh
    import sparkle_settings
    import sparkle_run_configured_solver_help as srcsh
    from sparkle_settings import PerformanceMeasure
    from reporting_scenario import ReportingScenario


if __name__ == r'__main__':
    # Initialise settings
    global settings
    settings_dir = Path('Settings')
    file_path_latest = PurePath(settings_dir / 'latest.ini')
    sgh.settings = sparkle_settings.Settings(file_path_latest)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', required=True, type=str, nargs='+',
                        help='path to instance to run on')
    parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__,
                        default=sgh.settings.DEFAULT_general_performance_measure,
                        help='the performance measure, e.g. runtime')
    args = parser.parse_args()

    # Process command line arguments
    # Turn multiple instance files into a space separated string
    instance_path = " ".join(args.instance)
    performance_measure = PerformanceMeasure.from_str(args.performance_measure)

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Run configured solver
    srcsh.call_configured_solver_for_instance(instance_path)
