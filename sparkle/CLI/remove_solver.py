#!/usr/bin/env python3
"""Sparkle command to remove a solver from the Sparkle platform."""

import sys
import argparse
import shutil

from sparkle.platform import file_help as sfh
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame
from sparkle.CLI.help import logging as sl
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Remove a solver from the platform.")
    parser.add_argument(*ac.SolverRemoveArgument.names,
                        **ac.SolverRemoveArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the remove solver command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    solver_path = resolve_object_name(
        args.solver,
        gv.file_storage_data_mapping[gv.solver_nickname_list_path],
        gv.settings().DEFAULT_solver_dir)

    if solver_path is None:
        print(f'Could not resolve Solver path/name "{solver_path}"!')
        sys.exit(-1)
    if not solver_path.parent == gv.settings().DEFAULT_solver_dir:
        # Allow user to only specify solvers in Sparkle solver dir
        print("Specified Solver is not is platform directory! Exiting.")
        sys.exit(-1)

    print(f"Start removing solver {solver_path.name} ...")

    solver_nickname_mapping = gv.file_storage_data_mapping[gv.solver_nickname_list_path]
    if len(solver_nickname_mapping):
        nickname = None
        for key in solver_nickname_mapping:
            if solver_nickname_mapping[key] == str(solver_path):
                nickname = key
                break

        sfh.add_remove_platform_item(
            solver_path,
            gv.solver_nickname_list_path,
            gv.file_storage_data_mapping[gv.solver_nickname_list_path],
            key=nickname,
            remove=True)

    if gv.settings().DEFAULT_performance_data_path.exists():
        performance_data = PerformanceDataFrame(
            gv.settings().DEFAULT_performance_data_path)
        if str(solver_path) in performance_data.solvers:
            performance_data.remove_solver(str(solver_path))
        performance_data.save_csv()

    # We unlink symbolics links, erase copies
    if solver_path.is_symlink():
        solver_path.unlink()
    else:
        # Remove the directory and all its files
        shutil.rmtree(solver_path)

    print(f"Removing solver {solver_path.name} done!")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
