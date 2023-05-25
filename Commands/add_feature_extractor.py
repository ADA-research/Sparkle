#!/usr/bin/env python3
"""Sparkle command to add a feature extractor to the Sparkle platform."""

import os
import sys
import argparse
from pathlib import Path
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


def _check_existence_of_test_instance_list_file(extractor_directory: str):
    """Check whether a file exists with the list of test instances."""
    if not Path(extractor_directory).is_dir():
        return False

    test_instance_list_file_name = "sparkle_test_instance_list.txt"
    test_instance_list_file_path = (Path(extractor_directory)
                                    / test_instance_list_file_name)

    if Path(test_instance_list_file_path).is_file():
        return True
    else:
        return False


def parser_function():
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
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    extractor_source = args.extractor_path
    if not Path(extractor_source).exists():
        print(f'Feature extractor path "{extractor_source}" does not exist!')
        sys.exit()

    nickname_str = args.nickname
    my_flag_parallel = args.parallel

    # Start add feature extractor
    last_level_directory = ""
    last_level_directory = sfh.get_last_level_directory_name(extractor_source)

    extractor_directory = "Extractors/" + last_level_directory

    if not Path(extractor_directory).exists():
        Path(extractor_directory).mkdir()
    else:
        print(
            "Feature extractor "
            + sfh.get_last_level_directory_name(extractor_directory)
            + " already exists!"
        )
        print(
            "Do not add feature extractor "
            + sfh.get_last_level_directory_name(extractor_directory)
        )
        sys.exit()

    os.system("cp -r " + extractor_source + "/* " + extractor_directory)

    sgh.extractor_list.append(extractor_directory)
    sfh.add_new_extractor_into_file(extractor_directory)

    # pre-run the feature extractor on a testing instance, to obtain the feature names
    if _check_existence_of_test_instance_list_file(extractor_directory):
        test_instance_list_file_name = "sparkle_test_instance_list.txt"
        test_instance_list_file_path = (Path(extractor_directory)
                                        / test_instance_list_file_name)
        infile = Path(test_instance_list_file_path).open("r")
        test_instance_files = infile.readline().strip().split()
        instance_path = ""
        for test_instance_file in test_instance_files:
            instance_path += Path(extractor_directory) / test_instance_file + " "
        instance_path = instance_path.strip()
        infile.close()

        result_path = (
            "Tmp/"
            + sfh.get_last_level_directory_name(extractor_directory)
            + "_"
            + sfh.get_last_level_directory_name(instance_path)
            + "_"
            + sparkle_basic_help.get_time_pid_random_string()
            + ".rawres"
        )

        command_line = (
            f"{Path(extractor_directory) / sgh.sparkle_run_default_wrapper} "
            f"{extractor_directory}/ {instance_path} {result_path}"
        )
        os.system(command_line)
    else:
        instance_path = Path(extractor_directory) / "sparkle_test_instance.cnf"
        if not Path(instance_path).is_file():
            instance_path = Path(extractor_directory) / "sparkle_test_instance.txt"
        result_path = (
            "Tmp/"
            + sfh.get_last_level_directory_name(extractor_directory)
            + "_"
            + sfh.get_last_level_directory_name(str(instance_path))
            + "_"
            + sparkle_basic_help.get_time_pid_random_string()
            + ".rawres"
        )
        command_line = (
            extractor_directory
            + "/"
            + sgh.sparkle_run_default_wrapper
            + " "
            + extractor_directory
            + "/"
            + " "
            + str(instance_path)
            + " "
            + result_path
        )
        os.system(command_line)

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)

    tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
    list_columns = tmp_fdcsv.list_columns()
    for column_name in list_columns:
        feature_data_csv.add_column(column_name)

    feature_data_csv.update_csv()

    sgh.extractor_feature_vector_size_mapping[extractor_directory] = len(list_columns)
    sfh.add_new_extractor_feature_vector_size_into_file(
        extractor_directory, len(list_columns)
    )

    command_line = "rm -f " + result_path
    os.system(command_line)

    print(
        "Adding feature extractor "
        + sfh.get_last_level_directory_name(extractor_directory)
        + " done!"
    )

    if Path(sgh.sparkle_portfolio_selector_path).exists():
        command_line = "rm -f " + sgh.sparkle_portfolio_selector_path
        os.system(command_line)
        print(
            "Removing Sparkle portfolio selector "
            + sgh.sparkle_portfolio_selector_path
            + " done!"
        )

    if Path(sgh.sparkle_report_path).exists():
        command_line = "rm -f " + sgh.sparkle_report_path
        os.system(command_line)
        print("Removing Sparkle report " + sgh.sparkle_report_path + " done!")

    if nickname_str is not None:
        sgh.extractor_nickname_mapping[nickname_str] = extractor_directory
        sfh.add_new_extractor_nickname_into_file(nickname_str, extractor_directory)
        pass

    if args.run_extractor_now:
        if not my_flag_parallel:
            print("Start computing features ...")
            scf.computing_features(Path(sgh.feature_data_csv_path), False)
            print(
                "Feature data file "
                + sgh.feature_data_csv_path
                + " has been updated!"
            )
            print("Computing features done!")
        else:
            scf.computing_features_parallel(
                Path(sgh.feature_data_csv_path), False
            )
            print("Computing features in parallel ...")

    # Write used settings to file
    sgh.settings.write_used_settings()
