#!/usr/bin/env python3
"""Sparkle command to add a feature extractor to the Sparkle platform."""
import os
import sys
import shutil
import argparse
from pathlib import Path

from sparkle.platform import file_help as sfh, settings_objects
from CLI.help import global_variables as gv
from sparkle.structures import FeatureDataFrame
from CLI.compute_features import compute_features
from CLI.help import sparkle_logging as sl
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc
from sparkle.solver import Extractor


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(*apc.ExtractorPathArgument.names,
                        **apc.ExtractorPathArgument.kwargs)
    group_extractor_run = parser.add_mutually_exclusive_group()
    group_extractor_run.add_argument(*apc.RunExtractorNowArgument.names,
                                     **apc.RunExtractorNowArgument.kwargs)
    group_extractor_run.add_argument(*apc.RunExtractorLaterArgument.names,
                                     **apc.RunExtractorLaterArgument.kwargs)
    parser.add_argument(*apc.NicknameFeatureExtractorArgument.names,
                        **apc.NicknameFeatureExtractorArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_objects.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    check_for_initialise(ch.COMMAND_DEPENDENCIES[ch.CommandName.ADD_FEATURE_EXTRACTOR])

    extractor_source = Path(args.extractor_path)
    if not extractor_source.exists():
        print(f'Feature extractor path "{extractor_source}" does not exist!')
        sys.exit(-1)

    nickname_str = args.nickname

    # Start add feature extractor
    extractor_target_path = gv.extractor_dir / extractor_source.name

    if extractor_target_path.exists():
        print(f"Feature extractor {extractor_source.name} already exists! "
              "Can not add feature extractor.")
        sys.exit(-1)
    extractor_target_path.mkdir()
    shutil.copytree(extractor_source, extractor_target_path, dirs_exist_ok=True)

    # Check execution permissions for wrapper
    extractor_wrapper = extractor_target_path / Extractor.wrapper
    if not extractor_wrapper.is_file() or not os.access(extractor_wrapper, os.X_OK):
        print(f"The file {extractor_wrapper} does not exist or is \
              not executable.")
        sys.exit(-1)

    # Get the extractor features groups and names from the wrapper
    extractor = Extractor(extractor_target_path)
    feature_dataframe = FeatureDataFrame(gv.feature_data_csv_path)
    feature_dataframe.add_extractor(str(extractor_target_path), extractor.features)
    feature_dataframe.save_csv()

    print(f"Adding feature extractor {extractor_target_path.name} done!")

    if Path(gv.sparkle_algorithm_selector_path).exists():
        sfh.rmfiles(Path(gv.sparkle_algorithm_selector_path))
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    if nickname_str is not None:
        sfh.add_remove_platform_item(
            extractor_target_path,
            gv.extractor_nickname_list_path,
            gv.file_storage_data_mapping[gv.extractor_nickname_list_path],
            key=nickname_str)

    if args.run_extractor_now:
        print("Start computing features ...")
        compute_features(gv.feature_data_csv_path, False)

    # Write used settings to file
    gv.settings.write_used_settings()
