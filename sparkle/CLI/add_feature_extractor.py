#!/usr/bin/env python3
"""Sparkle command to add a feature extractor to the Sparkle platform."""
import os
import sys
import shutil
import argparse
from pathlib import Path

from sparkle.platform import file_help as sfh
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import FeatureDataFrame
from sparkle.CLI.help import logging as sl
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.solver import Extractor


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    # Define command line arguments
    parser = argparse.ArgumentParser(
        description="Add a feature extractor to the platform.")
    parser.add_argument(*ac.ExtractorPathArgument.names,
                        **ac.ExtractorPathArgument.kwargs)
    parser.add_argument(*ac.NicknameFeatureExtractorArgument.names,
                        **ac.NicknameFeatureExtractorArgument.kwargs)
    parser.add_argument(*ac.NoCopyArgument.names, **ac.NoCopyArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the add feature extractor command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    extractor_source = Path(args.extractor_path)
    if not extractor_source.exists():
        print(f'Feature extractor path "{extractor_source}" does not exist!')
        sys.exit(-1)

    nickname_str = args.nickname

    # Start add feature extractor
    extractor_target_path = gv.settings().DEFAULT_extractor_dir / extractor_source.name

    if extractor_target_path.exists():
        print(f"Feature extractor {extractor_source.name} already exists! "
              "Can not add feature extractor.")
        sys.exit(-1)

    if args.no_copy:
        print(f"Creating symbolic link from {extractor_source} "
              f"to {extractor_target_path}...")
        extractor_target_path.symlink_to(extractor_source.absolute())
    else:
        print(f"Copying feature extractor {extractor_source.name} ...")
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
    feature_dataframe = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
    feature_dataframe.add_extractor(extractor.name, extractor.features)
    feature_dataframe.save_csv()

    print(f"Adding feature extractor {extractor_target_path.name} done!")

    if nickname_str is not None:
        sfh.add_remove_platform_item(
            extractor_target_path,
            gv.extractor_nickname_list_path,
            gv.file_storage_data_mapping[gv.extractor_nickname_list_path],
            key=nickname_str)

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
