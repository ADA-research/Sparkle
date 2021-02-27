#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''

import os
import sys
from pathlib import Path


def make_directory(sparkle_portfolio_selector_path: Path)->bool:
    try:
        sparkle_portfolio_selector_path.mkdir(mode=0o777, parents=True,exist_ok=False)
    except:
        print('c There was an error creating the directory')
        return False
    else:
        print('c Directory created')
        return True

def directory_exists(sparkle_portfolio_selector_path: Path) -> bool:
	exists = sparkle_portfolio_selector_path.is_dir()

	return exists

def construct_sparkle_parallel_portfolio(sparkle_parallel_portfolio_path: Path, overwrite: bool)->bool:


    if(directory_exists(Path(sparkle_parallel_portfolio_path)) and overwrite==False):
        print('c directory already exists')
        print('c use \'--overwrite\' or give the portfolio a different name')
        return False
    elif(overwrite==True):
        #TODO add the removing of the existing files
        print('c this is not yet implemented please use a different name')
        pass
    else:
        if(make_directory(Path(sparkle_parallel_portfolio_path)) == False):
            return False
    return True