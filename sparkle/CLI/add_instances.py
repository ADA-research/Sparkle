#!/usr/bin/env python3
"""Sparkle command to add an instance set to the Sparkle platform."""

import sys
import argparse
from pathlib import Path
import shutil

from sparkle.CLI.help import global_variables as gv
from sparkle.platform import file_help as sfh
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.instance import InstanceSet
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.CLI.compute_features import compute_features
from sparkle.CLI.run_solvers import running_solvers_performance_data
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.CLI.help import command_help as ch
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as apc


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*apc.InstancesPathArgument.names,
                        **apc.InstancesPathArgument.kwargs)
    group_extractor_run = parser.add_mutually_exclusive_group()
    group_extractor_run.add_argument(*apc.RunExtractorNowArgument.names,
                                     **apc.RunExtractorNowArgument.kwargs)
    group_extractor_run.add_argument(*apc.RunExtractorLaterArgument.names,
                                     **apc.RunExtractorLaterArgument.kwargs)
    group_solver = parser.add_mutually_exclusive_group()
    group_solver.add_argument(*apc.RunSolverNowArgument.names,
                              **apc.RunSolverNowArgument.kwargs)
    group_solver.add_argument(*apc.RunSolverLaterArgument.names,
                              **apc.RunSolverLaterArgument.kwargs)
    parser.add_argument(*apc.NicknameInstanceSetArgument.names,
                        **apc.NicknameInstanceSetArgument.kwargs)
    parser.add_argument(*apc.RunOnArgument.names,
                        **apc.RunOnArgument.kwargs)

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    settings = Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instances_source = Path(args.instances_path)
    instances_target = gv.settings.DEFAULT_instance_dir / instances_source.name

    if args.run_on is not None:
        settings.set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = settings.get_run_on()

    check_for_initialise(ch.COMMAND_DEPENDENCIES[ch.CommandName.ADD_INSTANCES])

    if not instances_source.exists():
        print(f'Instance set path "{instances_source}" does not exist!')
        sys.exit(-1)
    if instances_target.exists():
        print(f'Instance set "{instances_source.name}" already exists in Sparkle! '
              "Exiting...")
        sys.exit(-1)
    if args.nickname is not None:
        sfh.add_remove_platform_item(instances_target,
                                     gv.instances_nickname_path, key=args.nickname)

    print(f"Start adding all instances in directory {instances_source} ...")
    instance_set = InstanceSet(instances_source)

    instances_target.mkdir(parents=True)
    print("Copying files...")
    for instance_path_source in instance_set.all_paths:
        print(f"Copying {instance_path_source} to {instances_target}...", end="\r")
        shutil.copy(instance_path_source, instances_target)
    print("Copying done!")
    # Refresh the instance set as the target instance set
    instance_set = InstanceSet(instances_target)

    # Add the instances to the Feature Data / Performance Data
    feature_data = FeatureDataFrame(gv.settings.DEFAULT_feature_data_path)
    # When adding instances, an empty performance DF has no objectives yet
    performance_data = PerformanceDataFrame(
        gv.settings.DEFAULT_performance_data_path,
        objectives=settings.get_general_sparkle_objectives())
    for instance_path in instance_set.get_instance_paths:
        # Construct a name path due to multi-file instances
        feature_data.add_instance(str(instance_path))
        performance_data.add_instance(str(instance_path))
    feature_data.save_csv()
    performance_data.save_csv()

    print(f"\nAdding instance set {instance_set.name} done!")

    if gv.settings.DEFAULT_algorithm_selector_path.exists():
        gv.settings.DEFAULT_algorithm_selector_path.unlink()
        print("Removing Sparkle portfolio selector "
              f"{gv.settings.DEFAULT_algorithm_selector_path} done!")

    if args.run_extractor_now:
        print("Start computing features ...")
        compute_features(gv.settings.DEFAULT_feature_data_path, False)

    if args.run_solver_now:
        num_job_in_parallel = settings.get_number_of_jobs_in_parallel()
        running_solvers_performance_data(gv.settings.DEFAULT_performance_data_path,
                                         num_job_in_parallel,
                                         rerun=False, run_on=run_on)
        print("Running solvers...")

    # Write used settings to file
    settings.write_used_settings()
