#!/usr/bin/env python3
"""Sparkle command to remove a feature extractor from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

from sparkle.platform import file_help as sfh
import global_variables as sgh
from sparkle.structures import feature_data_csv_help as sfdcsv
import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "extractor_path",
        metavar="extractor-path",
        type=str,
        help="path to or nickname of the feature extractor",
    )
    parser.add_argument(
        "--nickname",
        action="store_true",
        help=("if set to True extractor_path is used as a nickname for the feature "
              "extractor"),
    )

    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    extractor_path = args.extractor_path

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_FEATURE_EXTRACTOR]
    )

    if args.nickname:
        extractor_path = sgh.extractor_nickname_mapping[extractor_path]
    if not Path(extractor_path).exists():
        print(f'Feature extractor path "{extractor_path}" does not exist!')
        sys.exit(-1)

    if extractor_path[-1] == "/":
        extractor_path = extractor_path[:-1]

    print("Starting removing feature extractor "
          f"{Path(extractor_path).name} ...")

    if len(sgh.extractor_list) > 0:
        sfh.add_remove_platform_item(extractor_path,
                                     sgh.extractor_list_path, remove=True)

    if len(sgh.extractor_feature_vector_size_mapping) > 0:
        sfh.add_remove_platform_item(None,
                                     sgh.extractor_feature_vector_size_list_path,
                                     key=extractor_path,
                                     remove=False)

    if len(sgh.extractor_nickname_mapping) > 0:
        for key in sgh.extractor_nickname_mapping:
            if sgh.extractor_nickname_mapping[key] == extractor_path:
                sfh.add_remove_platform_item(None,
                                             sgh.extractor_nickname_list_path,
                                             key=key,
                                             remove=False)
                break

    if Path(sgh.feature_data_csv_path).exists():
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(
            sgh.feature_data_csv_path
        )
        for column_name in feature_data_csv.list_columns():
            tmp_extractor_path = feature_data_csv.get_extractor_path_from_feature(
                column_name
            )
            if extractor_path == tmp_extractor_path:
                feature_data_csv.delete_column(column_name)
        feature_data_csv.save_csv()
        shutil.rmtree(extractor_path)

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(sgh.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        shutil.rmtree(sgh.sparkle_report_path)
        print(f"Removing Sparkle report {sgh.sparkle_report_path} done!")

    print("Removing feature extractor "
          f"{Path(extractor_path).name} done!")
