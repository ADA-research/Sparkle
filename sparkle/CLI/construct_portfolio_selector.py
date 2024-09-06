#!/usr/bin/env python3
"""Sparkle command to construct a portfolio selector."""
import sys
import argparse
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.RecomputePortfolioSelectorArgument.names,
                        **ac.RecomputePortfolioSelectorArgument.kwargs)
    parser.add_argument(*ac.RecomputeMarginalContributionForSelectorArgument.names,
                        **ac.RecomputeMarginalContributionForSelectorArgument.kwargs)
    parser.add_argument(*ac.SelectorTimeoutArgument.names,
                        **ac.SelectorTimeoutArgument.kwargs)
    parser.add_argument(*ac.SparkleObjectiveArgument.names,
                        **ac.SparkleObjectiveArgument.kwargs)
    parser.add_argument(*ac.SelectorAblationArgument.names,
                        **ac.SelectorAblationArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    return parser


def judge_exist_remaining_jobs(feature_data_csv: Path,
                               performance_data_csv: Path) -> bool:
    """Return whether there are remaining feature or performance computation jobs."""
    feature_data = FeatureDataFrame(feature_data_csv)
    if feature_data.has_missing_vectors():
        return True
    performance_data = PerformanceDataFrame(performance_data_csv)
    return performance_data.has_missing_values


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    selector_timeout = args.selector_timeout
    flag_recompute_portfolio = args.recompute_portfolio_selector
    flag_recompute_marg_cont = args.recompute_marginal_contribution
    solver_ablation = args.solver_ablation

    check_for_initialise(
        COMMAND_DEPENDENCIES[CommandName.CONSTRUCT_PORTFOLIO_SELECTOR]
    )

    if ac.set_by_user(args, "objectives"):
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE
        )
    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    print("Start constructing Sparkle portfolio selector ...")
    selector = gv.settings().get_general_sparkle_selector()

    flag_judge_exist_remaining_jobs = judge_exist_remaining_jobs(
        gv.settings().DEFAULT_feature_data_path,
        gv.settings().DEFAULT_performance_data_path)

    if flag_judge_exist_remaining_jobs:
        print("There remain unperformed feature computation jobs or performance "
              "computation jobs!")
        print("Please first execute all unperformed jobs before constructing Sparkle "
              "portfolio selector")
        print("Sparkle portfolio selector is not successfully constructed!")
        sys.exit(-1)

    # Selector (AutoFolio) cannot handle cutoff time less than 2, adjust if needed
    cutoff_time = max(gv.settings().get_general_target_cutoff_time(), 2)

    # Determine the objective function
    objective = gv.settings().get_general_sparkle_objectives()[0]

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    if feature_data.has_missing_value():
        print("WARNING: Missing values in the feature data, will be imputed as the mean "
              "value of all other non-missing values! Imputing all missing values...")
        feature_data.impute_missing_values()

    # TODO: Allow user to specify subsets of data to be used

    # Selector is named after the solvers it can predict, sort for permutation invariance
    solvers = sorted([s.name for s in gv.settings().DEFAULT_solver_dir.iterdir()])
    selection_scenario_path = (
        gv.settings().DEFAULT_selection_output
        / gv.settings().DEFAULT_general_sparkle_selector.name
        / "_".join(solvers))

    # Update latest scenario
    gv.latest_scenario().set_selection_scenario_path(selection_scenario_path)
    gv.latest_scenario().set_latest_scenario(Scenario.SELECTION)
    # Set to default to overwrite possible old path
    gv.latest_scenario().set_selection_test_case_directory()

    selector_path = selection_scenario_path / "portfolio_selector"
    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    if selector_path.exists() and not flag_recompute_portfolio:
        print("Portfolio selector already exists. Set the recompute flag to re-create.")
        sys.exit()

    selector_path.parent.mkdir(exist_ok=True, parents=True)

    selector_run = selector.construct(selector_path,
                                      performance_data,
                                      feature_data,
                                      objective,
                                      cutoff_time,
                                      selector_timeout,
                                      run_on=run_on,
                                      sbatch_options=sbatch_options,
                                      base_dir=sl.caller_log_dir)
    if run_on == Runner.LOCAL:
        print("Sparkle portfolio selector constructed!")
    else:
        print("Sparkle portfolio selector constructor running...")

    dependencies = [selector_run]
    if solver_ablation:
        for solver in performance_data.solvers:
            solver_name = Path(solver).name
            ablate_solver_dir = selection_scenario_path / f"ablate_{solver_name}"
            ablate_solver_selector = ablate_solver_dir / "portfolio_selector"
            if (ablate_solver_selector.exists() and not flag_recompute_portfolio):
                print(f"Portfolio selector without {solver_name} already exists. "
                      "Set the recompute flag to re-create.")
                continue
            ablate_solver_dir.mkdir(exist_ok=True, parents=True)
            ablated_performance_data = performance_data.copy()
            ablated_performance_data.remove_solver(solver)
            ablated_run = selector.construct(ablate_solver_selector,
                                             ablated_performance_data,
                                             feature_data,
                                             objective,
                                             cutoff_time,
                                             selector_timeout,
                                             run_on=run_on,
                                             sbatch_options=sbatch_options,
                                             base_dir=sl.caller_log_dir)
            dependencies.append(ablated_run)
            if run_on == Runner.LOCAL:
                print(f"Portfolio selector without {solver_name} constructed!")
            else:
                print(f"Portfolio selector without {solver_name} constructor running...")
    with_actual = "--actual" if solver_ablation else ""
    cmd = (f"sparkle/CLI/compute_marginal_contribution.py --perfect {with_actual} "
           f"{ac.SparkleObjectiveArgument.names[0]} {objective}")

    marginal_contribution = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd,
        name=CommandName.COMPUTE_MARGINAL_CONTRIBUTION,
        base_dir=sl.caller_log_dir,
        dependencies=dependencies,
        sbatch_options=sbatch_options)
    dependencies.append(marginal_contribution)
    if run_on == Runner.LOCAL:
        marginal_contribution.wait()
        print("Selector marginal contribution computing done!")
    else:
        print(f"Running selector construction. Waiting for Slurm job(s) with id(s): "
              f"{', '.join([d.run_id for d in dependencies])}")

    # Write used settings to file
    gv.settings().write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
