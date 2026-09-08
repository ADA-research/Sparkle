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
from sparkle.CLI.help.nicknames import resolve_object_name, resolve_instance_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sparkle command to Compute features "
        "for instances using added extractors "
        "and instances."
    )
    parser.add_argument(
        *ac.InstanceSetPathsArgument.names, **ac.InstanceSetPathsArgument.kwargs
    )
    parser.add_argument(*ac.ExtractorsArgument.names, **ac.ExtractorsArgument.kwargs)
    parser.add_argument(
        *ac.RecomputeFeaturesArgument.names, **ac.RecomputeFeaturesArgument.kwargs
    )
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    parser.add_argument(
        *Settings.OPTION_groupwise_computation.args,
        **Settings.OPTION_groupwise_computation.kwargs,
    )
    return parser


def compute_features(
    feature_data: FeatureDataFrame,
    recompute: bool,
    run_on: Runner = Runner.SLURM,
    instance_sets: list[InstanceSet] = None,
) -> list[Run]:
    """Compute features for all instance and feature extractor combinations.

    A RunRunner run is submitted for the computation of the features.
    The results are then stored in the csv file specified by feature_data_csv_path.

    Args:
        feature_data: Feature Data Frame to use
        recompute: Specifies if features should be recomputed.
        run_on: Runner
            On which computer or cluster environment to run the solvers.
            Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM
        instance_sets: Optional resolved instance sets to search. By default, instances
            are resolved from the registered platform instance directory.

    Returns:
        Submitted runs. Empty if there are no jobs to execute.
    """
    settings = gv.settings()
    if recompute:
        feature_data.reset_dataframe()

    remaining_jobs = feature_data.remaining_jobs(
        groupwise_computation=settings.groupwise_computation
    )

    # If there are no jobs, stop
    if not remaining_jobs:
        print(
            "No feature computation jobs to run; stopping execution! To recompute "
            "feature values use the --recompute flag."
        )
        return []

    cutoff = settings.extractor_cutoff_time
    sbatch_options = settings.sbatch_settings
    slurm_prepend = settings.slurm_job_prepend
    srun_options = ["-N1", "-n1"] + sbatch_options
    search_location = (
        settings.DEFAULT_instance_dir if instance_sets is None else instance_sets
    )
    runs = []
    for (instance_set, instance_name), extractor_name, feature_group in remaining_jobs:
        extractor_path = settings.DEFAULT_extractor_dir / extractor_name
        extractor = Extractor(extractor_path)

        instance_path = resolve_instance_name(
            instance_set, instance_name, search_location
        )
        if instance_path is None:
            raise ValueError(
                f"ERROR: The instance {instance_name} ({instance_set}) could not be found. "
                f"Please make sure the path is correct."
            )

        instance_paths = []
        if isinstance(instance_path, list):
            instance_paths = [Path(path) for path in instance_path]
        elif isinstance(instance_path, (str, Path)):
            instance_paths = [Path(instance_path)]

        run = extractor.run_cli(
            instance_paths,
            feature_data,
            cutoff,
            feature_group,
            run_on,
            sbatch_options,
            srun_options,
            settings.slurm_jobs_in_parallel,
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

    # Load feature data
    feature_data = FeatureDataFrame(settings.DEFAULT_feature_data_path)

    # Narrow the work down to only the instances and/or extractors the user named on CLI by filtering the full FDF.
    if args.instance_path:
        instances = set()
        for instance_arg in args.instance_path:
            instance: InstanceSet = resolve_object_name(
                instance_arg,
                gv.instance_set_nickname_mapping,
                settings.DEFAULT_instance_dir,
                Instance_Set,
            )
            if instance is None:
                raise ValueError(
                    f"Argument Error! Could not resolve instance: '{instance_arg}'"
                )
            # resolve_object_name may hand back a single-file FileInstanceSet whose .name
            # is the file stem rather than the owning set (e.g. "PTN/bce7824.cnf" -> name
            # "bce7824"). The FeatureDataFrame is keyed by the owning set, so pair each
            # requested instance with its directory name to match how it was stored.
            for instance_name in instance.instance_names:
                instances.add((instance.directory.name, instance_name))

        filtered_instances = [
            (instance_set, instance_name)
            for instance_set, instance_name in feature_data.instance_pairs
            if (instance_set, instance_name) not in instances
        ]
        feature_data.remove_instance(filtered_instances)
        if feature_data.num_instances == 0:
            raise ValueError("Argument Error! No instances left after filtering.")
    if args.extractors:
        extractors = set()
        for extractor in args.extractors:
            extractor: Extractor = resolve_object_name(
                extractor,
                nickname_dict=gv.extractor_nickname_mapping,
                target_dir=settings.DEFAULT_extractor_dir,
                class_name=Extractor,
            )
            if extractor is None:
                raise ValueError(
                    f"Argument Error! Could not resolve extractor: '{extractor}'"
                )
            extractors.add(extractor.name)
        for extractor in feature_data.extractors:
            if extractor not in extractors:
                feature_data.remove_extractor(extractor)
        if feature_data.num_extractors == 0:
            raise ValueError(
                "Argument Error! No feature extractors left after filtering."
            )

    # Start compute features
    print("Start computing features ...")
    compute_features(feature_data, args.recompute, run_on)

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
