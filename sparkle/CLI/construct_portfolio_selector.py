#!/usr/bin/env python3
"""Sparkle command to construct a portfolio selector."""
import sys
import argparse
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

from sparkle.solver import Selector
from sparkle.instance import Instance_Set

from sparkle.platform.settings_objects import SettingState
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types import resolve_objective
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to construct a portfolio selector over all known features "
                    "solver performances.")
    parser.add_argument(*ac.RecomputePortfolioSelectorArgument.names,
                        **ac.RecomputePortfolioSelectorArgument.kwargs)
    parser.add_argument(*ac.ObjectiveArgument.names,
                        **ac.ObjectiveArgument.kwargs)
    parser.add_argument(*ac.SelectorAblationArgument.names,
                        **ac.SelectorAblationArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTrainOptionalArgument.names,
                        **ac.InstanceSetTrainOptionalArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    # Solver Configurations arguments
    configuration_group = parser.add_mutually_exclusive_group(required=False)
    configuration_group.add_argument(*ac.AllSolverConfigurationArgument.names,
                                     **ac.AllSolverConfigurationArgument.kwargs)
    configuration_group.add_argument(*ac.BestSolverConfigurationArgument.names,
                                     **ac.BestSolverConfigurationArgument.kwargs)
    configuration_group.add_argument(*ac.DefaultSolverConfigurationArgument.names,
                                     **ac.DefaultSolverConfigurationArgument.kwargs)
    # TODO: Allow user to pick configurations by ?? per solver?
    return parser


def judge_exist_remaining_jobs(feature_data: FeatureDataFrame,
                               performance_data: PerformanceDataFrame) -> bool:
    """Return whether there are remaining feature or performance computation jobs."""
    missing_features = feature_data.has_missing_vectors()
    missing_performances = performance_data.has_missing_values
    if missing_features:
        print("There remain unperformed feature computation jobs! Please run: "
              "'sparkle compute features'")
    if missing_performances:
        print("There remain unperformed performance computation jobs! Please run: "
              "'sparkle run solvers --performance-data'")
    if missing_features or missing_performances:
        print("Please first execute all unperformed jobs before constructing Sparkle "
              "portfolio selector")
        print("Sparkle portfolio selector is not successfully constructed!")
        sys.exit(-1)


def main(argv: list[str]) -> None:
    """Main method of construct portfolio selector."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    flag_recompute_portfolio = args.recompute_portfolio_selector
    solver_ablation = args.solver_ablation

    if ac.set_by_user(args, "settings_file"):
        # Do first, so other command line options can override settings from the file
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if ac.set_by_user(args, "objective"):
        objective = resolve_objective(args.objective)
    else:
        objective = gv.settings().get_general_sparkle_objectives()[0]
        print("WARNING: No objective specified, defaulting to first objective from "
              f"settings ({objective}).")
    if args.run_on is not None:
        gv.settings().set_run_on(args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    print("Start constructing Sparkle portfolio selector ...")
    selector = Selector(gv.settings().get_selection_class(),
                        gv.settings().get_selection_model())

    instance_set = None
    if args.instance_set_train is not None:
        instance_set = resolve_object_name(
            args.instance_set_train,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            gv.settings().DEFAULT_instance_dir, Instance_Set)

    cutoff_time = gv.settings().get_general_target_cutoff_time()

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    if instance_set is not None:
        applicable_instances = [str(i) for i in instance_set.instance_paths]
        removable_instances = [i for i in performance_data.instances
                               if i not in applicable_instances]
        performance_data.remove_instances(removable_instances)
        feature_data.remove_instances(removable_instances)

    judge_exist_remaining_jobs(feature_data, performance_data)

    # TODO Allow user to select solvers to construct over
    # TODO: Filter solvers/configurations that do not meet
    # TODO: And only then call judge exist remaining jobs
    # minimum marginal contribution on training set
    # Selector is named after the solvers it can predict, sort for permutation invariance
    solvers = sorted([str(s) for s in gv.settings().DEFAULT_solver_dir.iterdir()])

    if feature_data.has_missing_value():
        print("WARNING: Missing values in the feature data, will be imputed as the mean "
              "value of all other non-missing values! Imputing all missing values...")
        feature_data.impute_missing_values()

    # Check what configurations should be considered
    if args.best_configuration:
        configurations = {s: performance_data.best_configuration(s, objective=objective)
                          for s in solvers}
    elif args.default_configuration:
        configurations = {s: PerformanceDataFrame.default_configuration for s in solvers}
    else:
        configurations = {s: performance_data.get_configurations(s) for s in solvers}
        if not args.all_configurations:  # Take the only configuration
            if any(len(c) > 1 for c in configurations.values()):
                print("ERROR: More than one configuration for the following solvers:")
                for solver, config in configurations.items():
                    if len(config) > 1:
                        print(f"\t{solver}: {config} configurations")
                raise ValueError(
                    "Cannot construct portfolio selector with single configuration per "
                    "solver. Specify all_solver_configurations flag to construct the "
                    "portfolio selector with all configurations, or the "
                    "best-configuration flag to construct the portfolio selector with "
                    "the best configuration per solver. Set the default-configuration "
                    "flag to construct the portfolio selector with the default "
                    "configuration per solver."
                )
    # TODO: Filter configurations from performance dataframe
    selection_scenario_path =\
        gv.settings().DEFAULT_selection_output / selector.name / "_".join(solvers)

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
    slurm_prepend = gv.settings().get_slurm_job_prepend()
    selector_run = selector.construct(selector_path,
                                      performance_data,
                                      feature_data,
                                      objective,
                                      cutoff_time,
                                      run_on=run_on,
                                      sbatch_options=sbatch_options,
                                      slurm_prepend=slurm_prepend,
                                      base_dir=sl.caller_log_dir)
    if run_on == Runner.LOCAL:
        print("Sparkle portfolio selector constructed!")
    else:
        print("Sparkle portfolio selector constructor running...")

    dependencies = [selector_run]
    if solver_ablation:
        for solver in performance_data.solvers:
            for config_id in performance_data.get_configurations(solver):
                solver_name = Path(solver).name
                ablate_solver_dir =\
                    selection_scenario_path / f"ablate_{solver_name}_{config_id}"
                ablate_solver_selector = ablate_solver_dir / "portfolio_selector"
                if (ablate_solver_selector.exists() and not flag_recompute_portfolio):
                    print(f"Portfolio selector without {solver_name} already exists. "
                          "Set the recompute flag to re-create.")
                    continue
                ablate_solver_dir.mkdir(exist_ok=True, parents=True)
                ablated_performance_data = performance_data.clone()
                ablated_performance_data.remove_configuration(solver, config_id)
                ablated_run = selector.construct(
                    ablate_solver_selector,
                    ablated_performance_data,
                    feature_data,
                    objective,
                    cutoff_time,
                    run_on=run_on,
                    job_name=f"Construct Selector: Ablate {solver_name} ({config_id})",
                    sbatch_options=sbatch_options,
                    slurm_prepend=slurm_prepend,
                    base_dir=sl.caller_log_dir)
                dependencies.append(ablated_run)
                if run_on == Runner.LOCAL:
                    print("Portfolio selector without "
                          f"{solver_name} ({config_id}) constructed!")
                else:
                    print("Portfolio selector without "
                          f"{solver_name} ({config_id}) constructor running...")

    # Compute the marginal contribution
    with_actual = "--actual" if solver_ablation else ""
    cmd = (f"python3 sparkle/CLI/compute_marginal_contribution.py --perfect "
           f"{with_actual} {ac.ObjectivesArgument.names[0]} {objective}")
    solver_names = ", ".join([Path(s).name for s in performance_data.solvers])
    marginal_contribution = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd,
        name=f"Marginal Contribution computation: {solver_names}",
        base_dir=sl.caller_log_dir,
        dependencies=dependencies,
        sbatch_options=sbatch_options,
        prepend=gv.settings().get_slurm_job_prepend())
    dependencies.append(marginal_contribution)
    if run_on == Runner.LOCAL:
        marginal_contribution.wait()
        print("Selector marginal contribution computing done!")
    else:
        print(f"Running selector construction through Slurm with job id(s): "
              f"{', '.join([d.run_id for d in dependencies])}")

    # Write used settings to file
    gv.settings().write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
