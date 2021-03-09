#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
import os
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_run_solvers_help as srsh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh

def run_parallel_portfolio(instances: list, portfolio_path: Path, cutoff_time: int)->bool:
    print('DEBUG instances: ' + str(instances))
    print('DEBUG portfolio_path: ' + str(portfolio_path))
    print('DEBUG cutoff_time: ' + str(cutoff_time))
    #TODO add functionality for multiple instances
    if(len(instances) > 1): 
        print('c running on multiple instances is not yet supported, aborting the process')
        return False

    solver_list = sfh.get_solver_list_from_parallel_portfolio(portfolio_path)
    print('c there are ' + str(len(solver_list)) + ' jobs')
    for instance in instances:
        for solver in solver_list:
            solver_wrapper_path = str(solver) + '/sparkle_run_default_wrapper.py'
            raw_result_path = sgh.sparkle_tmp_path + sfh.get_last_level_directory_name(solver) + '_' + sfh.get_last_level_directory_name(instance) + '_' + sbh.get_time_pid_random_string() + '.rawres'
            runsolver_values_path = raw_result_path.replace('.rawres', '.val')
            srsh.run_solver_on_instance(str(solver),solver_wrapper_path,str(instance),raw_result_path, runsolver_values_path,str(cutoff_time))
    return True