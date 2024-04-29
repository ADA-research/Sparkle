#!/usr/bin/env python3
"""Sparkle command to construct a portfolio selector."""

import sys
import argparse
from pathlib import Path

from CLI.help.status_info import ConstructPortfolioSelectorStatusInfo
import global_variables as sgh
from sparkle.platform import file_help as sfh, settings_help
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.support import construct_portfolio_selector_help as scps
from CLI.support import compute_marginal_contribution_help as scmch
from CLI.support import sparkle_job_help as sjh
import sparkle_logging as sl
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recompute-portfolio-selector",
        action="store_true",
        help=("force the construction of a new portfolio selector even when it already "
              "exists for the current feature and performance data. NOTE: This will "
              "also result in the computation of the marginal contributions of solvers "
              "to the new portfolio selector."),
    )
    parser.add_argument(
        "--recompute-marginal-contribution",
        action="store_true",
        help=("force marginal contribution to be recomputed even when it already exists "
              "in file for the current selector"),
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )

    return parser


def judge_exist_remaining_jobs(feature_data_csv_path: str,
                               performance_data_csv_path: str) -> bool:
    """Return whether there are remaining feature or performance computation jobs."""
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    feature_computation_jobs =\
        feature_data_csv.get_list_remaining_feature_computation_job()
    total_job_num = sjh.get_num_of_total_job_from_list(feature_computation_jobs)

    if total_job_num > 0:
        return True

    performance_data_csv = PerformanceDataFrame(performance_data_csv_path)
    performance_computation_jobs =\
        performance_data_csv.get_list_remaining_performance_computation_job()
    total_job_num = sjh.get_num_of_total_job_from_list(performance_computation_jobs)

    return total_job_num > 0


def delete_log_files() -> None:
    """Remove the log files."""
    sfh.rmfiles([sgh.sparkle_log_path, sgh.sparkle_err_path])


def print_log_paths() -> None:
    """Print paths to the log files."""
    print("Consider investigating the log files:")
    print(f"stdout: {sgh.sparkle_log_path}")
    print(f"stderr: {sgh.sparkle_err_path}")


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    flag_recompute_portfolio = args.recompute_portfolio_selector
    flag_recompute_marg_cont = args.recompute_marginal_contribution

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR]
    )

    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    print("Start constructing Sparkle portfolio selector ...")

    status_info = ConstructPortfolioSelectorStatusInfo()
    status_info.set_algorithm_selector_path(str(sgh.sparkle_algorithm_selector_path))
    status_info.set_feature_data_csv_path(str(sgh.feature_data_csv_path))
    status_info.set_performance_data_csv_path(str(sgh.performance_data_csv_path))
    status_info.save()

    flag_judge_exist_remaining_jobs = judge_exist_remaining_jobs(
        sgh.feature_data_csv_path, sgh.performance_data_csv_path
    )

    if flag_judge_exist_remaining_jobs:
        print("There remain unperformed feature computation jobs or performance "
              "computation jobs!")
        print("Please first execute all unperformed jobs before constructing Sparkle "
              "portfolio selector")
        print("Sparkle portfolio selector is not successfully constructed!")

        sys.exit(-1)

    delete_log_files()  # Make sure no old log files remain
    success = scps.construct_sparkle_portfolio_selector(
        sgh.sparkle_algorithm_selector_path,
        sgh.performance_data_csv_path,
        sgh.feature_data_csv_path,
        flag_recompute_portfolio,
    )

    if success:
        print("Sparkle portfolio selector constructed!")
        print("Sparkle portfolio selector located at "
              f"{sgh.sparkle_algorithm_selector_path}")

        # Update latest scenario
        sgh.latest_scenario().set_selection_portfolio_path(
            Path(sgh.sparkle_algorithm_selector_path)
        )
        sgh.latest_scenario().set_latest_scenario(Scenario.SELECTION)
        # Set to default to overwrite possible old path
        sgh.latest_scenario().set_selection_test_case_directory()

        # Compute and print marginal contributions of the perfect and actual portfolio
        # selectors
        scmch.compute_marginal_contribution(flag_compute_perfect=True,
                                            flag_compute_actual=True,
                                            flag_recompute=flag_recompute_marg_cont)

        status_info.delete()

        delete_log_files()

    # Write used settings to file
    sgh.settings.write_used_settings()
    # Write used scenario to file
    sgh.latest_scenario().write_scenario_ini()
