#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''

import os
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--portfolio-name", type=str, help='Gives a name to the portfolio, otherwise it will overwrite the latest portfolio.')
    parser.add_argument("-o","--overwrite", action="store_true", help='Allows overwrite of the directory, default true if no name is specified otherwise the default is false')
    # Process command line arguments;
    args = parser.parse_args() 
    portfolio_str = args.portfolio_name
    overwrite = args.overwrite

    if portfolio_str is not None:
        portfolio_path = "Sparkle_Parallel_portfolio/" + portfolio_str
    else:
        portfolio_path = sgh.sparkle_parallel_portfolio_path
        overwrite = True
    print('c Start constructing Sparkle parallel portfolio ...')

    print('c TODO ...')

    #TODO construct portfolio.
    success = scpp.construct_sparkle_parallel_portfolio(Path(portfolio_path),overwrite)
    
    if success:
        print('c Sparkle portfolio constructed!')
        print('c Sparkle portfolio located at ' + str(Path(portfolio_path)))
        
        # Update latest scenario
        sgh.latest_scenario.set_parallel_portfolio_path(Path(portfolio_path))
        sgh.latest_scenario.set_latest_scenario(Scenario.PARALLELPORTFOLIO)
        # Set to default to overwrite possible old instance used
        sgh.latest_scenario.set_parallel_portfolio_instance()
    else:
        #TODO unsuccesful logging
        pass
    # Write used settings to file
    sgh.settings.write_used_settings()

    print('DEBUG After adding into scenario')