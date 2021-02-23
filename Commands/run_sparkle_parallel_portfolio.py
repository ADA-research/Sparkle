#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''

import sys
import argparse

from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help import sparkle_global_help as sgh

if __name__ == r'__main__':
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()

    # Process command line arguments
    # not needed yet.
    # args = parser.parse_args()

    print('c Sparkle parallel portfolio is running ...')
    print('c TODO ...')

    print('c Running Sparkle parallel portfolio is done!')

    # Write used settings to file
    sgh.settings.write_used_settings()
