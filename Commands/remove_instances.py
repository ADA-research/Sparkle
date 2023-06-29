#!/usr/bin/env python3
"""Sparkle command to remove an instance set from the Sparkle platform."""

import os
import sys
import argparse
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_instances_help as sih
from Commands.sparkle_help import sparkle_command_help as sch


def parser_function():
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

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.REMOVE_INSTANCES])

    if args.nickname:
        instances_path = "Instances/" + args.nickname
    if not Path(instances_path).exists():
        print(f'Instances path "{instances_path}" does not exist!')
        print("Removing possible leftovers (if any)")

    if instances_path[-1] == "/":
        instances_path = instances_path[:-1]

    print(f"Start removing all instances in directory {instances_path} ...")

    list_all_filename = sfh.get_list_all_filename(instances_path)
    list_instances = sfh.get_instance_list_from_reference(instances_path)

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        sgh.performance_data_csv_path
    )

    for i in range(0, len(list_instances)):
        intended_instance = list_instances[i]

        # Remove instance records
        sgh.instance_list.remove(intended_instance)
        sfh.remove_line_from_file(intended_instance, sgh.instance_list_path)
        feature_data_csv.delete_row(intended_instance)
        performance_data_csv.delete_row(intended_instance)

        # Delete instance file(s)
        for instance_file in intended_instance.split():
            print("Removing instance file", instance_file)
            instance_path = Path(instance_file)
            sfh.rmfile(instance_path)

        print("Instance " + intended_instance + " has been removed!")

    sfh.rmdir(Path(instances_path))

    # Remove instance reference list (for multi-file instances)
    instance_set_name = Path(instances_path).name
    sih.remove_reference_instance_list(instance_set_name)

    # Remove instance set from SMAC directories
    smac_train_instances_path = (
        sgh.smac_dir
        + "/"
        + "example_scenarios/"
        + "instances/"
        + sfh.get_last_level_directory_name(instances_path)
    )
    file_smac_train_instances = (
        sgh.smac_dir
        + "/"
        + "example_scenarios/"
        + "instances/"
        + sfh.get_last_level_directory_name(instances_path)
        + "_train.txt"
    )
    os.system("rm -rf " + smac_train_instances_path)
    os.system("rm -f " + file_smac_train_instances)

    smac_test_instances_path = (
        sgh.smac_dir
        + "/"
        + "example_scenarios/"
        + "instances_test/"
        + sfh.get_last_level_directory_name(instances_path)
    )
    file_smac_test_instances = (
        sgh.smac_dir
        + "/"
        + "example_scenarios/"
        + "instances_test/"
        + sfh.get_last_level_directory_name(instances_path)
        + "_test.txt"
    )
    os.system("rm -rf " + smac_test_instances_path)
    os.system("rm -f " + file_smac_test_instances)

    sfh.write_instance_list()
    feature_data_csv.update_csv()
    performance_data_csv.update_csv()

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        command_line = "rm -f " + sgh.sparkle_algorithm_selector_path
        os.system(command_line)
        print(
            "Removing Sparkle portfolio selector "
            + sgh.sparkle_algorithm_selector_path
            + " done!"
        )

    if Path(sgh.sparkle_report_path).exists():
        command_line = "rm -f " + sgh.sparkle_report_path
        os.system(command_line)
        print("Removing Sparkle report " + sgh.sparkle_report_path + " done!")

    print("Removing instances in directory " + instances_path + " done!")
