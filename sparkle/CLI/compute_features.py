#!/usr/bin/env python3
"""Sparkle command to compute features for instances."""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

from runrunner.base import Run, Runner

from sparkle.selector import Extractor
from sparkle.platform.settings_objects import Settings
from sparkle.structures import FeatureDataFrame
from sparkle.instance import Instance_Set, InstanceSet


from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_instance_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sparkle command to Compute features "
        "for instances using added extractors "
        "and instances."
    )
    parser.add_argument(
        *ac.RecomputeFeaturesArgument.names, **ac.RecomputeFeaturesArgument.kwargs
    )
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    return parser


def compute_features(
    feature_data: Path | FeatureDataFrame,
    recompute: bool,
    run_on: Runner = Runner.SLURM,
) -> list[Run]:
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

    # Lookup all instances to resolve the instance paths later
    instances: list[InstanceSet] = []
    for instance_dir in gv.settings().DEFAULT_instance_dir.iterdir():
        if instance_dir.is_dir():
            instances.append(Instance_Set(instance_dir))

    # If there are no jobs, stop
    if not jobs:
        print(
            "No feature computation jobs to run; stopping execution! To recompute "
            "feature values use the --recompute flag."
        )
        return None
    cutoff = gv.settings().extractor_cutoff_time
    cmd_list = []
    instance_paths = set()
    grouped_job_list: dict[str, dict[str, list[str]]] = {}

    # Group the jobs by extractor/feature group
    for instance_name, extractor_name, feature_group in jobs:
        if extractor_name not in grouped_job_list:
            grouped_job_list[extractor_name] = {}
        if feature_group not in grouped_job_list[extractor_name]:
            grouped_job_list[extractor_name][feature_group] = []
        instance_path = resolve_instance_name(str(instance_name), instances)
        grouped_job_list[extractor_name][feature_group].append(instance_path)

    parallel_jobs = min(len(cmd_list), gv.settings().slurm_jobs_in_parallel)
    sbatch_options = gv.settings().sbatch_settings
    slurm_prepend = gv.settings().slurm_job_prepend
    srun_options = ["-N1", "-n1"] + sbatch_options
    runs = []
    for extractor_name, feature_groups in grouped_job_list.items():
        extractor_path = gv.settings().DEFAULT_extractor_dir / extractor_name
        extractor = Extractor(extractor_path)
        for feature_group, instance_paths in feature_groups.items():
            run = extractor.run_cli(
                instance_paths,
                feature_data,
                cutoff,
                feature_group if extractor.groupwise_computation else None,
                run_on,
                sbatch_options,
                srun_options,
                parallel_jobs,
                slurm_prepend,
                log_dir=sl.caller_log_dir,
            )
            runs.append(run)
    return runs


def main(argv: list[str]) -> None:
    """Main function of the compute features command."""
    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    settings = gv.settings(args)
    run_on = settings.run_on

    # Log command call
    sl.log_command(sys.argv, settings.random_state)
    check_for_initialise()

    # Check if there are any feature extractors registered
    if not any([p.is_dir() for p in gv.settings().DEFAULT_extractor_dir.iterdir()]):
        print(
            "No feature extractors present! Add feature extractors to Sparkle "
            "by using the add_feature_extractor command."
        )
        sys.exit()

    # Start compute features
    print("Start computing features ...")
    compute_features(settings.DEFAULT_feature_data_path, args.recompute, run_on)

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
