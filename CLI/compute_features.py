#!/usr/bin/env python3
"""Sparkle command to compute features for instances."""
from __future__ import annotations
import sys
import argparse
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Status, Run

from sparkle.solver import Extractor
from CLI.help import global_variables as gv
from CLI.help import sparkle_logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from CLI.help import argparse_custom as ac
from CLI.help.command_help import COMMAND_DEPENDENCIES, CommandName
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc
from sparkle.structures import FeatureDataFrame


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*apc.RecomputeFeaturesArgument.names,
                        **apc.RecomputeFeaturesArgument.kwargs)
    parser.add_argument(*apc.SettingsFileArgument.names,
                        **apc.SettingsFileArgument.kwargs)
    parser.add_argument(*apc.RunOnArgument.names,
                        **apc.RunOnArgument.kwargs)

    return parser


def compute_features(
        feature_data_csv_path: Path,
        recompute: bool,
        run_on: Runner = Runner.SLURM) -> Run:
    """Compute features for all instance and feature extractor combinations.

    A RunRunner run is submitted for the computation of the features.
    The results are then stored in the csv file specified by feature_data_csv_path.

    Args:
        feature_data_csv_path: Create or load feature data CSV file in the path
            specified by this parameter.
        recompute: Specifies if features should be recomputed.
        run_on: Runner
            On which computer or cluster environment to run the solvers.
            Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM

    Returns:
        The Slurm job or Local job
    """
    feature_dataframe = FeatureDataFrame(feature_data_csv_path)
    if recompute:
        feature_dataframe.reset_dataframe()
    jobs = feature_dataframe.remaining_jobs()

    # If there are no jobs, stop
    if not jobs:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()
    cutoff = gv.settings.get_general_extractor_cutoff_time()
    cmd_list = []
    extractors = {}
    # We create a job for each instance/extractor combination
    for instance_path, extractor_path, feature_group in jobs:
        cmd = ("CLI/core/compute_features.py "
               f"--instance {instance_path} "
               f"--extractor {extractor_path} "
               f"--feature-csv {feature_data_csv_path} "
               f"--cutoff {cutoff}")
        if extractor_path in extractors:
            extractor = extractors[extractor_path]
        else:
            extractor = Extractor(Path(extractor_path))
            extractors[extractor_path] = extractor
        if extractor.groupwise_computation:
            # Extractor job can be parallelised, thus creating i * e * g jobs
            cmd_list.append(cmd + f" --feature-group {feature_group}")
        else:
            cmd_list.append(cmd)

    print(f"The number of compute jobs: {len(cmd_list)}")
    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # Generate the sbatch script
    parallel_jobs = min(len(cmd_list), gv.settings.get_number_of_jobs_in_parallel())
    sbatch_options = gv.settings.get_slurm_extra_options(as_args=True)
    srun_options = ["-N1", "-n1"] + sbatch_options
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.COMPUTE_FEATURES,
        parallel_jobs=parallel_jobs,
        base_dir=gv.sparkle_tmp_path,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        run.wait()
        for job in run.jobs:
            jobs_done = sum(j.status == Status.COMPLETED for j in run.jobs)
            print(f"Executing Progress: {jobs_done} out of {len(run.jobs)}")
            if jobs_done == len(run.jobs):
                break
            job.wait()
        print("Computing features done!")

    return run


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.run_on is not None:
        gv.settings.set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings.get_run_on()

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.COMPUTE_FEATURES])

    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file

    # Check if there are any feature extractors registered
    if not any([p.is_dir() for p in gv.extractor_dir.iterdir()]):
        print("No feature extractors present! Add feature extractors to Sparkle "
              "by using the add_feature_extractor command.")
        sys.exit()

    # Start compute features
    print("Start computing features ...")
    compute_features(gv.feature_data_csv_path, args.recompute, run_on=run_on)

    # Write used settings to file
    gv.settings.write_used_settings()
