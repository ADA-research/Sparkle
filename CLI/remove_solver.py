#!/usr/bin/env python3
"""Sparkle command to remove a solver from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

from sparkle.platform import file_help as sfh
import global_variables as sgh
from sparkle.structures.performance_dataframe import PerformanceDataFrame
import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "solver",
        metavar="solver",
        type=str,
        help="name, path to or nickname of the solver",
    )
    parser.add_argument(
        "--nickname",
        action="store_true",
        help="if set to True solver_path is used as a nickname for the solver",
    )
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver_path = Path(args.solver)

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_SOLVER])

    if args.nickname:
        solver_path = Path(sgh.solver_nickname_mapping[args.nickname])
    if not solver_path.parent == sgh.solver_dir:
        # Allow user to only specify solvers in Sparkle solver dir
        solver_path = sgh.solver_dir / solver_path
    if not solver_path.exists():
        print(f'Sparkle Solver path "{solver_path}" does not exist!')
        sys.exit(-1)

    print(f"Start removing solver {solver_path.name} ...")

    if len(sgh.solver_list) > 0:
        sfh.add_remove_platform_item(str(solver_path),
                                     sgh.solver_list_path)

    solver_nickname_mapping = sgh.solver_nickname_mapping
    if len(solver_nickname_mapping):
        for key in solver_nickname_mapping:
            if solver_nickname_mapping[key] == str(solver_path):
                output = solver_nickname_mapping.pop(key)
                break
        sgh.write_data_to_file(sgh.solver_nickname_list_path,
                               sgh.solver_nickname_mapping)

    if Path(sgh.performance_data_csv_path).exists():
        performance_data = PerformanceDataFrame(sgh.performance_data_csv_path)
        if solver_path.name in performance_data.dataframe.columns:
            performance_data.remove_solver(solver_path.name)
        performance_data.save_csv()

    shutil.rmtree(solver_path)

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(sgh.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        shutil.rmtree(sgh.sparkle_report_path)
        print(f"Removing Sparkle report {sgh.sparkle_report_path} done!")

    print(f"Removing solver {solver_path.name} done!")
