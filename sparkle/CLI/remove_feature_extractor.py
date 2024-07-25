#!/usr/bin/env python3
"""Sparkle command to remove a feature extractor from the Sparkle platform."""

import sys
import argparse
import shutil
from pathlib import Path

from sparkle.platform import file_help as sfh
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import FeatureDataFrame
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.CLI.help import command_help as ch
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name


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
    extractor_nicknames = gv.file_storage_data_mapping[gv.extractor_nickname_list_path]
    extractor_path = resolve_object_name(
        args.extractor_path,
        extractor_nicknames,
        gv.extractor_dir)

    check_for_initialise(
        ch.COMMAND_DEPENDENCIES[ch.CommandName.REMOVE_FEATURE_EXTRACTOR]
    )

    if not Path(extractor_path).exists():
        print(f'Feature extractor path "{extractor_path}" does not exist!')
        sys.exit(-1)

    print(f"Starting removing feature extractor {Path(extractor_path).name} ...")

    for key in extractor_nicknames:
        if extractor_nicknames == extractor_path:
            sfh.add_remove_platform_item(
                None,
                gv.extractor_nickname_list_path,
                extractor_nicknames,
                key=key,
                remove=True)
            break

    if gv.feature_data_csv_path.exists():
        feature_data = FeatureDataFrame(gv.feature_data_csv_path)
        feature_data.remove_extractor(str(extractor_path))
        feature_data.save_csv()
    shutil.rmtree(extractor_path)

    if Path(gv.sparkle_algorithm_selector_path).exists():
        shutil.rmtree(gv.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    print(f"Removing feature extractor {Path(extractor_path).name} done!")
