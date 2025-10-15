#!/usr/bin/env python3
"""Command to display the status of the platform."""

import sys
import argparse
from pathlib import Path

from sparkle.structures import FeatureDataFrame, PerformanceDataFrame

from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform import Settings


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Display the status of the platform.")
    parser.add_argument(
        *Settings.OPTION_verbosity.args, **Settings.OPTION_verbosity.kwargs
    )
    return parser


def print_objects_list(objects: list[any], type: str, details: bool = False) -> None:
    """Print a list of sparkle objects.

    Args:
        objects: The objects to print
        type: The name of the object type
        details: Indicating if output should be detailed
    """
    print(
        f"Currently Sparkle has {len(objects)} {type}(s)"
        + (":" if details and objects else "")
    )

    if details:
        for i, object in enumerate(objects):
            print(f"\t[{i + 1}] {Path(object).name}")


def print_feature_computation_jobs(
    feature_data_csv: Path, verbose: bool = False
) -> None:
    """Print a list of remaining feature computation jobs.

    Args:
        feature_data_csv: Path to the feature data csv
        verbose: Indicating, if output should be verbose
    """
    if not feature_data_csv.exists():
        print("\nNo feature data found, cannot determine remaining jobs.")

    feature_data = FeatureDataFrame(feature_data_csv)
    jobs = feature_data.remaining_jobs()

    print(
        f"Currently Sparkle has {len(jobs)} remaining feature computation "
        "jobs that need to be performed before creating an algorithm selector"
        + (":" if verbose and jobs else "")
    )

    if verbose:
        for i, job in enumerate(jobs):
            print(
                f"[{i + 1}]: Extractor: {Path(job[1]).name}, Group: {job[2]}, "
                f"Instance: {Path(job[0]).name}"
            )


def print_performance_computation_jobs(
    performance_data: PerformanceDataFrame, verbose: bool = False
) -> None:
    """Print a list of remaining performance computation jobs.

    Args:
        performance_data: The Performance data
        verbose: Indicating, if output should be verbose
    """
    jobs = performance_data.get_job_list()

    print(
        f"Currently Sparkle has {len(jobs)} remaining performance computation"
        " jobs that need to be performed before creating an algorithm selector"
        + (":" if verbose else "")
    )

    if verbose:
        i = 0
        for solver, config, instance, run in jobs:
            print(
                f"[{i + 1}]: Solver: "
                f"{Path(solver).name} ({config}), Instance: "
                f"{Path(instance).name}"
            )
            i += 1


def main(argv: list[str]) -> None:
    """Main function of the status command."""
    # Log command call
    sl.log_command(sys.argv, gv.settings().random_state)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)

    print("========Sparkle System Status========\n")
    print_objects_list(
        [s for s in gv.settings().DEFAULT_solver_dir.iterdir()],
        "Solver",
        args.verbosity,
    )
    if args.verbosity:
        print()
    print_objects_list(
        [e for e in gv.settings().DEFAULT_extractor_dir.iterdir()],
        "Extractor",
        args.verbosity,
    )
    if args.verbosity:
        print()
    print_objects_list(
        [i for i in gv.settings().DEFAULT_instance_dir.iterdir()],
        "Instance Set",
        args.verbosity,
    )

    print()
    print_feature_computation_jobs(
        gv.settings().DEFAULT_feature_data_path, args.verbosity
    )
    print_performance_computation_jobs(performance_data, args.verbosity)

    if args.verbosity:
        print("\nThe Performance Data overview:")
        print(performance_data)

    # scan configurator log files for warnings
    configurator = gv.settings().configurator
    configurator.get_status_from_logs(
        gv.settings().get_configurator_output_path(configurator)
    )

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
