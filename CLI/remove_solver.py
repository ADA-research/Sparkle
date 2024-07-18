#!/usr/bin/env python3
"""Sparkle command to remove a solver from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

from sparkle.platform import file_help as sfh
import global_variables as gv
from sparkle.structures import PerformanceDataFrame
import CLI.help.sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.SolverRemoveArgument.names,
                        **ac.SolverRemoveArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver_path = resolve_object_name(args.solver,
                                      gv.solver_nickname_mapping,
                                      gv.solver_dir)

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_SOLVER])
    if solver_path is None:
        print(f'Could not resolve Solver path/name "{solver_path}"!')
        sys.exit(-1)
    if not solver_path.parent == gv.solver_dir:
        # Allow user to only specify solvers in Sparkle solver dir
        print("Specified Solver is not is Sparkle solver dir! Exiting.")
        sys.exit(-1)

    print(f"Start removing solver {solver_path.name} ...")

    solver_nickname_mapping = gv.solver_nickname_mapping
    if len(solver_nickname_mapping):
        nickname = None
        for key in solver_nickname_mapping:
            if solver_nickname_mapping[key] == str(solver_path):
                nickname = key
                break
        sfh.add_remove_platform_item(
            nickname,
            gv.solver_nickname_list_path,
            gv.file_storage_data_mapping[gv.solver_nickname_list_path],
            remove=True)

    if gv.performance_data_csv_path.exists():
        performance_data = PerformanceDataFrame(gv.performance_data_csv_path)
        if solver_path.name in performance_data.dataframe.columns:
            performance_data.remove_solver(solver_path.name)
        performance_data.save_csv()

    shutil.rmtree(solver_path)

    if Path(gv.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(gv.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    print(f"Removing solver {solver_path.name} done!")
