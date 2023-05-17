#!/usr/bin/env python3
"""Sparkle command to remove a solver from the Sparkle platform."""

import os
import sys
import argparse
from pathlib import Path
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_logging as sl


def parser_function():
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

    if args.nickname:
        solver_path = sparkle_global_help.solver_nickname_mapping[args.nickname]
    if not Path(solver_path).exists():
        print(f'Solver path "{solver_path}" does not exist!')
        sys.exit()

    if solver_path[-1] == "/":
        solver_path = solver_path[:-1]

    print(
        "Starting removing solver "
        + sfh.get_last_level_directory_name(solver_path)
        + " ..."
    )

    solver_list = sparkle_global_help.solver_list
    if bool(solver_list):
        sfh.remove_from_solver_list(solver_path)

    solver_nickname_mapping = sparkle_global_help.solver_nickname_mapping
    if bool(solver_nickname_mapping):
        for key in solver_nickname_mapping:
            if solver_nickname_mapping[key] == solver_path:
                output = solver_nickname_mapping.pop(key)
                break
        sfh.write_solver_nickname_mapping()

    if Path(sparkle_global_help.performance_data_csv_path).exists():
        performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            sparkle_global_help.performance_data_csv_path
        )
        for column_name in performance_data_csv.list_columns():
            if solver_path == column_name:
                performance_data_csv.delete_column(column_name)
        performance_data_csv.update_csv()

    command_line = "rm -rf " + solver_path
    os.system(command_line)

    solver_name = sfh.get_last_level_directory_name(solver_path)
    smac_solver_path = (
        sparkle_global_help.smac_dir
        + "/"
        + "example_scenarios/"
        + solver_name
        + "_*/"
    )
    if Path(smac_solver_path).exists():
        command_line = "rm -rf " + smac_solver_path
        os.system(command_line)

    if Path(sparkle_global_help.sparkle_portfolio_selector_path).exists():
        command_line = "rm -f " + sparkle_global_help.sparkle_portfolio_selector_path
        os.system(command_line)
        print(
            "Removing Sparkle portfolio selector "
            + sparkle_global_help.sparkle_portfolio_selector_path
            + " done!"
        )

    if Path(sparkle_global_help.sparkle_report_path).exists():
        command_line = "rm -f " + sparkle_global_help.sparkle_report_path
        os.system(command_line)
        print(
            "Removing Sparkle report "
            + sparkle_global_help.sparkle_report_path
            + " done!"
        )

    print(
        "Removing solver " + sfh.get_last_level_directory_name(solver_path) + " done!"
    )
