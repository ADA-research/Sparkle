#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''
import sys
import argparse

from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_settings
from sparkle_help.reporting_scenario import ReportingScenario

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