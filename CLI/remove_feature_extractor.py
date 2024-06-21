#!/usr/bin/env python3
"""Sparkle command to remove a feature extractor from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

from sparkle.platform import file_help as sfh
import global_variables as gv
from sparkle.structures import feature_data_csv_help as sfdcsv
import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.ExtractorPathArgument.names,
                        **ac.ExtractorPathArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    extractor_path = resolve_object_name(args.extractor_path,
                                         gv.extractor_nickname_mapping,
                                         gv.extractor_dir)

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_FEATURE_EXTRACTOR]
    )

    if not Path(extractor_path).exists():
        print(f'Feature extractor path "{extractor_path}" does not exist!')
        sys.exit(-1)

    print("Starting removing feature extractor "
          f"{Path(extractor_path).name} ...")

    if len(gv.extractor_list) > 0:
        sfh.add_remove_platform_item(str(extractor_path),
                                     gv.extractor_list_path, remove=True)

    if len(gv.extractor_feature_vector_size_mapping) > 0:
        sfh.add_remove_platform_item(None,
                                     gv.extractor_feature_vector_size_list_path,
                                     key=str(extractor_path),
                                     remove=True)

    if len(gv.extractor_nickname_mapping) > 0:
        for key in gv.extractor_nickname_mapping:
            if gv.extractor_nickname_mapping[key] == extractor_path:
                sfh.add_remove_platform_item(None,
                                             gv.extractor_nickname_list_path,
                                             key=key,
                                             remove=True)
                break

    if Path(gv.feature_data_csv_path).exists():
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(gv.feature_data_csv_path,
                                                        gv.extractor_list)
        for column_name in feature_data_csv.list_columns():
            tmp_extractor_path = feature_data_csv.get_extractor_path_from_feature(
                column_name
            )
            if extractor_path == tmp_extractor_path:
                feature_data_csv.delete_column(column_name)
        feature_data_csv.save_csv()
        shutil.rmtree(extractor_path)

    if Path(gv.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(gv.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    if Path(gv.sparkle_report_path).exists():
        shutil.rmtree(gv.sparkle_report_path)
        print(f"Removing Sparkle report {gv.sparkle_report_path} done!")

    print("Removing feature extractor "
          f"{Path(extractor_path).name} done!")
