#!/usr/bin/env python3
"""Sparkle command to add a solver to the Sparkle platform."""
import os
import stat
import sys
import argparse
import shutil
from pathlib import Path

import runrunner as rrr

from sparkle.platform import file_help as sfh, settings_help
import global_variables as gv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.run_solvers import running_solvers_performance_data
from sparkle.solver import Solver
import sparkle_logging as sl
from CLI.help.command_help import CommandName
from CLI.help import command_help as ch
from CLI.help import slurm_help as ssh
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a solver to the Sparkle platform.",
        epilog="")
    parser.add_argument(*apc.DeterministicArgument.names,
                        **apc.DeterministicArgument.kwargs)
    group_solver_run = parser.add_mutually_exclusive_group()
    group_solver_run.add_argument(*apc.RunSolverNowArgument.names,
                                  **apc.RunSolverNowArgument.kwargs)
    group_solver_run.add_argument(*apc.RunExtractorLaterArgument.names,
                                  **apc.RunSolverLaterArgument.kwargs)
    parser.add_argument(*apc.NicknameSolverArgument.names,
                        **apc.NicknameSolverArgument.kwargs)
    parser.add_argument(*apc.ParallelArgument.names,
                        **apc.ParallelArgument.kwargs)
    parser.add_argument(*apc.SolverVariationsArgument.names,
                        **apc.SolverVariationsArgument.kwargs)
    parser.add_argument(*apc.SolverPathArgument.names,
                        **apc.SolverPathArgument.kwargs)
    parser.add_argument(*apc.RunOnArgument.names,
                        **apc.RunOnArgument.kwargs)
    parser.add_argument(
        "--skip-checks",
        dest="run_checks",
        default=True,
        action="store_false",
        help="Checks the solver's functionality by testing it on an instance "
             "and the pcs file, when applicable."
    )
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver_source = Path(args.solver_path)

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.ADD_SOLVER])

    if not solver_source.exists():
        print(f'Solver path "{solver_source}" does not exist!')
        sys.exit(-1)

    deterministic = args.deterministic
    nickname_str = args.nickname
    my_flag_parallel = args.parallel
    solver_variations = args.solver_variations
    run_on = args.run_on

    if solver_variations < 1:
        print("ERROR: Invalid number of solver variations given "
              f"({str(solver_variations)}), "
              "a postive integer must be used. Stopping execution.")
        sys.exit(-1)

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

        configurator_wrapper_path = solver_source / gv.sparkle_solver_wrapper
        if not (configurator_wrapper_path.is_file()
                and sfh.check_file_is_executable(configurator_wrapper_path)):
            print(f"WARNING: Solver {solver_source.name} does not have a solver wrapper "
                  f"(Missing file {gv.sparkle_solver_wrapper}) or is not executable. ")

    # Start add solver
    solver_directory = gv.solver_dir / solver_source.name
    if not Path(solver_directory).exists():
        Path(solver_directory).mkdir(parents=True, exist_ok=True)
    else:
        print(f"ERROR: Solver {solver_source.name} already exists! "
              "Can not add new solver.")
        sys.exit(-1)
    shutil.copytree(solver_source, solver_directory, dirs_exist_ok=True)
    # Save the deterministic bool in the solver
    with (solver_directory / Solver.meta_data).open("w+") as fout:
        fout.write(str({"deterministic": deterministic}))

    # Add RunSolver executable to the solver
    runsolver_path = gv.runsolver_path
    if runsolver_path.name in [file.name for file in Path(solver_directory).iterdir()]:
        print("Warning! RunSolver executable detected in Solver "
              f"{Path(solver_source).name}. This will be replaced with "
              f"Sparkle's version of RunSolver. ({runsolver_path})")
    runsolver_target = Path(solver_directory) / runsolver_path.name
    shutil.copyfile(runsolver_path, runsolver_target)
    runsolver_target.chmod(os.stat(runsolver_target).st_mode | stat.S_IEXEC)

    performance_data = PerformanceDataFrame(
        gv.performance_data_csv_path,
        objectives=gv.settings.get_general_sparkle_objectives())
    performance_data.add_solver(solver_directory)
    performance_data.save_csv()
    sfh.add_remove_platform_item(
        f"{solver_directory} {deterministic} {solver_variations}",
        gv.solver_list_path,
        gv.file_storage_data_mapping[gv.solver_list_path])

    print(f"Adding solver {solver_source.name} done!")

    if Path(gv.sparkle_algorithm_selector_path).exists():
        sfh.rmfiles(gv.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{gv.sparkle_algorithm_selector_path} done!")

    if nickname_str is not None:
        sfh.add_remove_platform_item(solver_directory,
                                     gv.solver_nickname_list_path, key=nickname_str)

    if args.run_solver_now:
        num_job_in_parallel = gv.settings.get_slurm_number_of_runs_in_parallel()
        dependency_run_list = [running_solvers_performance_data(
            gv.performance_data_csv_path, num_job_in_parallel,
            rerun=False, run_on=run_on
        )]

        sbatch_options = ssh.get_slurm_options_list()
        srun_options = ["-N1", "-n1"] + ssh.get_slurm_options_list()
        run_construct_portfolio_selector = rrr.add_to_queue(
            cmd="CLI/construct_sparkle_portfolio_selector.py",
            name=CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
            dependencies=dependency_run_list,
            base_dir=gv.sparkle_tmp_path,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

        dependency_run_list.append(run_construct_portfolio_selector)

        run_generate_report = rrr.add_to_queue(
            cmd="CLI/generate_report.py",
            name=CommandName.GENERATE_REPORT,
            dependencies=dependency_run_list,
            base_dir=gv.sparkle_tmp_path,
            sbatch_options=sbatch_options,
            srun_options=srun_options)

    # Write used settings to file
    gv.settings.write_used_settings()
