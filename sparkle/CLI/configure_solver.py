#!/usr/bin/env python3
"""Sparkle command to configure a solver."""
from __future__ import annotations
from pathlib import Path
import argparse
import sys

from runrunner import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name, resolve_instance_name
from sparkle.CLI.help import argparse_custom as ac

from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.solver import Solver
from sparkle.instance import Instance_Set


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure a solver in the platform.",
        epilog=("Note that the test instance set is only used if the ``--ablation``"
                " or ``--validation`` flags are given"))
    parser.add_argument(*ac.ConfiguratorArgument.names,
                        **ac.ConfiguratorArgument.kwargs)
    parser.add_argument(*ac.SolverArgument.names,
                        **ac.SolverArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTrainArgument.names,
                        **ac.InstanceSetTrainArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTestArgument.names,
                        **ac.InstanceSetTestArgument.kwargs)
    parser.add_argument(*ac.TestSetRunAllConfigurationArgument.names,
                        **ac.TestSetRunAllConfigurationArgument.kwargs)
    parser.add_argument(*ac.ObjectivesArgument.names,
                        **ac.ObjectivesArgument.kwargs)
    parser.add_argument(*ac.SolverCutOffTimeArgument.names,
                        **ac.SolverCutOffTimeArgument.kwargs)
    parser.add_argument(*ac.SolverCallsArgument.names,
                        **ac.SolverCallsArgument.kwargs)
    parser.add_argument(*ac.NumberOfRunsConfigurationArgument.names,
                        **ac.NumberOfRunsConfigurationArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.UseFeaturesArgument.names,
                        **ac.UseFeaturesArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    return parser


def apply_settings_from_args(args: argparse.Namespace) -> None:
    """Apply command line arguments to settings.

    Args:
        args: Arguments object created by ArgumentParser.
    """
    if args.settings_file is not None:
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.configurator is not None:
        gv.settings().set_general_sparkle_configurator(
            args.configurator, SettingState.CMD_LINE)
    if args.objectives is not None:
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE)
    if args.solver_cutoff_time is not None:
        gv.settings().set_general_solver_cutoff_time(
            args.solver_cutoff_time, SettingState.CMD_LINE)
    if args.solver_calls is not None:
        gv.settings().set_configurator_solver_calls(
            args.solver_calls, SettingState.CMD_LINE)
    if args.number_of_runs is not None:
        gv.settings().set_configurator_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE)
    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)


def main(argv: list[str]) -> None:
    """Main function of the configure solver command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    apply_settings_from_args(args)

    configurator = gv.settings().get_general_sparkle_configurator()

    # Check configurator is available
    if not configurator.check_requirements(verbose=True):
        print(f"{configurator.name} is not available. "
              "Please inspect possible warnings above.")
        print(f"Would you like to install {configurator.name}? (Y/n)")
        if input().lower().strip() == "y":
            configurator.download_requirements()
        else:
            sys.exit()
        if not configurator.check_requirements(verbose=True):
            raise RuntimeError(f"Failed to install {configurator.name}.")
        sys.exit(-1)

    # Compare current settings to latest.ini
    prev_settings = Settings(Path(Settings.DEFAULT_previous_settings_path))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    solver: Solver = resolve_object_name(
        args.solver,
        gv.file_storage_data_mapping[gv.solver_nickname_list_path],
        gv.settings().DEFAULT_solver_dir, class_name=Solver)
    if solver is None:
        raise ValueError(f"Solver {args.solver} not found.")
    instance_set_train = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, Instance_Set)
    if instance_set_train is None:
        raise ValueError(f"Instance set {args.instance_set_train} not found.")
    instance_set_test = args.instance_set_test
    if instance_set_test is not None:
        instance_set_test = resolve_object_name(
            args.instance_set_test,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            gv.settings().DEFAULT_instance_dir, Instance_Set)
    use_features = args.use_features
    run_on = gv.settings().get_run_on()

    configurator_settings = gv.settings().get_configurator_settings(configurator.name)

    sparkle_objectives =\
        gv.settings().get_general_sparkle_objectives()
    if len(sparkle_objectives) > 1:
        print(f"WARNING: {configurator.name} does not have multi objective support. "
              f"Only the first objective ({sparkle_objectives[0]}) will be optimised.")

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)

    # Check if given objectives are in the data frame
    for objective in sparkle_objectives:
        if objective.name not in performance_data.objective_names:
            print(f"WARNING: Objective {objective.name} not found in performance data. "
                  "Adding to data frame.")
            performance_data.add_objective(objective.name)

    if use_features:
        feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
        # Check that the train instance set is in the feature data frame
        invalid = False
        remaining_instance_jobs =\
            set([instance for instance, _, _ in feature_data.remaining_jobs()])
        for instance in instance_set_train.instance_paths:
            if str(instance) not in feature_data.instances:
                print(f"ERROR: Train Instance {instance} not found in feature data.")
                invalid = True
            elif instance in remaining_instance_jobs:  # Check jobs
                print(f"ERROR: Features have not been computed for instance {instance}.")
                invalid = True
        if invalid:
            sys.exit(-1)
        configurator_settings.update({"feature_data": feature_data})

    number_of_runs = gv.settings().get_configurator_number_of_runs()
    output_path = gv.settings().get_configurator_output_path(configurator)
    config_scenario = configurator.scenario_class()(
        solver, instance_set_train, sparkle_objectives, number_of_runs,
        output_path, **configurator_settings)

    # Run the default configuration
    default_jobs = [(solver, config_id, instance, run_id)
                    for solver, config_id, instance, run_id
                    in performance_data.get_job_list()
                    if config_id == PerformanceDataFrame.default_configuration]

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    slurm_prepend = gv.settings().get_slurm_job_prepend()
    dependency_job_list = configurator.configure(
        scenario=config_scenario,
        data_target=performance_data,
        sbatch_options=sbatch_options,
        slurm_prepend=slurm_prepend,
        num_parallel_jobs=gv.settings().get_number_of_jobs_in_parallel(),
        base_dir=sl.caller_log_dir,
        run_on=run_on)

    # If we have default configurations that need to be run, schedule them too
    if default_jobs:
        # Edit jobs to incorporate file paths
        instances = []
        for _, _, instance, _ in default_jobs:
            instance_path = resolve_instance_name(
                instance, gv.settings().DEFAULT_instance_dir)
            instances.append(instance_path)
        default_job = solver.run_performance_dataframe(
            instances, PerformanceDataFrame.default_configuration,
            performance_data,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            cutoff_time=config_scenario.solver_cutoff_time,
            log_dir=config_scenario.validation,
            base_dir=sl.caller_log_dir,
            job_name=f"Default Configuration: {solver.name} Validation on "
                     f"{instance_set_train.name}",
            run_on=run_on)
        dependency_job_list.append(default_job)

    if instance_set_test is not None:
        # Schedule test set jobs
        if args.test_set_run_all_configurations:
            # TODO: Schedule test set runs for all configurations
            print("Running all configurations on test set is not implemented yet.")
            pass
        else:
            # We place the results in the index we just added
            run_index = list(set([performance_data.get_instance_num_runs(str(i))
                                  for i in instance_set_test.instance_names]))
            test_set_job = solver.run_performance_dataframe(
                instance_set_test,
                run_index,
                performance_data,
                cutoff_time=config_scenario.solver_cutoff_time,
                objective=config_scenario.sparkle_objective,
                train_set=instance_set_train,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                log_dir=config_scenario.validation,
                base_dir=sl.caller_log_dir,
                dependencies=dependency_job_list,
                job_name=f"Best Configuration: {solver.name} Validation on "
                         f"{instance_set_test.name}",
                run_on=run_on)
            dependency_job_list.append(test_set_job)

    if run_on == Runner.SLURM:
        job_id_str = ",".join([run.run_id for run in dependency_job_list])
        print(f"Running {configurator.name} configuration through Slurm with job "
              f"id(s): {job_id_str}")
    else:
        print("Running configuration finished!")

    # Write used settings to file
    gv.settings().write_used_settings()
    # Write used scenario to file
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
