#!/usr/bin/env python3
"""Sparkle command to add a solver to the Sparkle platform."""
import os
import stat
import sys
import argparse
import shutil
from pathlib import Path

from sparkle.tools.parameters import PCSConvention

from sparkle.platform import file_help as sfh
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame
from sparkle.solver import Solver, verifiers
from sparkle.CLI.help import logging as sl
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a solver to the Sparkle platform.")
    parser.add_argument(*ac.DeterministicArgument.names,
                        **ac.DeterministicArgument.kwargs)
    parser.add_argument(*ac.SolutionVerifierArgument.names,
                        **ac.SolutionVerifierArgument.kwargs)
    parser.add_argument(*ac.NicknameSolverArgument.names,
                        **ac.NicknameSolverArgument.kwargs)
    parser.add_argument(*ac.SolverPathArgument.names, **ac.SolverPathArgument.kwargs)
    parser.add_argument(*ac.SkipChecksArgument.names, **ac.SkipChecksArgument.kwargs)
    parser.add_argument(*ac.NoCopyArgument.names, **ac.NoCopyArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    solver_source = Path(args.solver_path)
    deterministic = args.deterministic
    solution_verifier = args.solution_verifier

    if not solver_source.exists():
        print(f'Solver path "{solver_source}" does not exist!')
        sys.exit(-1)

    # Make sure it is pointing to the verifiers module
    if solution_verifier:
        if Path(solution_verifier).is_file():  # File verifier
            solution_verifier = (verifiers.SolutionFileVerifier.__name__,
                                 solution_verifier)
        elif solution_verifier not in verifiers.mapping:
            print(f"ERROR: Unknown solution verifier {solution_verifier}!")
            sys.exit(-1)

    nickname = args.nickname

    if args.run_checks:
        print("Running checks...")
        solver = Solver(Path(solver_source))
        if solver.pcs_file is None:
            print("None or multiple .pcs files found. Solver "
                  "is not valid for configuration.")
        else:
            print(f"PCS file detected: {solver.pcs_file.name}. ", end="")
            if solver.read_pcs_file():
                print("Can read the pcs file.")
            else:
                print("WARNING: Can not read the provided pcs file format.")

        configurator_wrapper_path = solver_source / Solver.wrapper
        if not (configurator_wrapper_path.is_file()
                and os.access(configurator_wrapper_path, os.X_OK)):
            print(f"WARNING: Solver {solver_source.name} does not have a solver wrapper "
                  f"(Missing file {Solver.wrapper}) or is not executable. ")

    # Start add solver
    solver_directory = gv.settings().DEFAULT_solver_dir / solver_source.name
    if solver_directory.exists():
        print(f"ERROR: Solver {solver_source.name} already exists! "
              "Can not add new solver.")
        sys.exit(-1)
    if args.no_copy:
        print(f"Creating symbolic link from {solver_source} "
              f"to {solver_directory}...")
        if not os.access(solver_source, os.W_OK):
            raise PermissionError("Sparkle does not have the right to write to the "
                                  "destination folder.")
        solver_directory.symlink_to(solver_source.absolute())
    else:
        print(f"Copying {solver_source.name} to platform...")
        solver_directory.mkdir(parents=True)
        shutil.copytree(solver_source, solver_directory, dirs_exist_ok=True)

    # Save the deterministic bool in the solver
    with (solver_directory / Solver.meta_data).open("w+") as fout:
        fout.write(str({"deterministic": deterministic,
                        "verifier": solution_verifier}))

    # Add RunSolver executable to the solver
    runsolver_path = gv.settings().DEFAULT_runsolver_exec
    if runsolver_path.name in [file.name for file in solver_directory.iterdir()]:
        print("Warning! RunSolver executable detected in Solver "
              f"{solver_source.name}. This will be replaced with "
              f"Sparkle's version of RunSolver. ({runsolver_path})")
    runsolver_target = solver_directory / runsolver_path.name
    shutil.copyfile(runsolver_path, runsolver_target)
    runsolver_target.chmod(os.stat(runsolver_target).st_mode | stat.S_IEXEC)

    performance_data = PerformanceDataFrame(
        gv.settings().DEFAULT_performance_data_path,
        objectives=gv.settings().get_general_sparkle_objectives())
    performance_data.add_solver(str(solver_directory))
    performance_data.save_csv()

    print(f"Adding solver {solver_source.name} done!")

    if nickname is not None:
        sfh.add_remove_platform_item(
            solver_directory,
            gv.solver_nickname_list_path,
            gv.file_storage_data_mapping[gv.solver_nickname_list_path],
            key=nickname)

    solver = Solver(solver_directory)  # Recreate solver from its new directory
    if solver.pcs_file is not None:
        # Generate missing PCS files
        # TODO: Only generate missing files
        print("Generating missing PCS files...")
        solver.port_pcs(PCSConvention.IRACE)  # Create PCS file for IRACE
        print("Generating IRACE done!")
        solver.port_pcs(PCSConvention.ParamILS)  # Create PCS file for ParamILS
        print("Generating ParamILS done!")

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
