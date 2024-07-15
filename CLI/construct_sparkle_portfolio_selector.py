#!/usr/bin/env python3
"""Sparkle command to construct a portfolio selector."""
import shutil
import sys
import argparse
from pathlib import Path

import global_variables as gv
import tools.general as tg
from sparkle.platform import settings_help
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from CLI.support import compute_marginal_contribution_help as scmch
import sparkle_logging as sl
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from sparkle.types.objective import PerformanceMeasure



def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.RecomputePortfolioSelectorArgument.names,
                        **ac.RecomputePortfolioSelectorArgument.kwargs)
    parser.add_argument(*ac.RecomputeMarginalContributionForSelectorArgument.names,
                        **ac.RecomputeMarginalContributionForSelectorArgument.kwargs)
    parser.add_argument(*ac.SelectorTimeoutArgument.names,
                        **ac.SelectorTimeoutArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureArgument.names,
                        **ac.PerformanceMeasureArgument.kwargs)

    return parser


def judge_exist_remaining_jobs(feature_data_csv: Path,
                               performance_data_csv: Path) -> bool:
    """Return whether there are remaining feature or performance computation jobs."""
    feature_data = FeatureDataFrame(feature_data_csv)
    if feature_data.has_missing_vectors():
        return True
    performance_data = PerformanceDataFrame(performance_data_csv)
    return performance_data.has_missing_performance()


def construct_sparkle_portfolio_selector(selector_path: Path,
                                         performance_data_csv_path: str,
                                         feature_data_csv_path: Path,
                                         flag_recompute: bool = False,
                                         selector_timeout: int = None) -> bool:
    """Create the Sparkle portfolio selector.

    Args:
        selector_path: Portfolio selector path.
        performance_data_csv_path: Performance data csv path.
        feature_data_csv_path: Feature data csv path.
        flag_recompute: Whether or not to recompute if the selector exists and no data
            was changed. Defaults to False.
        selector_timeout: The cuttoff time to configure the algorithm selector. If None
            uses the default selector configuration. Defaults to None.

    Returns:
        True if portfolio construction is successful.
    """
    # If the selector exists and the data didn't change, do nothing;
    # unless the recompute flag is set
    if selector_path.exists() and not flag_recompute:
        print("Portfolio selector already exists. Set the recompute flag to re-create.")
        return True

    # Remove contents of- and the selector path to ensure everything is (re)computed
    # for the new selector when required
    shutil.rmtree(selector_path.parent, ignore_errors=True)

    # (Re)create the path to the selector
    selector_path.parent.mkdir(parents=True, exist_ok=True)

    cutoff_time = gv.settings.get_general_target_cutoff_time()
    cutoff_time_minimum = 2

    # Selector (AutoFolio) cannot handle cutoff time less than 2, adjust if needed
    if cutoff_time < cutoff_time_minimum:
        print(f"Warning: A cutoff time of {cutoff_time} is too small for Selector, "
              f"setting it to {cutoff_time_minimum}")
        cutoff_time = cutoff_time_minimum

    # Determine the objective function
    perf_measure = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    if perf_measure == PerformanceMeasure.RUNTIME:
        objective_function = "runtime"
    elif perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION or\
            perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        objective_function = "solution_quality"
    else:
        print("ERROR: Unknown performance measure in portfolio selector construction.")
        sys.exit(-1)

    feature_data = FeatureDataFrame(feature_data_csv_path)
    bool_exists_missing_value = feature_data.has_missing_value()

    if bool_exists_missing_value:
        print("****** WARNING: There are missing values in the feature data, and all "
              "missing values will be imputed as the mean value of all other non-missing"
              " values! ******")
        print("Imputing all missing values...")
        feature_data.impute_missing_values()
        impute_feature_data_csv_path = Path(
            f"{feature_data_csv_path}_{tg.get_time_pid_random_string()}"
            "_impute.csv")
        feature_data.save_csv(impute_feature_data_csv_path)
        feature_data_csv_path = impute_feature_data_csv_path

    performance_data = PerformanceDataFrame(performance_data_csv_path)
    p_data_autofolio_path = performance_data.to_autofolio()
    f_data_autofolio_path = feature_data.to_autofolio()
    selector = gv.settings.get_general_sparkle_selector()
    selector_path = selector.construct(selector_path,
                                       p_data_autofolio_path,
                                       f_data_autofolio_path,
                                       objective_function,
                                       cutoff_time,
                                       selector_timeout)

    if bool_exists_missing_value:
        impute_feature_data_csv_path.unlink()

    # Remove the data copy for AutoFolio
    p_data_autofolio_path.unlink()
    f_data_autofolio_path.unlink()
    return True



if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

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
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    print("Start constructing Sparkle portfolio selector ...")

    flag_judge_exist_remaining_jobs = judge_exist_remaining_jobs(
        gv.feature_data_csv_path, gv.performance_data_csv_path)

    if flag_judge_exist_remaining_jobs:
        print("There remain unperformed feature computation jobs or performance "
              "computation jobs!")
        print("Please first execute all unperformed jobs before constructing Sparkle "
              "portfolio selector")
        print("Sparkle portfolio selector is not successfully constructed!")
        sys.exit(-1)

    success = construct_sparkle_portfolio_selector(
        gv.sparkle_algorithm_selector_path,
        gv.performance_data_csv_path,
        gv.feature_data_csv_path,
        flag_recompute_portfolio,
        args.selector_timeout
    )

    if success:
        print("Sparkle portfolio selector constructed!")
        print("Sparkle portfolio selector located at "
              f"{gv.sparkle_algorithm_selector_path}")

        # Update latest scenario
        gv.latest_scenario().set_selection_portfolio_path(
            Path(gv.sparkle_algorithm_selector_path)
        )
        gv.latest_scenario().set_latest_scenario(Scenario.SELECTION)
        # Set to default to overwrite possible old path
        gv.latest_scenario().set_selection_test_case_directory()

        # Compute and print marginal contributions of the perfect and actual portfolio
        # selectors
        scmch.compute_marginal_contribution(flag_compute_perfect=True,
                                            flag_compute_actual=True,
                                            flag_recompute=flag_recompute_marg_cont,
                                            selector_timeout=args.selector_timeout)

    # Write used settings to file
    gv.settings.write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
