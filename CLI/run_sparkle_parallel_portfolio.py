#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to execute a parallel algorithm portfolio.."""

import sys
import argparse
import random
import time
import shutil
from pathlib import Path, PurePath

from runrunner.base import Runner

from CLI.help.reporting_scenario import Scenario
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
import global_variables as gv
from sparkle.platform.settings_help import SettingState, Settings
from sparkle.solver.solver import Solver
from CLI.support import run_parallel_portfolio_help as srpp
from CLI.help import command_help as sch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancePathsRunParallelPortfolioArgument.names,
                        **ac.InstancePathsRunParallelPortfolioArgument.kwargs)
    parser.add_argument(
        "--portfolio-name",
        type=Path,
        help="Specify a name of the portfolio. If none is given, one will be generated."
    )
    parser.add_argument(
        "--solvers",
        type=list[str],
        nargs="+",
        help="Specify the list of solvers to be used. If not specifed, all solvers known"
             " in Sparkle will be employed."
    )
    parser.add_argument(*ac.ProcessMonitoringArgument.names,
                        **ac.ProcessMonitoringArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
    parser.add_argument(*ac.CutOffTimeArgument.names,
                        **ac.CutOffTimeArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Initialise settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    if args.solvers is not None:
        solver_names = ["".join(s) for s in args.solvers]
        solvers = [Solver.get_solver_by_name(solver) for solver in solver_names]
        if None in solvers:
            print("Some solvers not recognised! Check solver names:")
            for i, name in enumerate(solver_names):
                if solvers[i] is None:
                    print(f'\t- "{solver_names[i]}" ')
            sys.exit(-1)
    else:
        solvers = [Solver.get_solver_by_name(p) for p in gv.solver_dir.iterdir()]

    check_for_initialise(
        sys.argv,
        sch.COMMAND_DEPENDENCIES[sch.CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO]
    )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    # Do first, so other command line options can override settings from the file
    if args.settings_file is not None:
        gv.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    portfolio_path = args.portfolio_name
    run_on = args.run_on

    if run_on == Runner.LOCAL:
        print("Parallel Portfolio is not fully supported yet for Local runs. Exiting.")
        sys.exit(-1)

    # Create list of instance paths
    instance_paths = []

    for instance in args.instance_paths:
        instance_path = Path(instance)
        if not instance_path.exists():
            print(f'Instance "{instance}" not found, aborting the process.')
            sys.exit(-1)
        if instance_path.is_file():
            print(f"Running on instance {instance}")
            instance_paths.append(instance)
        elif not instance_path.is_dir():
            instance_path = gv.instance_dir / instance

        if instance_path.is_dir():
            items = [instance_path / p.name for p in Path(instance).iterdir()
                     if p.is_file()]
            print(f"Running on {len(items)} instance(s) from "
                  f"directory {instance}")
            instance_paths.extend(items)

    if args.cutoff_time is not None:
        gv.settings.set_general_target_cutoff_time(args.cutoff_time,
                                                   SettingState.CMD_LINE)

    if args.process_monitoring is not None:
        gv.settings.set_paraport_process_monitoring(args.process_monitoring,
                                                    SettingState.CMD_LINE)

    if args.performance_measure is not None:
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)
    if gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure\
            is not PerformanceMeasure.RUNTIME:
        print("ERROR: Parallel Portfolio is currently only relevant for "
              f"{PerformanceMeasure.RUNTIME} measurement. In all other cases, "
              "use validation")
        sys.exit(-1)
    # Write settings to file before starting, since they are used in callback scripts
    gv.settings.write_used_settings()

    print("Sparkle parallel portfolio is running ...")
    if args.portfolio_name is not None:  # Use a nickname
        portfolio_path = gv.parallel_portfolio_output_raw / args.portfolio_name
    else:  # Generate a timestamped nickname
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        randintstamp = int(random.getrandbits(32))
        portfolio_path = gv.parallel_portfolio_output_raw / f"{timestamp}_{randintstamp}"
    if portfolio_path.exists():
        print(f"[WARNING] Portfolio path {portfolio_path} already exists! "
              "Overwrite? [y/n] ", end="")
        user_input = input()
        if user_input != "y":
            sys.exit()
        shutil.rmtree(portfolio_path)
    portfolio_path.mkdir(parents=True)
    srpp.run_parallel_portfolio(instance_paths, portfolio_path, solvers, run_on=run_on)

    # Update latest scenario
    gv.latest_scenario().set_parallel_portfolio_path(portfolio_path)
    gv.latest_scenario().set_latest_scenario(Scenario.PARALLEL_PORTFOLIO)
    gv.latest_scenario().set_parallel_portfolio_instance_list(instance_paths)
    # NOTE: Patching code to make sure generate report still works
    solvers_file = portfolio_path / "solvers.txt"
    with solvers_file.open("w") as fout:
        for solver in solvers:
            fout.write(f"{solver.directory}\n")
    print("Running Sparkle parallel portfolio is done!")

    # Write used settings to file
    gv.settings.write_used_settings()
