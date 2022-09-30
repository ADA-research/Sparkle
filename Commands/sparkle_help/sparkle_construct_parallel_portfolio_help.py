#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path
from sparkle_help import sparkle_file_help as sfh


def add_solvers(sparkle_parallel_portfolio_path: Path, solver_list: list[str]) -> bool:
    '''Creates a file containing the list of solvers within the given portfolio path.'''
    empty_file = f'{sparkle_parallel_portfolio_path}/solvers.txt'
    sfh.create_new_empty_file(str(empty_file))

    for solver in solver_list:
        if solver.rfind(',') >= 0:
            solver_name = solver[:solver.rfind(',')]
            solver_n_instances = solver[solver.rfind(',')+1:]
            solver = f'{solver_name} {solver_n_instances}'
        sfh.append_string_to_file(empty_file, solver)

    return True


def construct_sparkle_parallel_portfolio(sparkle_parallel_portfolio_path: Path,
                                         overwrite: bool,
                                         list_of_solvers: list[str]) -> bool:
    '''Create the parallel portfolio by preparing a directory and the solver list.'''
    if sparkle_parallel_portfolio_path.is_dir():
        if overwrite:
            sfh.rmtree(sparkle_parallel_portfolio_path)
        else:
            print('directory already exists')
            print('use "--overwrite" or give the portfolio a different name')

            return False

    sparkle_parallel_portfolio_path.mkdir(parents=True, exist_ok=False)

    # Directory is now created (and cleaned)
    # Add a file which specifies the location of the solvers.
    if add_solvers(sparkle_parallel_portfolio_path, list_of_solvers) is False:
        print('An error occured when adding the solvers to the portfolio')

    return True
