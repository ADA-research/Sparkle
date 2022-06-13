#!/usr/bin/env python3

import os
import sys
import argparse
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_logging as sl

def parser_function():
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


if __name__ == r"__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    extractor_path = args.extractor_path

    if args.nickname:
        extractor_path = sparkle_global_help.extractor_nickname_mapping[extractor_path]
    if not os.path.exists(extractor_path):
        print(
            r"c Feature extractor path "
            + "'"
            + extractor_path
            + "'"
            + r" does not exist!"
        )
        sys.exit()

    if extractor_path[-1] == r"/":
        extractor_path = extractor_path[:-1]

    print(
        "c Starting removing feature extractor "
        + sfh.get_last_level_directory_name(extractor_path)
        + " ..."
    )

    extractor_list = sparkle_global_help.extractor_list
    if bool(extractor_list):
        extractor_list.remove(extractor_path)
        sfh.write_extractor_list()

    extractor_feature_vector_size_mapping = (
        sparkle_global_help.extractor_feature_vector_size_mapping
    )
    if bool(extractor_feature_vector_size_mapping):
        output = extractor_feature_vector_size_mapping.pop(extractor_path)
        sfh.write_extractor_feature_vector_size_mapping()

    extractor_nickname_mapping = sparkle_global_help.extractor_nickname_mapping
    if bool(extractor_nickname_mapping):
        for key in extractor_nickname_mapping:
            if extractor_nickname_mapping[key] == extractor_path:
                output = extractor_nickname_mapping.pop(key)
                break
        sfh.write_extractor_nickname_mapping()

    if os.path.exists(sparkle_global_help.feature_data_csv_path):
        feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(
            sparkle_global_help.feature_data_csv_path
        )
        for column_name in feature_data_csv.list_columns():
            tmp_extractor_path = feature_data_csv.get_extractor_path_from_feature(
                column_name
            )
            if extractor_path == tmp_extractor_path:
                feature_data_csv.delete_column(column_name)
        feature_data_csv.update_csv()

        command_line = r"rm -rf " + extractor_path
        os.system(command_line)

    if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
        command_line = r"rm -f " + sparkle_global_help.sparkle_portfolio_selector_path
        os.system(command_line)
        print(
            "c Removing Sparkle portfolio selector "
            + sparkle_global_help.sparkle_portfolio_selector_path
            + " done!"
        )

    if os.path.exists(sparkle_global_help.sparkle_report_path):
        command_line = r"rm -f " + sparkle_global_help.sparkle_report_path
        os.system(command_line)
        print(
            "c Removing Sparkle report "
            + sparkle_global_help.sparkle_report_path
            + " done!"
        )

    print(
        "c Removing feature extractor "
        + sfh.get_last_level_directory_name(extractor_path)
        + " done!"
    )
