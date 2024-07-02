#!/usr/bin/env python3
"""Sparkle command to add an instance set to the Sparkle platform."""

import sys
import argparse
from pathlib import Path
import shutil

import global_variables as gv
from sparkle.platform import file_help as sfh, settings_help
from sparkle.instance import InstanceSet
from sparkle.structures.feature_data_csv_help import SparkleFeatureDataCSV
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.help import compute_features_help as scf
from CLI.run_solvers import running_solvers_performance_data
import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc


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
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instances_source = Path(args.instances_path)
    instances_target = gv.instance_dir / instances_source.name
    run_on = args.run_on

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.ADD_INSTANCES])

    if not instances_source.exists():
        print(f'Instance set path "{instances_source}" does not exist!')
        sys.exit(-1)

    nickname = args.nickname
    if nickname is not None:
        sfh.add_remove_platform_item(instances_target,
                                     gv.instances_nickname_path, key=nickname)

    print(f"Start adding all instances in directory {instances_source} ...")
    instance_set = InstanceSet(instances_source)

    if not instances_target.exists():
        instances_target.mkdir(parents=True, exist_ok=True)
    print("Copying files...")
    for instance_path_source in instance_set.all_paths:
        print(f"Copying {instance_path_source} to {instances_target}...", end="\r")
        shutil.copy(instance_path_source, instances_target)
    print("Copying done!")
    # Refresh the instance set as the target instance set
    instance_set = InstanceSet(instances_target)

    # Add the instances to the Feature Data / Performance Data
    feature_data_csv = SparkleFeatureDataCSV(gv.feature_data_csv_path,
                                             gv.extractor_list)
    # When adding instances, an empty performance DF has no objectives yet
    performance_data = PerformanceDataFrame(
        gv.performance_data_csv_path,
        objectives=gv.settings.get_general_sparkle_objectives())
    for path in instance_set.instance_paths:
        feature_data_csv.add_row(str(path))
        performance_data.add_instance(str(path))

    feature_data_csv.save_csv()
    performance_data.save_csv()

    """if sih._check_existence_of_instance_list_file(instances_source):
        # Copy the reference list to the reference list dir of Sparkle
        instance_list_path = instances_source / Path(sih._instance_list_file)
        target_path = gv.reference_list_dir / (
            instances_source.name + gv.instance_list_postfix)
        shutil.copy(instance_list_path, target_path)
        list_instance = sih._get_list_instance(instances_source)

        feature_data_csv = SparkleFeatureDataCSV(gv.feature_data_csv_path,
                                                 gv.extractor_list)
        # When adding instances, an empty performance DF has no objectives yet
        performance_data = PerformanceDataFrame(
            gv.performance_data_csv_path,
            objectives=gv.settings.get_general_sparkle_objectives())

        print(f"Number of instances to be added: {len(list_instance)}")

        for instance_line in list_instance:
            instance_related_files = instance_line.strip().split()
            intended_instance_line = ""

            for related_file_name in instance_related_files:
                source_file_path = instances_source / related_file_name
                target_file_path = instances_directory / related_file_name
                shutil.copy(source_file_path, target_file_path)
                intended_instance_line += str(target_file_path) + " "

            intended_instance_line = intended_instance_line.strip()
            target_instance = instances_directory / Path(intended_instance_line).name
            feature_data_csv.add_row(target_instance)
            performance_data.add_instance(target_instance)

            print(f"Instance {instance_line} has been added!\n")

        feature_data_csv.save_csv()
        performance_data.save_csv()
    else:
        list_source_all_filename = sfh.get_file_paths_recursive(instances_source)
        target_all_filename = sfh.get_file_paths_recursive(instances_directory)

        feature_data_csv = SparkleFeatureDataCSV(gv.feature_data_csv_path,
                                                 gv.extractor_list)
        # When adding instances, an empty performance DF has no objectives yet
        performance_data = PerformanceDataFrame(
            gv.performance_data_csv_path,
            objectives=gv.settings.get_general_sparkle_objectives())

        num_inst = len(list_source_all_filename)
        added = 0
        print(f"Number of instances to be added: {num_inst}")
        for i, intended_filepath in enumerate(list_source_all_filename):
            intended_filename = intended_filepath.name
            print(f"Adding {intended_filename} ... "
                  f"({i + 1} out of {num_inst})", end="\r")
            if intended_filename in target_all_filename:
                print(f"Instance {intended_filename} already exists in Directory "
                      f"{instances_directory}")
                print(f"Ignore adding file {intended_filename}")
            else:
                shutil.copy(intended_filepath, instances_directory)
                feature_data_csv.add_row(instances_directory / intended_filename)
                performance_data.add_instance(
                    str(instances_directory / intended_filename))
                added += 1
        if added == num_inst:
            print(f"All instances of {instances_source} have been added!")
        else:
            print(f"{added}/{num_inst} instances of {instances_source} have been added!")

        feature_data_csv.save_csv()
        performance_data.save_csv()"""

    print(f"\nAdding instance set {instance_set.name} done!")

    if Path(gv.sparkle_algorithm_selector_path).exists():
        sfh.rmfiles(gv.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    if args.run_extractor_now:
        print("Start computing features ...")
        scf.compute_features(Path(gv.feature_data_csv_path), False)

    if args.run_solver_now:
        num_job_in_parallel = gv.settings.get_number_of_jobs_in_parallel()
        running_solvers_performance_data(gv.performance_data_csv_path,
                                         num_job_in_parallel,
                                         rerun=False, run_on=run_on)
        print("Running solvers...")

    # Write used settings to file
    gv.settings.write_used_settings()
