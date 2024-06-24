#!/usr/bin/env python3
"""Sparkle command to remove an instance set from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

import global_variables as gv
from sparkle.platform import file_help as sfh
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancesPathRemoveArgument.names,
                        **ac.InstancesPathRemoveArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instances_path = resolve_object_name(args.instances_path,
                                         target_dir=gv.instance_dir)

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_INSTANCES])

    if instances_path is None:
        print(f'Could not resolve instances path arg "{args.instances_path}"!')
        print("Check that the path or nickname is spelled correctly.")
        sys.exit(-1)

    print(f"Start removing all instances in directory {instances_path} ...")
    list_all_filename = sfh.get_list_all_filename_recursive(instances_path)
    reference_list = gv.reference_list_dir / (instances_path.name
                                              + gv.instance_list_postfix)
    if reference_list.exists():
        list_all_filename = reference_list.open("r").read().splitlines()
        # Prepend the instance path to each name
        for i, instance in enumerate(list_all_filename):
            file_names = instance.split(" ")
            list_all_filename[i] = " ".join([f"{instances_path / fname}"
                                             for fname in file_names])

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(gv.feature_data_csv_path,
                                                    gv.extractor_list)
    performance_data_csv = PerformanceDataFrame(gv.performance_data_csv_path)

    for instance_path in list_all_filename:
        intended_instance = str(instance_path)
        print(intended_instance)
        # Remove instance records
        sfh.add_remove_platform_item(intended_instance,
                                     gv.instance_list_path,
                                     gv.file_storage_data_mapping[gv.instance_list_path],
                                     remove=True)
        if reference_list.exists():
            # In case of reference lists, we only take the last instance part
            # For the matrix rows to remove them
            intended_instance = str(instances_path / Path(instance_path).name)
        feature_data_csv.delete_row(intended_instance)
        performance_data_csv.remove_instance(intended_instance)
        print(f"Instance {intended_instance} has been removed from platform!")

    if instances_path.exists() and instances_path.is_dir():
        shutil.rmtree(instances_path)
        print(f"Instance set {instances_path} has been removed!")
    else:
        print(f"Warning: Path {instances_path} did not exist. Continuing")

    # Remove instance reference list (for multi-file instances)
    instance_list_path = Path(gv.reference_list_dir
                              / Path(instances_path.name + gv.instance_list_postfix))
    sfh.rmfiles(instance_list_path)

    feature_data_csv.save_csv()
    performance_data_csv.save_csv()

    if Path(gv.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(gv.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    print(f"Removing instances in directory {instances_path} done!")
