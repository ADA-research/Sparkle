#!/usr/bin/env python3
"""Sparkle command to remove an instance set from the Sparkle platform."""

import sys
import argparse
import shutil

from sparkle.CLI.help import global_variables as gv
from sparkle.platform import file_help as sfh
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.instance import Instance_Set
from sparkle.CLI.help import logging as sl
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Remove instances from the platform.")
    parser.add_argument(*ac.InstancesPathRemoveArgument.names,
                        **ac.InstancesPathRemoveArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the remove instances command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    instances_path = resolve_object_name(
        args.instances_path,
        nickname_dict=gv.file_storage_data_mapping[gv.instances_nickname_path],
        target_dir=gv.settings().DEFAULT_instance_dir)

    if instances_path is None or not instances_path.exists() or not\
            instances_path.is_dir():
        print(f'Could not resolve instances path arg "{args.instances_path}"!')
        print("Check that the path or nickname is spelled correctly.")
        sys.exit(-1)

    print(f"Start removing all instances in directory {instances_path} ...")
    old_instance_set = Instance_Set(instances_path)
    # Remove from feature data and performance data
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    for instance in old_instance_set.instance_paths:
        feature_data.remove_instances(str(instance))
        performance_data.remove_instance(str(instance))

    feature_data.save_csv()
    performance_data.save_csv()

    # Remove nickname, if it exists
    instances_nicknames = gv.file_storage_data_mapping[gv.instances_nickname_path]
    for key in instances_nicknames:
        if instances_nicknames[key] == instances_path:
            sfh.add_remove_platform_item(instances_path,
                                         gv.instances_nickname_path,
                                         key=key, remove=True)
            break

    # We unlink symbolics links, erase copies
    if instances_path.is_symlink():
        instances_path.unlink()
    else:
        # Remove the directory and all its files
        shutil.rmtree(instances_path)

    print(f"Removing instances set {instances_path.name} done!")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
