#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_settings
from sparkle_help import sparkle_construct_parallel_portfolio_help as scpp
from sparkle_help.reporting_scenario import ReportingScenario
from sparkle_help.reporting_scenario import Scenario

if __name__ == r'__main__':
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser
    #TODO add arguments

    # Process command line arguments; none to process yet.
    # args = parser.parse_args() 

    print('c Start constructing Sparkle parallel portfolio ...')
    print('c TODO ...')

    #TODO construct portfolio.
    success = 1
    succes2 = scpp.construct_sparkle_parallel_portfolio(sgh.sparkle_parallel_portfolio_path, sgh.performance_data_csv_path, sgh.feature_data_csv_path)
    
    if success:
        print('c Sparkle portfolio selector constructed!')
        print('c Sparkle portfolio selector located at ' + sgh.sparkle_parallel_portfolio_path)
        
        # Update latest scenario
        sgh.latest_scenario.set_parallel_portfolio_path(Path(sgh.sparkle_parallel_portfolio_path))
        sgh.latest_scenario.set_latest_scenario(Scenario.PARALLEL)
        # Set to default to overwrite possible old path
        sgh.latest_scenario.set_parallel_test_case_directory()


    print('c After adding into scenario')