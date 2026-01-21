#!/usr/bin/env python3
"""Sparkle command to compute features for instances."""

from __future__ import annotations
import sys
import argparse

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
        *Settings.OPTION_no_groupwise_computation.args,
        **Settings.OPTION_no_groupwise_computation.kwargs,
    )
    return parser


def compute_features(
    feature_data: FeatureDataFrame,
    recompute: bool,
    run_on: Runner = Runner.SLURM,
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

    Returns:
        The Slurm job or Local job
    """

    def group_jobs(
        jobs: list[tuple[str, str, str]],
        instances: list[InstanceSet],
        no_groupwise_computation: bool,
    ) -> dict[str, dict[str | None, list[str]]]:
        """Group jobs per extractor and feature group, with optional groupwise override."""
        grouped_job_list: dict[str, dict[str | None, set[str]]] = {}

        for instance_name, extractor_name, feature_group in jobs:
            if extractor_name not in grouped_job_list:
                grouped_job_list[extractor_name] = {}
            effective_group = None if no_groupwise_computation else feature_group
            if effective_group not in grouped_job_list[extractor_name]:
                grouped_job_list[extractor_name][effective_group] = set()
            instance_path = resolve_instance_name(str(instance_name), instances)
            grouped_job_list[extractor_name][effective_group].add(instance_path)

        return {
            extractor: {group: list(paths) for group, paths in feature_groups.items()}
            for extractor, feature_groups in grouped_job_list.items()
        }

    settings = gv.settings()
    if recompute:
        feature_data.reset_dataframe()
    jobs = feature_data.remaining_jobs()

    # Lookup all instances to resolve the instance paths later
    instances: list[InstanceSet] = []
    for instance_dir in settings.DEFAULT_instance_dir.iterdir():
        if instance_dir.is_dir():
            instances.append(Instance_Set(instance_dir))

    # If there are no jobs, stop
    if not jobs:
        print(
            "No feature computation jobs to run; stopping execution! To recompute "
            "feature values use the --recompute flag."
        )
        return
    cutoff = settings.extractor_cutoff_time
    grouped_job_list = group_jobs(jobs, instances, settings.no_groupwise_computation)

    sbatch_options = settings.sbatch_settings
    slurm_prepend = settings.slurm_job_prepend
    srun_options = ["-N1", "-n1"] + sbatch_options
    runs = []
    for extractor_name, feature_groups in grouped_job_list.items():
        extractor_path = settings.DEFAULT_extractor_dir / extractor_name
        extractor = Extractor(extractor_path)
        for feature_group, instance_paths in feature_groups.items():
            run = extractor.run_cli(
                instance_paths,
                feature_data,
                cutoff,
                (
                    feature_group
                    if extractor.groupwise_computation
                    and not settings.no_groupwise_computation
                    else None
                ),
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

    # Filter instances or extractors
    if args.instance_path:
        instances = []
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
            for i in instance.instance_names:
                instances.append(i)

        for instance in feature_data.instances:
            if instance not in instances:
                feature_data.remove_instances(instance)
        if feature_data.num_instances == 0:
            raise ValueError("Argument Error! No instances left after filtering.")
    if args.extractors:
        extractors = []
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
            extractors.append(extractor.name)
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
