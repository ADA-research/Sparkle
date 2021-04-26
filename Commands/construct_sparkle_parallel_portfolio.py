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
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac
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
    parser.add_argument("--portfolio-name", type=str, help='Gives a name to the portfolio, otherwise it will overwrite the latest portfolio.')
    parser.add_argument("--solver", required=False, metavar='N', nargs="+", type=str, help='List of paths to the solvers, add \",solver_instances\" to the end of a path to add multiple instances of a single solver')
    parser.add_argument("--overwrite", default=sgh.settings.DEFAULT_parallel_portfolio_overwriting, action=ac.SetByUser, help='Allows overwrite of the directory, default true if no name is specified otherwise the default is false')
    parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='specify the settings file to use in case you want to use one other than the default')

    # Process command line arguments;
    args = parser.parse_args() 
    portfolio_str = args.portfolio_name
    list_of_solvers = args.solver
    #If no solvers are given all previously added solvers are used
    #TODO only use all solvers which havent been used yet
    if list_of_solvers is None: list_of_solvers = sgh.solver_list

    if ac.set_by_user(args, 'settings_file'): sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE) # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, 'overwrite'): 
        if(args.overwrite != 'True'): args.overwrite = False
        sgh.settings.set_parallel_portfolio_overwriting_flag(args.overwrite, SettingState.CMD_LINE)
        overwrite = args.overwrite
    else:
        overwrite = args.overwrite
        if portfolio_str is None: overwrite = True
    if portfolio_str is not None:
        portfolio_path = "Sparkle_Parallel_portfolio/" + portfolio_str
    else:
        portfolio_path = sgh.sparkle_parallel_portfolio_path
    print('c Start constructing Sparkle parallel portfolio ...')

    #TODO use relative solver path
    success = scpp.construct_sparkle_parallel_portfolio(Path(portfolio_path),overwrite,list_of_solvers)
    
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