#!/usr/bin/env python3
"""Sparkle command to compute features for instances."""

import sys
import argparse
from pathlib import Path

from runrunner.base import Runner
import runrunner as rrr

import global_variables as gv
from sparkle.instance import compute_features_help as scf
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help import command_help as ch
from sparkle.platform import slurm_help as ssh
from CLI.help.command_help import CommandName
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    gv.settings = settings_help.Settings()

    parser = argparse.ArgumentParser()
    parser.add_argument(*apc.RecomputeFeaturesArgument.names,
                        **apc.RecomputeFeaturesArgument.kwargs)
    parser.add_argument(*apc.ParallelArgument.names,
                        **apc.ParallelArgument.kwargs)
    parser.add_argument(*apc.SettingsFileArgument.names,
                        **apc.SettingsFileArgument.kwargs)
    parser.add_argument(*apc.RunOnArgument.names,
                        **apc.RunOnArgument.kwargs)

    return parser


def compute_features_parallel(recompute: bool, run_on: Runner = Runner.SLURM) -> None:
    """Compute features in parallel.

    Args:
        recompute: variable indicating if features should be recomputed
        run_on: Runner
            On which computer or cluster environment to run the solvers.
            Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM
    """
    runs = [scf.computing_features_parallel(Path(gv.feature_data_csv_path),
                                            recompute, run_on=run_on)]
    # If there are no jobs return
    if all(run is None for run in runs):
        print("Running solvers done!")
        return

    # Update performance data csv after the last job is done
    runs.append(rrr.add_to_queue(
        runner=run_on,
        cmd="sparkle/structures/csv_merge.py",
        name=CommandName.CSV_MERGE,
        dependencies=runs[-1],
        base_dir=gv.sparkle_tmp_path,
        sbatch_options=ssh.get_slurm_options_list()))

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        for run in runs:
            if run is not None:
                run.wait()
        print("Computing Features in parallel done!")


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

    if not args.parallel:
        scf.computing_features(Path(gv.feature_data_csv_path), args.recompute)

        print("Feature data file " + gv.feature_data_csv_path + " has been updated!")
        print("Computing features done!")
    else:
        compute_features_parallel(args.recompute, run_on=args.run_on)

    # Write used settings to file
    gv.settings.write_used_settings()
