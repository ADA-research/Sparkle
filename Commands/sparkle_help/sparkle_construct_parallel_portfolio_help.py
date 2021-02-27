#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)
'''

import os
import sys
from pathlib import Path
from sparkle_help import sparkle_file_help as sfh


def add_solvers(sparkle_parallel_portfolio_path: Path, solver_list: list)->bool:
    empty_file = str(sparkle_parallel_portfolio_path) + "/solvers.txt"
    sfh.create_new_empty_file(empty_file)
    for solver in solver_list:
        sfh.append_string_to_file(empty_file, solver)
    return True

def make_directory(sparkle_parallel_portfolio_path: Path)->bool:
    try:
        sparkle_parallel_portfolio_path.mkdir(mode=0o777, parents=True,exist_ok=False)
    except:
        print('c There was an error creating the directory')
        return False
    else:
        print('c Directory created')
        return True

def directory_exists(sparkle_parallel_portfolio_path: Path) -> bool:
	exists = sparkle_parallel_portfolio_path.is_dir()

	return exists

def construct_sparkle_parallel_portfolio(sparkle_parallel_portfolio_path: Path, overwrite: bool,list_of_solvers: list)->bool:
    if(directory_exists(Path(sparkle_parallel_portfolio_path)) and overwrite==False):
        print('c directory already exists')
        print('c use \'--overwrite\' or give the portfolio a different name')
        return False
    elif(overwrite==True):
        #TODO add the removing of the existing files, sf
        print('c this is not yet implemented please use a different name')
        return False
    else:
        if(make_directory(Path(sparkle_parallel_portfolio_path)) == False):
            return False
    # Directory is now created or cleaned
    # Add a file which specifies the location of the solvers.
    if(add_solvers(Path(sparkle_parallel_portfolio_path),list_of_solvers) == False):
        print('c An error occured when adding the solvers to the portfolio')

    return True