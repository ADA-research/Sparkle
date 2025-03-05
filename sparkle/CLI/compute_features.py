#!/usr/bin/env python3
"""Sparkle command to compute features for instances."""
from __future__ import annotations
import sys
import argparse
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Status, Run

from sparkle.solver import Extractor
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.initialise import check_for_initialise
from sparkle.structures import FeatureDataFrame


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Sparkle command to Compute features "
                                                 "for instances using added extractors "
                                                 "and instances.")
    parser.add_argument(*ac.RecomputeFeaturesArgument.names,
                        **ac.RecomputeFeaturesArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)

    return parser


def compute_features(
        feature_data: Path | FeatureDataFrame,
        recompute: bool,
        run_on: Runner = Runner.SLURM) -> Run:
    """Compute features for all instance and feature extractor combinations.

    A RunRunner run is submitted for the computation of the features.
    The results are then stored in the csv file specified by feature_data_csv_path.

    Args:
        feature_data: Feature Data Frame to use, or path to read it from.
        recompute: Specifies if features should be recomputed.
        run_on: Runner
            On which computer or cluster environment to run the solvers.
            Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM

    Returns:
        The Slurm job or Local job
    """
    if isinstance(feature_data, Path):
        feature_data = FeatureDataFrame(feature_data)
    if recompute:
        feature_data.reset_dataframe()
    jobs = feature_data.remaining_jobs()

    # If there are no jobs, stop
    if not jobs:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        return None
    cutoff = gv.settings().get_general_extractor_cutoff_time()
    cmd_list = []
    extractors = {}
    instance_paths = set()
    features_core = Path(__file__).parent.resolve() / "core" / "compute_features.py"
    # We create a job for each instance/extractor combination
    for instance_path, extractor_name, feature_group in jobs:
        extractor_path = gv.settings().DEFAULT_extractor_dir / extractor_name
        instance_paths.add(instance_path)
        cmd = (f"python3 {features_core} "
               f"--instance {instance_path} "
               f"--extractor {extractor_path} "
               f"--feature-csv {feature_data.csv_filepath} "
               f"--cutoff {cutoff} "
               f"--log-dir {sl.caller_log_dir}")
        if extractor_name in extractors:
            extractor = extractors[extractor_name]
        else:
            extractor = Extractor(extractor_path)
            extractors[extractor_name] = extractor
        if extractor.groupwise_computation:
            # Extractor job can be parallelised, thus creating i * e * g jobs
            cmd_list.append(cmd + f" --feature-group {feature_group}")
        else:
            cmd_list.append(cmd)

    print(f"The number of compute jobs: {len(cmd_list)}")

    parallel_jobs = min(len(cmd_list), gv.settings().get_number_of_jobs_in_parallel())
    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    srun_options = ["-N1", "-n1"] + sbatch_options
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=f"Compute Features: {len(extractors)} Extractors on "
             f"{len(instance_paths)} instances",
        parallel_jobs=parallel_jobs,
        base_dir=sl.caller_log_dir,
        sbatch_options=sbatch_options,
        srun_options=srun_options,
        prepend=gv.settings().get_slurm_job_prepend())

    if run_on == Runner.SLURM:
        print(f"Running the extractors through Slurm with Job IDs: {run.run_id}")
    elif run_on == Runner.LOCAL:
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


def main(argv: list[str]) -> None:
    """Main function of the compute features command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    # Check if there are any feature extractors registered
    if not any([p.is_dir() for p in gv.settings().DEFAULT_extractor_dir.iterdir()]):
        print("No feature extractors present! Add feature extractors to Sparkle "
              "by using the add_feature_extractor command.")
        sys.exit()

    # Start compute features
    print("Start computing features ...")
    compute_features(gv.settings().DEFAULT_feature_data_path, args.recompute, run_on)

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
