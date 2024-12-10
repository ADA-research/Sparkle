#!/usr/bin/env python3
"""Sparkle command to configure a solver."""
from __future__ import annotations
import argparse
import sys
import os
import math

from pandas import DataFrame

from runrunner import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.CLI.help import argparse_custom as ac

from sparkle.platform.settings_objects import SettingState
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.configurator import implementations as configurator_implementations
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
    parser.add_argument(*ac.TargetCutOffTimeArgument.names,
                        **ac.TargetCutOffTimeArgument.kwargs)
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
    if args.target_cutoff_time is not None:
        gv.settings().set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)
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

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    apply_settings_from_args(args)

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

    check_for_initialise()

    configurator = gv.settings().get_general_sparkle_configurator()
    configurator_settings = gv.settings().get_configurator_settings(configurator.name)
    if use_features and configurator.name == configurator_implementations.SMAC2.__name__:
        feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

        data_dict = {}
        feature_data_df = feature_data.dataframe

        for label, row in feature_data_df.iterrows():
            # os.path.split(os.path.split(label)[0])[1] gives the dir/instance set name
            if os.path.split(os.path.split(label)[0])[1] == instance_set_train.name:
                if row.empty:
                    print("No feature data exists for the given training set, please "
                          "run add_feature_extractor.py, then compute_features.py")
                    sys.exit(-1)

                new_label = (f"../../../instances/{instance_set_train.name}/"
                             + os.path.split(label)[1])
                data_dict[new_label] = row

        feature_data_df = DataFrame.from_dict(data_dict, orient="index",
                                              columns=feature_data_df.columns)

        if feature_data.has_missing_value():
            print("You have unfinished feature computation jobs, please run "
                  "`sparkle compute features`")
            sys.exit(-1)

        for index, column in enumerate(feature_data_df):
            feature_data_df.rename(columns={column: f"Feature{index+1}"}, inplace=True)
        configurator_settings.update({"feature_data_df": feature_data_df})

    sparkle_objectives =\
        gv.settings().get_general_sparkle_objectives()
    configurator_runs = gv.settings().get_configurator_number_of_runs()
    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)

    # Check if given objectives are in the data frame
    for objective in sparkle_objectives:
        if objective.name not in performance_data.objective_names:
            print(f"WARNING: Objective {objective.name} not found in performance data. "
                  "Adding to data frame.")
            performance_data.add_objective(objective.name)

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    config_scenario = configurator.scenario_class()(
        solver, instance_set_train, sparkle_objectives,
        configurator.output_path, **configurator_settings)

    # Run the default configuration
    remaining_jobs = performance_data.get_job_list()
    relevant_jobs = []
    for job in remaining_jobs:
        if job[-1] != str(solver.directory):
            continue
        configuration = performance_data.get_value(
            job[2], job[0], sparkle_objectives[0].name, run=job[1],
            solver_fields=[PerformanceDataFrame.column_configuration])
        # Only run jobs with the default configuration
        if not isinstance(configuration, str) and math.isnan(configuration):
            relevant_jobs.append(job)

    # Expand the performance dataframe so it can store the configuration
    performance_data.add_runs(configurator_runs,
                              instance_names=[
                                  str(i) for i in instance_set_train.instance_paths])
    if instance_set_test is not None:
        # Expand the performance dataframe so it can store the test set results of the
        # found configurations
        test_set_runs = configurator_runs if args.test_set_run_all_configurations else 1
        performance_data.add_runs(
            test_set_runs,
            instance_names=[str(i) for i in instance_set_test.instance_paths])
    performance_data.save_csv()

    dependency_job_list = configurator.configure(
        scenario=config_scenario,
        data_target=performance_data,
        sbatch_options=sbatch_options,
        num_parallel_jobs=gv.settings().get_number_of_jobs_in_parallel(),
        base_dir=sl.caller_log_dir,
        run_on=run_on)

    # If we have default configurations that need to be run, schedule them too
    if len(relevant_jobs) > 0:
        instances = [job[0] for job in relevant_jobs]
        runs = list(set([job[1] for job in relevant_jobs]))
        default_job = solver.run_performance_dataframe(
            instances, runs, performance_data,
            sbatch_options=sbatch_options,
            cutoff_time=config_scenario.cutoff_time,
            log_dir=config_scenario.validation,
            base_dir=sl.caller_log_dir,
            run_on=run_on)
        dependency_job_list.append(default_job)

    # Update latest scenario
    gv.latest_scenario().set_config_solver(solver)
    gv.latest_scenario().set_config_instance_set_train(instance_set_train.directory)
    gv.latest_scenario().set_configuration_scenario(config_scenario.scenario_file_path)
    gv.latest_scenario().set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        gv.latest_scenario().set_config_instance_set_test(instance_set_test.directory)
        # Schedule test set jobs
        if args.test_set_run_all_configurations:
            pass
        else:
            # We place the results in the index we just added
            run_index = list(set([performance_data.get_instance_num_runs(str(i))
                                  for i in instance_set_test.instance_paths]))
        test_set_job = solver.run_performance_dataframe(
            instance_set_test,
            run_index,
            performance_data,
            cutoff_time=config_scenario.cutoff_time,
            objective=config_scenario.sparkle_objective,
            train_set=instance_set_train,
            sbatch_options=sbatch_options,
            log_dir=config_scenario.validation,
            base_dir=sl.caller_log_dir,
            dependencies=dependency_job_list,
            run_on=run_on)
        dependency_job_list.append(test_set_job)
    else:
        # Set to default to overwrite possible old path
        gv.latest_scenario().set_config_instance_set_test()

    if run_on == Runner.SLURM:
        job_id_str = ",".join([run.run_id for run in dependency_job_list])
        print(f"Running configuration. Waiting for Slurm job(s) with id(s): "
              f"{job_id_str}")
    else:
        print("Running configuration finished!")

    # Write used settings to file
    gv.settings().write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
