#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to construct a parallel algorithm portfolio."""

import sys
import argparse
from pathlib import Path

from CLI.help.status_info import ConstructParallelPortfolioStatusInfo
import sparkle_logging as sl
import global_variables as sgh
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState
from CLI.support import construct_parallel_portfolio_help as scpp
from CLI.help.reporting_scenario import Scenario
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--nickname", type=Path,
                        help="Give a nickname to the portfolio."
                             f" (default: {sgh.sparkle_parallel_portfolio_name})")
    parser.add_argument("--solver", required=False, nargs="+", type=str,
                        help="Specify the list of solvers, add "
                             '\",<#solver_variations>\" to the end of a path to add '
                             "multiple instances of a single solver. For example "
                             "--solver Solver/PbO-CCSAT-Generic,25 to construct a "
                             "portfolio containing 25 variations of PbO-CCSAT-Generic.")
    parser.add_argument("--overwrite", type=bool,
                        help="When set to True an existing parallel portfolio with the "
                             "same name will be overwritten, when False an error will "
                             "be thrown instead."
                             " (default: "
                             f"{sgh.settings.DEFAULT_paraport_overwriting})")
    parser.add_argument("--settings-file", type=Path,
                        help="Specify the settings file to use in case you want to use "
                             "one other than the default"
                             f" (default: {sgh.settings.DEFAULT_settings_path}")
    return parser


if __name__ == "__main__":
    # Initialise settings
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments;
    args = parser.parse_args()
    portfolio_name = args.nickname
    list_of_solvers = args.solver

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO]
    )

    # If no solvers are given all previously added solvers are used
    if list_of_solvers is None:
        list_of_solvers = sgh.solver_list

    # Do first, so other command line options can override settings from the file
    if args.settings_file is not None:
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    if args.overwrite is not None:
        sgh.settings.set_paraport_overwriting_flag(args.overwrite, SettingState.CMD_LINE)

    if portfolio_name is None:
        portfolio_name = sgh.sparkle_parallel_portfolio_name

    portfolio_path = sgh.sparkle_parallel_portfolio_dir / portfolio_name

    print("Start constructing Sparkle parallel portfolio ...")

    # create status info
    status_info = ConstructParallelPortfolioStatusInfo()
    status_info.set_portfolio_name(str(portfolio_name))
    status_info.set_list_of_solvers(list_of_solvers)
    status_info.save()

    success = scpp.construct_sparkle_parallel_portfolio(portfolio_path, args.overwrite,
                                                        list_of_solvers)

    if success:
        print(f"Sparkle parallel portfolio located at {str(portfolio_path)}")
        print("Sparkle parallel portfolio construction done!")

        # Update latest scenario
        sgh.latest_scenario().set_parallel_portfolio_path(Path(portfolio_path))
        sgh.latest_scenario().set_latest_scenario(Scenario.PARALLEL_PORTFOLIO)
        # Set to default to overwrite instance from possible previous run
        sgh.latest_scenario().set_parallel_portfolio_instance_list()

        status_info.delete()

    else:
        print("An unexpected error occurred when constructing the portfolio, please "
              "check your input and try again.")

    # Write used settings to file
    sgh.settings.write_used_settings()
