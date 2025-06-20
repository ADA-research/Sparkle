"""Command to help users check if their input solvers, datasets etc. are correct."""
import sys
import os
import argparse

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.instance import Instance_Set, InstanceSet
from sparkle.selector.extractor import Extractor
from sparkle.types import SolverStatus

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to help users check if their input solvers, instance sets "
                    "or feature extractors are readable by Sparkle. Specify a path to "
                    "an instance to test calling the wrapper.")
    parser.add_argument(*ac.CheckTypeArgument.names, **ac.CheckTypeArgument.kwargs)
    parser.add_argument(*ac.CheckPathArgument.names, **ac.CheckPathArgument.kwargs)
    parser.add_argument(*ac.InstancePathOptional.names,
                        **ac.InstancePathOptional.kwargs)
    parser.add_argument(*ac.CutOffTimeArgument.names,
                        **ac.CutOffTimeArgument.kwargs)
    parser.add_argument(*ac.SeedArgument.names,
                        **ac.SeedArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main entry point of the Check command."""
    # Log command call
    sl.log_command(sys.argv)
    parser = parser_function()
    args = parser.parse_args(argv)
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
        "InstanceSet": Instance_Set}
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
        if not os.access(object.wrapper_path, os.X_OK):
            print(f"Wrapper {object.wrapper_path} is not executable!"
                  f"Check that wrapper execution rights are set for all.")
            sys.exit(-1)
        if args.instance_path:  # Instance to test with
            # Test the wrapper with a dummy call
            print(f"\nTesting Wrapper {object.wrapper} ...")
            # Patchfix runsolver
            object.runsolver_exec = gv.settings().DEFAULT_runsolver_exec

            objectives = gv.settings().get_general_sparkle_objectives()
            cutoff = args.cutoff_time if args.cutoff_time else 5  # Short call
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
                run_on=Runner.LOCAL)
            print("Result:")
            for obj in objectives:  # Check objectives
                if obj.name not in result:
                    print(f"\tSolver output is missing objective {obj.name}")
                else:
                    print(f"\t{obj.name}: {result[obj.name]}")
            if result["status"] == SolverStatus.UNKNOWN:
                print(f"Sparkle was unable to process {obj.name} output. "
                      "Check that your wrapper is able to handle KILL SIGNALS. "
                      "It is important to always communicate back to Sparkle "
                      "on regular exit and termination signals for stability.")
                sys.exit(-1)
    elif isinstance(object, Extractor):
        if args.instance_path:  # Test on an instance
            # Patchfix runsolver
            object.runsolver_exec = gv.settings().DEFAULT_runsolver_exec
            print(f"\nTesting Wrapper {object.wrapper} ...")
            # cutoff = args.cutoff_time if args.cutoff_time else 20  # Short call
            result = object.run(instance=args.instance_path,
                                log_dir=sl.caller_log_dir)
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


if __name__ == "__main__":
    main(sys.argv[1:])
