"""Command to help users check if their input solvers, datasets etc. are correct."""

import sys
import os
import argparse

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.instance import Instance_Set, InstanceSet
from sparkle.selector.extractor import Extractor
from sparkle.platform import Settings
from sparkle.types import SolverStatus

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to help users check if their input solvers, instance sets "
        "or feature extractors are readable by Sparkle. Specify a path to "
        "an instance to test calling the wrapper."
    )
    parser.add_argument(*ac.CheckTypeArgument.names, **ac.CheckTypeArgument.kwargs)
    parser.add_argument(*ac.CheckPathArgument.names, **ac.CheckPathArgument.kwargs)
    parser.add_argument(*ac.InstancePathOptional.names, **ac.InstancePathOptional.kwargs)
    parser.add_argument(*ac.SeedArgument.names, **ac.SeedArgument.kwargs)
    # Settings arguments
    parser.add_argument(
        *Settings.OPTION_solver_cutoff_time.args,
        **Settings.OPTION_solver_cutoff_time.kwargs,
    )
    return parser


def main(argv: list[str]) -> None:
    """Main entry point of the Check command."""
    parser = parser_function()
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, settings.random_state)

    type_map = {
        "extractor": Extractor,
        "feature-extractor": Extractor,
        "solver": Solver,
        "instance-set": Instance_Set,
        "Extractor": Extractor,
        "Feature-Extractor": Extractor,
        "Instance-Set": Instance_Set,
        "Solver": Solver,
        "FeatureExtractor": Extractor,
        "InstanceSet": Instance_Set,
    }
    type = type_map[args.type]
    print(f"Checking {type.__name__} in directory {args.path} ...")
    object = type(args.path)
    print("Resolved to:")
    print(object.__repr__())

    # Conduct object specific tests
    if isinstance(object, Solver):
        if object.pcs_file:
            print()
            print(object.get_configuration_space())
        if not os.access(object.wrapper_file, os.X_OK):
            print(
                f"Wrapper {object.wrapper_file} is not executable!"
                f"Check that wrapper execution rights are set for all."
            )
            sys.exit(-1)
        if args.instance_path:  # Instance to test with
            object._runsolver_exec = settings.DEFAULT_runsolver_exec
            if not object.runsolver_exec.exists():
                print(
                    f"Runsolver {object.runsolver_exec} not found. "
                    "Checking without Runsolver currently not supported."
                )
            else:
                # Test the wrapper with a dummy call
                print(f"\nTesting Wrapper {object.wrapper} ...")
                # Patchfix runsolver
                objectives = settings.objectives if settings.objectives else []
                cutoff = (
                    settings.solver_cutoff_time if settings.solver_cutoff_time else 5
                )
                configuration = {}
                if object.pcs_file:
                    print("\nSample Configuration:")
                    sample_conf = object.get_configuration_space().sample_configuration()
                    print(sample_conf)
                    configuration = dict(sample_conf)
                result = object.run(
                    instances=args.instance_path,
                    objectives=objectives,
                    seed=42,  # Dummy seed
                    cutoff_time=cutoff,
                    configuration=configuration,
                    log_dir=sl.caller_log_dir,
                    run_on=Runner.LOCAL,
                )
                print("Result:")
                for obj in objectives:  # Check objectives
                    if obj.name not in result:
                        print(f"\tSolver output is missing objective {obj.name}")
                    else:
                        print(f"\t{obj.name}: {result[obj.name]}")
                status_key = [key for key in result.keys() if key.startswith("status")][
                    0
                ]
                if result[status_key] == SolverStatus.UNKNOWN:
                    print(
                        f"Sparkle was unable to process {obj.name} output. "
                        "Check that your wrapper is able to handle KILL SIGNALS. "
                        "It is important to always communicate back to Sparkle "
                        "on regular exit and termination signals for stability."
                    )
                    sys.exit(-1)
    elif isinstance(object, Extractor):
        if args.instance_path:  # Test on an instance
            # Patchfix runsolver
            object.runsolver_exec = settings.DEFAULT_runsolver_exec
            if not object.runsolver_exec.exists():
                print(
                    f"Runsolver {object.runsolver_exec} not found. "
                    "Checking without Runsolver currently not supported."
                )
            else:
                print(f"\nTesting Wrapper {object.wrapper} ...")
                # cutoff = args.cutoff_time if args.cutoff_time else 20  # Short call
                result = object.run(
                    instance=args.instance_path, log_dir=sl.caller_log_dir
                )
                # Print feature results
                print("Feature values:")
                for f_group, f_name, f_value in result:
                    print(f"\t[{f_group}] {f_name}: {f_value}")
        else:
            print("Feature names:")
            for f_group, fname in object.features:
                print(f"\t{f_group}: {fname}")
    elif isinstance(object, InstanceSet):
        print("\nList of instances:")
        for i_name, i_path in zip(object.instance_names, object.instance_paths):
            print(f"\t{i_name}: {i_path}")

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
