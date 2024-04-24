#!/usr/bin/env python3
"""Sparkle command to remove an instance set from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

import global_variables as sgh
from sparkle.platform import file_help as sfh
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
import sparkle_logging as sl
from sparkle.instance import instances_help as sih
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instances_path",
        metavar="instances-path",
        type=str,
        help="path to or nickname of the instance set",
    )
    parser.add_argument(
        "--nickname",
        action="store_true",
        help="if given instances_path is used as a nickname for the instance set",
    )

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instances_path = args.instances_path

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_INSTANCES])

    if args.nickname:
        instances_path = "Instances/" + args.nickname
    if not Path(instances_path).exists():
        print(f'Instances path "{instances_path}" does not exist!')
        print("Removing possible leftovers (if any)")

    if instances_path[-1] == "/":
        instances_path = instances_path[:-1]

    print(f"Start removing all instances in directory {instances_path} ...")
    list_all_filename = sfh.get_list_all_filename_recursive(instances_path)
    list_instances = sfh.get_instance_list_from_reference(instances_path)

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)
    performance_data_csv = PerformanceDataFrame(
        sgh.performance_data_csv_path
    )

    for intended_instance in list_instances:
        # Remove instance records
        sfh.add_remove_platform_item(intended_instance,
                                     sgh.instance_list_path, remove=True)
        feature_data_csv.delete_row(intended_instance)
        performance_data_csv.remove_instance(intended_instance)

        # Delete instance file(s)
        for instance_file in intended_instance.split():
            print(f"Removing instance file {instance_file}")
            sfh.rmfiles(Path(instance_file))

        print(f"Instance {intended_instance} has been removed!")

    if Path(instances_path).exists() and Path(instances_path).is_dir():
        shutil.rmtree(instances_path)
    else:
        print(f"Warning: Path {instances_path} did not exist. Continuing")

    # Remove instance reference list (for multi-file instances)
    instance_set_name = Path(instances_path).name
    sih.remove_reference_instance_list(instance_set_name)

    feature_data_csv.save_csv()
    performance_data_csv.save_csv()

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(sgh.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        shutil.rmtree(sgh.sparkle_report_path)
        print(f"Removing Sparkle report {sgh.sparkle_report_path} done!")

    print(f"Removing instances in directory {instances_path} done!")
