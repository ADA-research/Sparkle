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
    parser.add_argument("--nickname", type=str, help='Give a nickname to the portfolio, the default name of a portfolio is sparkle_parallel_portfolio.')
    parser.add_argument("--solver", required=False, metavar='N', nargs="+", type=str, help='Specify the list of solvers, add \",solver_variations\" to the end of a path to add multiple instances of a single solver. For example --solver Solver/PbO-CCSAT-Generic,25 to construct a portfolio containing 25 variations of PbO-CCSAT-Generic.')
    parser.add_argument("--overwrite", default=sgh.settings.DEFAULT_parallel_portfolio_overwriting, action=ac.SetByUser, help='Allows overwriting of the directory, default true the --nickname option is NOT specified otherwise constructing a portfolio with a name of an already existing portfolio will throw an error if --overwrite True is not used.')
    parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='Specify the settings file to use in case you want to use one other than the default')

    # Process command line arguments;
    args = parser.parse_args() 
    portfolio_str = args.nickname
    list_of_solvers = args.solver
    
    # If no solvers are given all previously added solvers are used
    if list_of_solvers is None: list_of_solvers = sgh.solver_list
    # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, 'settings_file'): sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if ac.set_by_user(args, 'overwrite'): 
        if(args.overwrite != 'True'): args.overwrite = False
        sgh.settings.set_parallel_portfolio_overwriting_flag(args.overwrite, SettingState.CMD_LINE)
        overwrite = args.overwrite
    else:
        overwrite = args.overwrite
        if portfolio_str is None: overwrite = True
    if portfolio_str is not None:
        portfolio_path = "Sparkle_Parallel_Portfolio/" + portfolio_str
    else:
        portfolio_path = sgh.sparkle_parallel_portfolio_path
    print('c Start constructing Sparkle parallel portfolio ...')

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
        print('c An unexpected error occurred when constructing the portfolio, please check your input and try again.')
        pass
    # Write used settings to file
    sgh.settings.write_used_settings()