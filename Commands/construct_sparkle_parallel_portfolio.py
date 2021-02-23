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

#Welke directory moet ik hiervoor aanhouden??
def generate_task_run_status():
    key_str = 'construct_sparkle_parallel_portfolio'
    task_run_status_path = r'Tmp/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
    status_info_str = 'Status: Running\n'
    sfh.write_string_to_file(task_run_status_path, status_info_str)
    return

def delete_task_run_status():
    key_str = 'construct_sparkle_parallel_portfolio'
    task_run_status_path = r'Tmp/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
    os.system(r'rm -rf ' + task_run_status_path)
    return

def delete_log_files():
    os.system(r'rm -f ' + sgh.sparkle_log_path)
    os.system(r'rm -f ' + sgh.sparkle_err_path)
    return


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
    
    generate_task_run_status()

    #Is het hier handig om checks uit te voeren of er wel instances bestaan.
    #En misschien andere checks die handig zijn om uit te voeren.

    print('c TODO ...')

    #TODO construct portfolio.
    delete_log_files() # Make sure no old log files remain
    success = scpp.construct_sparkle_parallel_portfolio(sgh.sparkle_parallel_portfolio_path, sgh.performance_data_csv_path, sgh.feature_data_csv_path)
    
    if success:
        print('c Sparkle portfolio selector constructed!')
        print('c Sparkle portfolio selector located at ' + sgh.sparkle_parallel_portfolio_path)
        
        # Update latest scenario
        sgh.latest_scenario.set_parallel_portfolio_path(Path(sgh.sparkle_parallel_portfolio_path))
        sgh.latest_scenario.set_latest_scenario(Scenario.PARALLEL)
        # Set to default to overwrite possible old path
        sgh.latest_scenario.set_parallel_test_case_directory()

        delete_task_run_status()
        delete_log_files()
        
    # Write used settings to file
    sgh.settings.write_used_settings()

    print('c After adding into scenario')