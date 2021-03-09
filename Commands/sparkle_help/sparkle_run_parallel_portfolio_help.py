#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
import os
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh

def run_parallel_portfolio(instances: list, portfolio_path: Path, cutoff_time: int)->bool:
    print('DEBUG instances: ' + str(instances))
    print('DEBUG portfolio_path: ' + str(portfolio_path))
    print('DEBUG cutoff_time: ' + str(cutoff_time))
    #TODO add functionality for multiple instances
    if(len(instances) > 1): 
        print('c running on multiple instances is not yet supported, aborting the process')
        return False

    solver_list = sfh.get_solver_list_from_parallel_portfolio(portfolio_path)
    print('DEBUG ' + str(solver_list))

    return True