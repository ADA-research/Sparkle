#!/usr/bin/env python3
"""Sparkle command to add a solver to the Sparkle platform."""
import os
import stat
import sys
import argparse
import shutil
from pathlib import Path

import runrunner as rrr

from sparkle.platform import file_help as sfh
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame
from sparkle.CLI.run_solvers import running_solvers_performance_data
from sparkle.solver import Solver
from sparkle.CLI.help import logging as sl
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.platform.settings_objects import SettingState


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a solver to the Sparkle platform.",
        epilog="")
    parser.add_argument(*ac.DeterministicArgument.names,
                        **ac.DeterministicArgument.kwargs)
    parser.add_argument(*ac.RunSolverNowArgument.names,
                        **ac.RunSolverNowArgument.kwargs)
    parser.add_argument(*ac.NicknameSolverArgument.names,
                        **ac.NicknameSolverArgument.kwargs)
    parser.add_argument(*ac.SolverPathArgument.names,
                        **ac.SolverPathArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SkipChecksArgument.names,
                        **ac.SkipChecksArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver_source = Path(args.solver_path)
    deterministic = args.deterministic

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.ADD_SOLVER])

    if not solver_source.exists():
        print(f'Solver path "{solver_source}" does not exist!')
        sys.exit(-1)

    nickname = args.nickname

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    if args.run_checks:
        print("Running checks...")
        solver = Solver(Path(solver_source))
        pcs_file = solver.get_pcs_file()
        if pcs_file is None:
            print("None or multiple .pcs files found. Solver "
                  "is not valid for configuration.")
        else:
            print(f"One pcs file detected: {pcs_file.name}. ", end="")
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
    if not solver_directory.exists():
        solver_directory.mkdir(parents=True, exist_ok=True)
    else:
        print(f"ERROR: Solver {solver_source.name} already exists! "
              "Can not add new solver.")
        sys.exit(-1)
    shutil.copytree(solver_source, solver_directory, dirs_exist_ok=True)
    # Save the deterministic bool in the solver
    with (solver_directory / Solver.meta_data).open("w+") as fout:
        fout.write(str({"deterministic": deterministic}))

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
    performance_data.add_solver(solver_directory)
    performance_data.save_csv()

    print(f"Adding solver {solver_source.name} done!")

    if nickname is not None:
        sfh.add_remove_platform_item(solver_directory,
                                     gv.solver_nickname_list_path, key=nickname)

    if args.run_solver_now:
        num_job_in_parallel = gv.settings().get_number_of_jobs_in_parallel()
        dependency_run_list = [running_solvers_performance_data(
            gv.settings().DEFAULT_performance_data_path, num_job_in_parallel,
            rerun=False, run_on=run_on
        )]

        sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
        srun_options = ["-N1", "-n1"] + sbatch_options
        run_construct_portfolio_selector = rrr.add_to_queue(
            cmd="sparkle/CLI/construct_portfolio_selector.py",
            name=CommandName.CONSTRUCT_PORTFOLIO_SELECTOR,
            dependencies=dependency_run_list,
            base_dir=sl.caller_log_dir,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

        dependency_run_list.append(run_construct_portfolio_selector)

        run_generate_report = rrr.add_to_queue(
            cmd="sparkle/CLI/generate_report.py",
            name=CommandName.GENERATE_REPORT,
            dependencies=dependency_run_list,
            base_dir=sl.caller_log_dir,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

    # Write used settings to file
    gv.settings().write_used_settings()
