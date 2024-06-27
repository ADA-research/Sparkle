#!/usr/bin/env python3
"""Sparkle command to compute features for instances."""

import sys
import argparse
from pathlib import Path

import global_variables as gv
from CLI.help import compute_features_help as scf
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    gv.settings = settings_help.Settings()

    parser = argparse.ArgumentParser()
    parser.add_argument(*apc.RecomputeFeaturesArgument.names,
                        **apc.RecomputeFeaturesArgument.kwargs)
    parser.add_argument(*apc.SettingsFileArgument.names,
                        **apc.SettingsFileArgument.kwargs)
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

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.COMPUTE_FEATURES])

    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file

    # Check if there are any feature extractors registered
    if not gv.extractor_list:
        print("No feature extractors present! Add feature extractors to Sparkle "
              "by using the add_feature_extractor command.")
        sys.exit()

    # Start compute features
    print("Start computing features ...")
    scf.compute_features(Path(gv.feature_data_csv_path),
                         args.recompute, run_on=args.run_on)

    # Write used settings to file
    gv.settings.write_used_settings()
