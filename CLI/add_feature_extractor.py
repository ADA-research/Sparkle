#!/usr/bin/env python3
"""Sparkle command to add a feature extractor to the Sparkle platform."""

import sys
import shutil
import subprocess
import argparse
from pathlib import Path

from sparkle.platform import file_help as sfh, settings_help
import global_variables as sgh
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.instance import compute_features_help as scf
import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def _check_existence_of_test_instance_list_file(extractor_directory: str) -> bool:
    """Check whether a file exists with the list of test instances."""
    if not Path(extractor_directory).is_dir():
        return False

    test_instance_list_file_name = "sparkle_test_instance_list.txt"
    test_instance_list_file_path = (Path(extractor_directory)
                                    / test_instance_list_file_name)

    return Path(test_instance_list_file_path).is_file()


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "extractor_path",
        metavar="extractor-path",
        type=str,
        help="path to the feature extractor",
    )
    group_extractor_run = parser.add_mutually_exclusive_group()
    group_extractor_run.add_argument(
        "--run-extractor-now",
        default=False,
        action="store_true",
        help=("immediately run the newly added feature extractor "
              + "on the existing instances")
    )
    group_extractor_run.add_argument(
        "--run-extractor-later",
        dest="run_extractor_now",
        action="store_false",
        help=("do not immediately run the newly added feature extractor "
              + "on the existing instances (default)")
    )
    parser.add_argument(
        "--nickname",
        type=str,
        help="set a nickname for the feature extractor"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the feature extractor on multiple instances in parallel",
    )
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.ADD_FEATURE_EXTRACTOR])

    extractor_source = Path(args.extractor_path)
    if not extractor_source.exists():
        print(f'Feature extractor path "{extractor_source}" does not exist!')
        sys.exit(-1)

    nickname_str = args.nickname

    # Start add feature extractor
    last_level_directory = ""
    extractor_name = Path(extractor_source)

    extractor_target_path = sgh.extractor_dir / extractor_source.name

    if extractor_target_path.exists():
        print(f"Feature extractor {extractor_source.name} already exists! "
              "Can not add feature extractor.")
        sys.exit(-1)
    extractor_target_path.mkdir()
    shutil.copytree(extractor_source, extractor_target_path, dirs_exist_ok=True)
    sfh.add_remove_platform_item(str(extractor_target_path), sgh.extractor_list_path)

    # pre-run the feature extractor on a testing instance, to obtain the feature names
    if _check_existence_of_test_instance_list_file(extractor_target_path):
        test_instance_list_file_name = "sparkle_test_instance_list.txt"
        test_instance_list_file_path = (extractor_target_path
                                        / test_instance_list_file_name)
        with test_instance_list_file_path.open("r") as infile:
            model_file, constraint_file = infile.readline().strip().split()

        result_path = (
            "Tmp/"
            + test_instance_list_file_path.name
            + "_"
            + Path(model_file).name
            + "_"
            + sgh.get_time_pid_random_string()
            + ".rawres"
        )
        command_line = [extractor_target_path / sgh.sparkle_run_default_wrapper,
                        f"{extractor_target_path}/",
                        extractor_target_path / model_file,
                        extractor_target_path / constraint_file,
                        result_path]
        subprocess.run(command_line)
    else:
        instance_path = extractor_target_path / "sparkle_test_instance.cnf"
        if not instance_path.is_file():
            instance_path = extractor_target_path / "sparkle_test_instance.txt"
        result_path = (
            "Tmp/"
            + extractor_target_path.name
            + "_"
            + instance_path.name
            + "_"
            + sgh.get_time_pid_random_string()
            + ".rawres"
        )
        command_line = [extractor_target_path / sgh.sparkle_run_default_wrapper,
                        f"{extractor_target_path}/",
                        str(instance_path),
                        result_path]
        subprocess.run(command_line)

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)

    tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
    list_columns = tmp_fdcsv.list_columns()
    for column_name in list_columns:
        feature_data_csv.add_column(column_name)

    feature_data_csv.save_csv()
    sfh.add_remove_platform_item(len(list_columns),
                                 sgh.extractor_feature_vector_size_list_path,
                                 key=str(extractor_target_path))

    sfh.rmfiles(Path(result_path))

    print("Adding feature extractor "
          f"{extractor_target_path.name} done!")

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        sfh.rmfiles(Path(sgh.sparkle_algorithm_selector_path))
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        sfh.rmfiles(Path(sgh.sparkle_report_path))
        print(f"Removing Sparkle report {sgh.sparkle_report_path} done!")

    if nickname_str is not None:
        sfh.add_remove_platform_item(str(extractor_target_path),
                                     sgh.extractor_nickname_list_path, key=nickname_str)

    if args.run_extractor_now:
        if not args.parallel:
            print("Start computing features ...")
            scf.computing_features(Path(sgh.feature_data_csv_path), False)
            print(f"Feature data file {sgh.feature_data_csv_path} has been updated!")
            print("Computing features done!")
        else:
            scf.computing_features_parallel(Path(sgh.feature_data_csv_path), False)
            print("Computing features in parallel ...")

    # Write used settings to file
    sgh.settings.write_used_settings()
