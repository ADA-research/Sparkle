#!/usr/bin/env python3
"""Sparkle command to add a solver to the Sparkle platform."""
import os
import stat
import sys
import argparse
import shutil
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_run_solvers_help as srs
from Commands.sparkle_help import sparkle_run_solvers_parallel_help as srsp
from Commands.sparkle_help import sparkle_add_solver_help as sash
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_settings
from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help import sparkle_command_help as sch
from Commands.sparkle_help import sparkle_slurm_help as ssh


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a solver to the Sparkle platform.",
        epilog="")
    parser.add_argument(
        "--deterministic",
        required=True,
        type=int,
        choices=[0, 1],
        help="indicate whether the solver is deterministic or not",
    )
    group_solver_run = parser.add_mutually_exclusive_group()
    group_solver_run.add_argument(
        "--run-solver-now",
        default=False,
        action="store_true",
        help="immediately run the newly added solver on all instances",
    )
    group_solver_run.add_argument(
        "--run-solver-later",
        dest="run_solver_now",
        action="store_false",
        help="do not immediately run the newly added solver on all instances (default)",
    )
    parser.add_argument(
        "--nickname",
        type=str,
        help="set a nickname for the solver"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the solver on multiple instances in parallel",
    )
    parser.add_argument(
        "--solver-variations",
        default=1,
        type=int,
        help=("Use this option to add multiple variations of the solver by using a "
              "different random seed for each varation."))
    parser.add_argument(
        "solver_path",
        metavar="solver-path",
        type=str,
        help="path to the solver"
    )
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        choices=[Runner.LOCAL, Runner.SLURM],
        help=("On which computer or cluster environment to execute the calculation.")
    )
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver_source = args.solver_path

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.ADD_SOLVER])

    if not Path(solver_source).exists():
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

    configurator_wrapper_path = Path(solver_source,
                                     sgh.sparkle_solver_wrapper)
    if configurator_wrapper_path.is_file():
        sfh.check_file_is_executable(configurator_wrapper_path)
    else:
        print("WARNING: The solver does not have a configurator wrapper. "
              "Therefore it cannot be automatically be configured.")

    # Start add solver
    last_level_directory = ""
    last_level_directory = sfh.get_last_level_directory_name(solver_source)

    solver_directory = sash.get_solver_directory(last_level_directory)
    if not Path(solver_directory).exists():
        Path(solver_directory).mkdir(parents=True, exist_ok=True)
    else:
        print(f"Solver {last_level_directory} already exists!")
        print(f"Do not add solver {last_level_directory}")
        sys.exit(-1)
    shutil.copytree(solver_source, solver_directory, dirs_exist_ok=True)

    # Add RunSolver executable to the solver
    runsolver_path = Path(sgh.runsolver_path)
    if runsolver_path.name in [file.name for file in Path(solver_directory).iterdir()]:
        print("Warning! RunSolver executable detected in Solver "
              f"{Path(solver_source).name}. This will be replaced with "
              f"Sparkle's version of RunSolver. ({runsolver_path})")
    runsolver_target = Path(solver_directory) / runsolver_path.name
    shutil.copyfile(runsolver_path, runsolver_target)
    runsolver_target.chmod(os.stat(runsolver_target).st_mode | stat.S_IEXEC)

    performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        sgh.performance_data_csv_path
    )
    performance_data_csv.add_column(solver_directory)
    performance_data_csv.update_csv()
    sfh.add_remove_platform_item(
        f"{solver_directory} {deterministic} {solver_variations}", sgh.solver_list_path)

    if sash.check_adding_solver_contain_pcs_file(solver_directory):
        print("One pcs file detected, this is a configurable solver.")

    print(f"Adding solver {sfh.get_last_level_directory_name(solver_directory)} "
          "done!")

    if Path(sgh.sparkle_algorithm_selector_path).exists():
        sfh.rmfiles(sgh.sparkle_algorithm_selector_path)
        print("Removing Sparkle portfolio selector "
              f"{sgh.sparkle_algorithm_selector_path} done!")

    if Path(sgh.sparkle_report_path).exists():
        sfh.rmfiles(sgh.sparkle_report_path)
        print(f"Removing Sparkle report {sgh.sparkle_report_path} done!")

    if nickname_str is not None:
        sfh.add_remove_platform_item(solver_directory,
                                     sgh.solver_nickname_list_path, key=nickname_str)

    if args.run_solver_now:
        if not my_flag_parallel:
            print("Start running solvers ...")
            srs.running_solvers(sgh.performance_data_csv_path, rerun=False)
            print(f"Performance data file {sgh.performance_data_csv_path}"
                  " has been updated!")
            print("Running solvers done!")
        else:
            num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
            dependency_run_list = [srsp.running_solvers_parallel(
                sgh.performance_data_csv_path, num_job_in_parallel,
                rerun=False, run_on=run_on
            )]

            sbatch_options = ssh.get_slurm_options_list()
            srun_options = ["-N1", "-n1"] + ssh.get_slurm_options_list()
            run_construct_portfolio_selector = rrr.add_to_queue(
                cmd="Commands/construct_sparkle_portfolio_selector.py",
                name=CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
                dependencies=dependency_run_list,
                base_dir=sgh.sparkle_tmp_path,
                sbatch_options=sbatch_options,
                srun_options=srun_options)

            dependency_run_list.append(run_construct_portfolio_selector)

            run_generate_report = rrr.add_to_queue(
                cmd="Commands/generate_report.py",
                name=CommandName.GENERATE_REPORT,
                dependencies=dependency_run_list,
                base_dir=sgh.sparkle_tmp_path,
                sbatch_options=sbatch_options,
                srun_options=srun_options)

    # Write used settings to file
    sgh.settings.write_used_settings()
