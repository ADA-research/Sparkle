#!/usr/bin/env python3
"""Sparkle command to construct a portfolio selector."""

import sys
import argparse
from pathlib import Path

from Commands.Structures.status_info import ConstructPortfolioSelectorStatusInfo
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_construct_portfolio_selector_help as scps
from Commands.sparkle_help import sparkle_compute_marginal_contribution_help as scmch
from Commands.sparkle_help import sparkle_job_help
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_settings
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help.sparkle_settings import SettingState
from Commands.sparkle_help import argparse_custom as ac
from Commands.sparkle_help.reporting_scenario import ReportingScenario
from Commands.sparkle_help.reporting_scenario import Scenario
from Commands.sparkle_help import sparkle_command_help as sch


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
        default=sgh.settings.DEFAULT_general_performance_measure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )

    return parser


def judge_exist_remaining_jobs(feature_data_csv_path: str,
                               performance_data_csv_path: str) -> bool:
    """Return whether there are remaining feature or performance computation jobs."""
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    list_feature_computation_job = (
        feature_data_csv.get_list_remaining_feature_computation_job()
    )
    total_job_num = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job
    )

    if total_job_num > 0:
        return True

    performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        performance_data_csv_path
    )
    list_performance_computation_job = (
        performance_data_csv.get_list_remaining_performance_computation_job()
    )
    total_job_num = sparkle_job_help.get_num_of_total_job_from_list(
        list_performance_computation_job
    )

    if total_job_num > 0:
        return True

    return False


def delete_log_files() -> None:
    """Remove the log files."""
    sfh.rmfiles([sgh.sparkle_log_path, sgh.sparkle_err_path])
    return


def print_log_paths() -> None:
    """Print paths to the log files."""
    print("Consider investigating the log files:")
    print(f"stdout: {sgh.sparkle_log_path}")
    print(f"stderr: {sgh.sparkle_err_path}")
    return


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    flag_recompute_portfolio = args.recompute_portfolio_selector
    flag_recompute_marg_cont = args.recompute_marginal_contribution

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR])

    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE
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
        sgh.latest_scenario.set_selection_portfolio_path(
            Path(sgh.sparkle_algorithm_selector_path)
        )
        sgh.latest_scenario.set_latest_scenario(Scenario.SELECTION)
        # Set to default to overwrite possible old path
        sgh.latest_scenario.set_selection_test_case_directory()

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
    sgh.latest_scenario.write_scenario_ini()
