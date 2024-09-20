#!/usr/bin/env python3
"""Sparkle command to add an instance set to the Sparkle platform."""

import sys
import argparse
from pathlib import Path
import shutil

from sparkle.CLI.help import global_variables as gv
from sparkle.platform import file_help as sfh
from sparkle.platform.settings_objects import SettingState
from sparkle.instance import instance_set
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.CLI.compute_features import compute_features
from sparkle.CLI.run_solvers import running_solvers_performance_data
from sparkle.CLI.help import logging as sl
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancesPathArgument.names,
                        **ac.InstancesPathArgument.kwargs)
    parser.add_argument(*ac.RunExtractorNowArgument.names,
                        **ac.RunExtractorNowArgument.kwargs)
    parser.add_argument(*ac.RunSolverNowArgument.names,
                        **ac.RunSolverNowArgument.kwargs)
    parser.add_argument(*ac.NicknameInstanceSetArgument.names,
                        **ac.NicknameInstanceSetArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instances_source = Path(args.instances_path)
    instances_target = gv.settings().DEFAULT_instance_dir / instances_source.name

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.ADD_INSTANCES])

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
    new_instance_set = instance_set(instances_source)

    instances_target.mkdir(parents=True)
    print("Copying files...")
    for instance_path_source in new_instance_set.all_paths:
        print(f"Copying {instance_path_source} to {instances_target}...", end="\r")
        shutil.copy(instance_path_source, instances_target)
    print("\nCopying done!")
    # Refresh the instance set as the target instance set
    new_instance_set = instance_set(instances_target)

    # Add the instances to the Feature Data / Performance Data
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
    # When adding instances, an empty performance DF has no objectives yet
    performance_data = PerformanceDataFrame(
        gv.settings().DEFAULT_performance_data_path,
        objectives=gv.settings().get_general_sparkle_objectives())
    for instance_path in new_instance_set.instance_paths:
        # Construct a name path due to multi-file instances
        feature_data.add_instances(str(instance_path))
        performance_data.add_instance(str(instance_path))
    feature_data.save_csv()
    performance_data.save_csv()

    print(f"\nAdding instance set {new_instance_set.name} done!")

    if args.run_extractor_now:
        print("Start computing features ...")
        compute_features(gv.settings().DEFAULT_feature_data_path, False)

    if args.run_solver_now:
        num_job_in_parallel = gv.settings().get_number_of_jobs_in_parallel()
        running_solvers_performance_data(gv.settings().DEFAULT_performance_data_path,
                                         num_job_in_parallel,
                                         rerun=False, run_on=run_on)
        print("Running solvers...")

    # Write used settings to file
    gv.settings().write_used_settings()
