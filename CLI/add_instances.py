#!/usr/bin/env python3
"""Sparkle command to add an instance set to the Sparkle platform."""

import sys
import argparse
from pathlib import Path
import shutil

from CLI.sparkle_help import sparkle_global_help as sgh
from CLI.sparkle_help import sparkle_file_help as sfh
from sparkle.sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.sparkle_help import sparkle_compute_features_help as scf
from CLI.sparkle_help import sparkle_run_solvers_help as srs
from CLI.sparkle_help import sparkle_run_solvers_parallel_help as srsp
from CLI.sparkle_help import sparkle_logging as sl
from CLI.sparkle_help import sparkle_settings
from CLI.sparkle_help import sparkle_instances_help as sih
from CLI.help import sparkle_command_help as sch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instances_path",
        metavar="instances-path",
        type=str,
        help="path to the instance set")
    group_extractor_run = parser.add_mutually_exclusive_group()
    group_extractor_run.add_argument(
        "--run-extractor-now",
        default=False,
        action="store_true",
        help="immediately run the feature extractor(s) on the newly added instances")
    group_extractor_run.add_argument(
        "--run-extractor-later",
        dest="run_extractor_now",
        action="store_false",
        help=("do not immediately run the feature extractor(s) "
              + "on the newly added instances (default)"))
    group_solver = parser.add_mutually_exclusive_group()
    group_solver.add_argument(
        "--run-solver-now",
        default=False,
        action="store_true",
        help="immediately run the solver(s) on the newly added instances")
    group_solver.add_argument(
        "--run-solver-later",
        dest="run_solver_now",
        action="store_false",
        help=("do not immediately run the solver(s) "
              + "on the newly added instances (default)"))
    parser.add_argument(
        "--nickname", type=str, help="set a nickname for the instance set")
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the solvers and feature extractor on multiple instances in parallel")

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instances_source = args.instances_path

    check_for_initialise(sys.argv,
                         sch.COMMAND_DEPENDENCIES[sch.CommandName.ADD_INSTANCES])

    if not Path(instances_source).exists():
        print(f'Instance set path "{instances_source}" does not exist!')
        sys.exit(-1)

    nickname_str = args.nickname

    print(f"Start adding all instances in directory {instances_source} ...")

    last_level_directory = ""
    if nickname_str is not None:
        last_level_directory = nickname_str
    else:
        last_level_directory = Path(instances_source).name

    instances_directory = sgh.instance_dir / last_level_directory
    if not instances_directory.exists():
        instances_directory.mkdir(parents=True, exist_ok=True)

    if sih._check_existence_of_instance_list_file(instances_source):
        sih._copy_instance_list_to_reference(Path(instances_source))
        list_instance = sih._get_list_instance(instances_source)

        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)
        performance_data_csv = PerformanceDataFrame(sgh.performance_data_csv_path)

        print(f"Number of instances to be added: {len(list_instance)}")

        for instance_line in list_instance:
            instance_related_files = instance_line.strip().split()
            intended_instance_line = ""

            for related_file_name in instance_related_files:
                source_file_path = Path(instances_source) / related_file_name
                target_file_path = instances_directory / related_file_name
                shutil.copy(source_file_path, target_file_path)
                intended_instance_line += str(target_file_path) + " "

            intended_instance_line = intended_instance_line.strip()
            sfh.add_remove_platform_item(intended_instance_line, sgh.instance_list_path)
            feature_data_csv.add_row(intended_instance_line)
            performance_data_csv.add_instance(intended_instance_line)

            print(f"Instance {instance_line} has been added!\n")

        feature_data_csv.save_csv()
        performance_data_csv.save_csv()
    else:
        list_source_all_filename = sfh.get_list_all_filename_recursive(instances_source)
        target_all_filename = sfh.get_list_all_filename_recursive(instances_directory)

        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)
        performance_data_csv = PerformanceDataFrame(sgh.performance_data_csv_path)

        num_inst = len(list_source_all_filename)

        print(f"Number of instances to be added: {str(num_inst)}")
        for i, intended_filename in enumerate(list_source_all_filename):
            print("")
            print(f"Adding {intended_filename.name} ... "
                  f"({str(i + 1)} out of {str(num_inst)})")

            if intended_filename in target_all_filename:
                print(f"Instance {intended_filename.name} already exists in Directory "
                      f"{instances_directory}")
                print(f"Ignore adding file {intended_filename.name}")
            else:
                sfh.add_remove_platform_item(intended_filename, sgh.instance_list_path)
                feature_data_csv.add_row(intended_filename)
                performance_data_csv.add_instance(intended_filename)
                shutil.copy(intended_filename, instances_directory)
                print(f"Instance {intended_filename.name} has been added!")

        feature_data_csv.save_csv()
        performance_data_csv.save_csv()

    print("\nAdding instance set "
          f"{instances_directory.name} done!")

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        sfh.rmfiles(sgh.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        sfh.rmfiles(sgh.sparkle_report_path)
        print("Removing Sparkle report " + sgh.sparkle_report_path + " done!")

    if args.run_extractor_now:
        if not args.parallel:
            print("Start computing features ...")
            scf.computing_features(Path(sgh.feature_data_csv_path), False)
            print(f"Feature data file {sgh.feature_data_csv_path} has been updated!")
            print("Computing features done!")
        else:
            scf.computing_features_parallel(
                Path(sgh.feature_data_csv_path), False)
            print("Computing features in parallel ...")

    if args.run_solver_now:
        if not args.parallel:
            print("Start running solvers ...")
            srs.running_solvers(sgh.performance_data_csv_path, rerun=False)
            print(f"Performance data file {sgh.performance_data_csv_path} has been "
                  "updated!")
            print("Running solvers done!")
        else:
            num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
            srsp.running_solvers_parallel(
                sgh.performance_data_csv_path, num_job_in_parallel, rerun=False)
            print("Running solvers in parallel ...")

    # Write used settings to file
    sgh.settings.write_used_settings()
