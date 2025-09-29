#!/usr/bin/env python3
"""Sparkle command to construct a portfolio selector."""

import sys
import argparse

from runrunner.base import Runner

from sparkle.selector import Selector, SelectionScenario
from sparkle.instance import Instance_Set

from sparkle.platform.settings_objects import Settings
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types import resolve_objective
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name, resolve_instance_name
from sparkle.CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to construct a portfolio selector over all known features "
        "solver performances."
    )
    parser.add_argument(*ac.SolversArgument.names, **ac.SolversArgument.kwargs)
    parser.add_argument(
        *ac.RecomputePortfolioSelectorArgument.names,
        **ac.RecomputePortfolioSelectorArgument.kwargs,
    )
    parser.add_argument(*ac.ObjectiveArgument.names, **ac.ObjectiveArgument.kwargs)
    parser.add_argument(
        *ac.SelectorAblationArgument.names, **ac.SelectorAblationArgument.kwargs
    )
    parser.add_argument(
        *ac.InstanceSetTrainOptionalArgument.names,
        **ac.InstanceSetTrainOptionalArgument.kwargs,
    )
    # Solver Configurations arguments
    configuration_group = parser.add_mutually_exclusive_group(required=False)
    configuration_group.add_argument(
        *ac.AllSolverConfigurationArgument.names,
        **ac.AllSolverConfigurationArgument.kwargs,
    )
    configuration_group.add_argument(
        *ac.BestSolverConfigurationArgument.names,
        **ac.BestSolverConfigurationArgument.kwargs,
    )
    configuration_group.add_argument(
        *ac.DefaultSolverConfigurationArgument.names,
        **ac.DefaultSolverConfigurationArgument.kwargs,
    )
    # TODO: Allow user to specify configuration ids to use
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(
        *Settings.OPTION_minimum_marginal_contribution.args,
        **Settings.OPTION_minimum_marginal_contribution.kwargs,
    )
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    return parser


def judge_exist_remaining_jobs(
    feature_data: FeatureDataFrame, performance_data: PerformanceDataFrame
) -> bool:
    """Return whether there are remaining feature or performance computation jobs."""
    missing_features = feature_data.has_missing_vectors()
    missing_performances = performance_data.has_missing_values
    if missing_features:
        print(
            "There remain unperformed feature computation jobs! Please run: "
            "'sparkle compute features'"
        )
    if missing_performances:
        print(
            "There remain unperformed performance computation jobs! Please run:\n"
            "'sparkle cleanup --performance-data'\n"
            "to check for missing values in the logs, otherwise run:\n"
            "'sparkle run solvers --performance-data'\n"
            "to compute missing values."
        )
    if missing_features or missing_performances:
        print(
            "Please first execute all unperformed jobs before constructing Sparkle "
            "portfolio selector."
        )
        sys.exit(-1)


def main(argv: list[str]) -> None:
    """Main method of construct portfolio selector."""
    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, settings.random_state)
    check_for_initialise()

    flag_recompute_portfolio = args.recompute_portfolio_selector
    solver_ablation = args.solver_ablation

    if args.objective is not None:
        objective = resolve_objective(args.objective)
    else:
        objective = settings.objectives[0]
        print(
            "WARNING: No objective specified, defaulting to first objective from "
            f"settings ({objective})."
        )
    run_on = settings.run_on

    print("Start constructing Sparkle portfolio selector ...")
    selector = Selector(settings.selection_class, settings.selection_model)

    instance_set = None
    if args.instance_set_train is not None:
        instance_set = resolve_object_name(
            args.instance_set_train,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            gv.settings().DEFAULT_instance_dir,
            Instance_Set,
        )

    solver_cutoff_time = gv.settings().solver_cutoff_time
    extractor_cutoff_time = gv.settings().extractor_cutoff_time

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    # Check that the feature data actually contains features (extractors)
    if feature_data.num_features == 0:
        print(
            "ERROR: Feature data is empty! Please add a feature extractor and run "
            "'sparkle compute features' first."
        )
        sys.exit(-1)

    # Filter objective
    performance_data.remove_objective(
        [obj for obj in performance_data.objective_names if obj != objective.name]
    )
    if instance_set is not None:
        removable_instances = [
            i for i in performance_data.instances if i not in instance_set.instance_names
        ]
        performance_data.remove_instances(removable_instances)
        feature_data.remove_instances(removable_instances)

    if args.solvers is not None:
        solvers = args.solvers
        removeable_solvers = [s for s in performance_data.solvers if s not in solvers]
        performance_data.remove_solver(removeable_solvers)
    else:
        solvers = sorted(
            [str(s) for s in gv.settings().DEFAULT_solver_dir.iterdir() if s.is_dir()]
        )

    # Check what configurations should be considered
    if args.best_configuration:
        configurations = {
            s: performance_data.best_configuration(s, objective=objective)
            for s in solvers
        }
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
                    "Please set the --all-configurations flag if you wish to use more "
                    "than one configuration per solver."
                )
    for solver in solvers:
        removeable_configs = [
            c
            for c in performance_data.get_configurations(solver)
            if c not in configurations[solver]
        ]
        performance_data.remove_configuration(solver, removeable_configs)

    judge_exist_remaining_jobs(feature_data, performance_data)
    if feature_data.has_missing_value():
        print(
            "WARNING: Missing values in the feature data, will be imputed as the mean "
            "value of all other non-missing values! Imputing all missing values..."
        )
        feature_data.impute_missing_values()

    # Filter the scenario from Solver (Configurations) that do not meet the minimum marginal contribution on the training set
    if gv.settings().minimum_marginal_contribution > 0.0:
        print(
            f"Filtering the scenario from Solver (Configurations) with contribution < {gv.settings().minimum_marginal_contribution} ..."
        )
        for (
            solver,
            config_id,
            marginal_contribution,
            _,
        ) in performance_data.marginal_contribution(objective=objective):
            if marginal_contribution < gv.settings().minimum_marginal_contribution:
                print(f"\tRemoving {solver}, {config_id} [{marginal_contribution}]")
                performance_data.remove_configuration(solver, config_id)

    selection_scenario = SelectionScenario(
        gv.settings().DEFAULT_selection_output,
        selector,
        objective,
        performance_data,
        feature_data,
        solver_cutoff=solver_cutoff_time,
        extractor_cutoff=extractor_cutoff_time,
        ablate=solver_ablation,
    )

    if selection_scenario.selector_file_path.exists():
        if not flag_recompute_portfolio:
            print(
                "Portfolio selector already exists. "
                "Set the recompute flag to remove and reconstruct."
            )
            sys.exit(-1)
        # Delete all selectors
        selection_scenario.selector_file_path.unlink(missing_ok=True)
        if selection_scenario.ablation_scenarios:
            for scenario in selection_scenario.ablation_scenarios:
                scenario.selector_file_path.unlink(missing_ok=True)

    sbatch_options = gv.settings().sbatch_settings
    slurm_prepend = gv.settings().slurm_job_prepend
    selector_run = selector.construct(
        selection_scenario,
        run_on=run_on,
        sbatch_options=sbatch_options,
        slurm_prepend=slurm_prepend,
        base_dir=sl.caller_log_dir,
    )
    jobs = [selector_run]
    if run_on == Runner.LOCAL:
        print("Sparkle portfolio selector constructed!")
    else:
        print("Sparkle portfolio selector constructor running...")

    # Validate the selector to run on the given instances
    instances = [
        resolve_instance_name(instance, Settings.DEFAULT_instance_dir)
        for instance in performance_data.instances
    ]
    selector_validation = selector.run_cli(
        selection_scenario.scenario_file,
        instances,
        feature_data.csv_filepath,
        run_on=run_on,
        sbatch_options=sbatch_options,
        slurm_prepend=slurm_prepend,
        dependencies=[selector_run],
        log_dir=sl.caller_log_dir,
    )
    jobs.append(selector_validation)

    if solver_ablation:
        for ablated_scenario in selection_scenario.ablation_scenarios:
            # Construct the ablated selector
            ablation_run = selector.construct(
                ablated_scenario,
                run_on=run_on,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                base_dir=sl.caller_log_dir,
            )
            # Validate the ablated selector
            ablation_validation = selector.run_cli(
                ablated_scenario.scenario_file,
                instances,
                feature_data.csv_filepath,
                run_on=run_on,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                job_name=f"Selector Ablation: {ablated_scenario.directory.name} on {len(instances)} instances",
                dependencies=[ablation_run],
                log_dir=sl.caller_log_dir,
            )
            jobs.extend([ablation_run, ablation_validation])

    if run_on == Runner.LOCAL:
        for job in jobs:
            job.wait()
        selector_validation.wait()
        print("Selector validation done!")
    else:
        print(
            f"Running selector construction through Slurm with job id(s): "
            f"{', '.join([d.run_id for d in jobs])}"
        )

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
