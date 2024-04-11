#!/usr/bin/env python3
"""Sparkle command to remove a solver from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_command_help as sch


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "solver_path",
        metavar="solver-path",
        type=str,
        help="path to or nickname of the solver",
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
    solver_path = args.solver_path

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.REMOVE_SOLVER])

    if args.nickname:
        solver_path = sgh.solver_nickname_mapping[args.nickname]
    if not Path(solver_path).exists():
        print(f'Solver path "{solver_path}" does not exist!')
        sys.exit(-1)

    if solver_path[-1] == "/":
        solver_path = solver_path[:-1]

    print(f"Start removing solver {sfh.get_last_level_directory_name(solver_path)} ...")

    if len(sgh.solver_list) > 0:
        sfh.add_remove_platform_item(solver_path,
                                     sgh.solver_list_path)

    solver_nickname_mapping = sgh.solver_nickname_mapping
    if len(solver_nickname_mapping):
        for key in solver_nickname_mapping:
            if solver_nickname_mapping[key] == solver_path:
                output = solver_nickname_mapping.pop(key)
                break
        sgh.write_data_to_file(sgh.solver_nickname_list_path,
                               sgh.solver_nickname_mapping)

    if Path(sgh.performance_data_csv_path).exists():
        performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            sgh.performance_data_csv_path
        )
        for column_name in performance_data_csv.dataframe.columns:
            if solver_path == column_name:
                performance_data_csv.remove_solver(column_name)
        performance_data_csv.save_csv()

    shutil.rmtree(solver_path)

    solver_name = sfh.get_last_level_directory_name(solver_path)
    smac_solver_path = f"{sgh.smac_dir}scenarios/{solver_name}_*"

    if Path(smac_solver_path).exists():
        shutil.rmtree(smac_solver_path)

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(sgh.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        shutil.rmtree(sgh.sparkle_report_path)
        print(f"Removing Sparkle report {sgh.sparkle_report_path} done!")

    print(f"Removing solver {sfh.get_last_level_directory_name(solver_path)} done!")
