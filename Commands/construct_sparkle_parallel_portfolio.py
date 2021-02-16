#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''
import sys
import argparse

from sparkle_help import sparkle_logging as sl

if __name__ == r'__main__':
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()

    # Process command line arguments
    args = parser.parse_args()

    print('c Start constructing Sparkle parallel portfolio ...')
    print('c TODO ...')