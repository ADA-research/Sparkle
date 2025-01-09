#!/usr/bin/env python3
"""Sparkle command to add an instance set to the Sparkle platform."""

import sys
import argparse
from pathlib import Path
import shutil

from sparkle.CLI.help import global_variables as gv
from sparkle.platform import file_help as sfh
from sparkle.instance import Instance_Set
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.CLI.help import logging as sl

from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Add instances to the platform.")
    parser.add_argument(*ac.InstancesPathArgument.names,
                        **ac.InstancesPathArgument.kwargs)
    parser.add_argument(*ac.NicknameInstanceSetArgument.names,
                        **ac.NicknameInstanceSetArgument.kwargs)
    parser.add_argument(*ac.NoCopyArgument.names,
                        **ac.NoCopyArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the add instances command."""
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()
    check_for_initialise()

    # Process command line arguments
    args = parser.parse_args(argv)
    instances_source = Path(args.instances_path)
    instances_target = gv.settings().DEFAULT_instance_dir / instances_source.name

    if not instances_source.exists():
        print(f'Instance set path "{instances_source}" does not exist!')
        sys.exit(-1)
    if instances_target.exists():
        print(f'Instance set "{instances_source.name}" already exists in Sparkle! '
              "Exiting...")
        sys.exit(-1)
    if args.nickname is not None:
        sfh.add_remove_platform_item(
            instances_target,
            gv.instances_nickname_path,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            key=args.nickname)

    print(f"Start adding all instances in directory {instances_source} ...")
    new_instance_set = Instance_Set(instances_source)

    if args.no_copy:
        print(f"Creating symbolic link from {instances_source} to {instances_target}...")
        instances_target.symlink_to(instances_source.absolute())
    else:
        instances_target.mkdir(parents=True)
        print("Copying files...")
        for instance_path_source in new_instance_set.all_paths:
            print(f"Copying {instance_path_source} to {instances_target}...", end="\r")
            shutil.copy(instance_path_source, instances_target)
        print("\nCopying done!")
    # Refresh the instance set as the target instance set
    new_instance_set = Instance_Set(instances_target)

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

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
