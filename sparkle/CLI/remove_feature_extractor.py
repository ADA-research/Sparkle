#!/usr/bin/env python3
"""Sparkle command to remove a feature extractor from the Sparkle platform."""

import sys
import argparse
import shutil

from sparkle.platform import file_help as sfh
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import FeatureDataFrame
from sparkle.CLI.help import logging as sl
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.solver import Extractor


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
    extractor = resolve_object_name(
        args.extractor_path,
        extractor_nicknames,
        gv.settings().DEFAULT_extractor_dir,
        class_name=Extractor)

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.REMOVE_FEATURE_EXTRACTOR])

    if extractor is None:
        print(f'Feature extractor path "{args.extractor_path}" does not exist!')
        sys.exit(-1)

    print(f"Starting removing feature extractor {extractor.name} ...")

    for key in extractor_nicknames:
        if extractor_nicknames == extractor.directory:
            sfh.add_remove_platform_item(
                None,
                gv.extractor_nickname_list_path,
                extractor_nicknames,
                key=key,
                remove=True)
            break

    if gv.settings().DEFAULT_feature_data_path.exists():
        feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
        feature_data.remove_extractor(extractor.name)
        feature_data.save_csv()
    shutil.rmtree(extractor.directory)

    print(f"Removing feature extractor {extractor.name} done!")
