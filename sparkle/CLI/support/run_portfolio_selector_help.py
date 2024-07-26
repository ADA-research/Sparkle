#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a portfolio selector."""
import sys
from filelock import FileLock, Timeout
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Run

from sparkle.solver import Extractor, Solver
from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame
from sparkle.CLI.support import run_solvers_help as srs

from sparkle.platform import CommandName


# Only called in call_sparkle_portfolio_selector_solve_instance
def call_solver_solve_instance_within_cutoff(
        solver: Solver,
        instance: Path,
        cutoff_time: int,
        performance_data: PerformanceDataFrame = None) -> bool:
    """Call the Sparkle portfolio selector to solve a single instance with a cutoff.

    Args:
        solver: The solver to run on the instance
        instance: The path to the instance
        cutoff_time: The cutoff time for the solver
        performance_data: The dataframe to store the results in

    Returns:
        Whether the instance was solved by the solver
    """
    _, _, cpu_time_penal, _, status, raw_result_path =\
        srs.run_solver_on_instance_and_process_results(solver,
                                                       instance,
                                                       cutoff_time,
                                                       gv.get_seed())
    flag_solved = False
    if status == "SUCCESS" or status == "SAT" or status == "UNSAT":
        flag_solved = True

    if performance_data is not None:
        solver_name = "Sparkle_Portfolio_Selector"
        print(f"Trying to write: {cpu_time_penal}, {solver_name}, {instance}")
        try:
            # Creating a seperate locked file for writing
            lock = FileLock(f"{performance_data.csv_filepath}.lock")
            with lock.acquire(timeout=60):
                # Reload the dataframe to latest version
                performance_data = PerformanceDataFrame(performance_data.csv_filepath)
                performance_data.set_value(cpu_time_penal, solver_name, str(instance))
                performance_data.save_csv()
            lock.release()
        except Timeout:
            print(f"ERROR: Cannot acquire File Lock on {performance_data}.")
    else:
        if flag_solved:
            print(f"Instance solved by solver {solver.name}")
        else:
            print(f"Solver {solver.name} failed to solve the instance with status "
                  f"{status}")
    raw_result_path.unlink(missing_ok=True)
    return flag_solved


# Only called in portfolio_core and run_sparkle_portfolio_selector
def portfolio_selector_solve_instance(
        instance: Path,
        performance_data: PerformanceDataFrame = None) -> None:
    """Call the Sparkle portfolio selector to solve a single instance.

    Args:
        instance: Path to the instance to run on
        performance_data: path to the performance data
    """
    print(f"Running portfolio selector on solving instance {instance} ...")

    cutoff_extractor = gv.settings.get_general_extractor_cutoff_time()
    print(f"Computing features of instance {instance} ...")
    feature_vector = []
    extractor_paths = [p for p in gv.settings.DEFAULT_extractor_dir.iterdir()]
    if len(extractor_paths) == 0:
        print("ERROR: No feature extractor added to Sparkle.")
        sys.exit(-1)
    for extractor_path in extractor_paths:
        extractor = Extractor(Path(extractor_path),
                              gv.settings.DEFAULT_runsolver_exec,
                              gv.settings.DEFAULT_tmp_output)
        # We create a watch log to filter out runsolver output
        runsolver_watch_path = gv.settings.DEFAULT_tmp_output /\
            f"{extractor_path.name}_{instance}.wlog"
        features = extractor.run(instance,
                                 runsolver_args=["--cpu-limit", str(cutoff_extractor),
                                                 "-w", runsolver_watch_path])
        for _, _, value in features:
            feature_vector.append(value)
        runsolver_watch_path.unlink(missing_ok=True)
    print(f"Sparkle computing features of instance {instance} done!")

    print("Sparkle portfolio selector predicting ...")
    selector = gv.settings.get_general_sparkle_selector()
    predict_schedule = selector.run(gv.settings.DEFAULT_algorithm_selector_path,
                                    feature_vector)

    if predict_schedule is None:
        # Selector Failed to produce prediction
        sys.exit(-1)
    print("Predicting done!")
    for solver, cutoff_time in predict_schedule:
        solver = Solver(Path(solver))
        print(f"Calling solver {solver.name} with time budget {cutoff_time} ...")
        flag_solved = call_solver_solve_instance_within_cutoff(
            solver, instance, cutoff_time, performance_data)
        print(f"Calling solver {solver.name} done!")

        if flag_solved:
            return
        else:
            print("The instance is not solved in this call")


# Only called in run_sparkle_portfolio_selector
def run_portfolio_selector_on_instances(
        instances: list[Path],
        performance_data: PerformanceDataFrame,
        portfolio_selector: Path,
        run_on: Runner = Runner.SLURM) -> Run:
    """Call the Sparkle portfolio selector to solve all instances in a directory.

    Args:
        instances: The paths to the instances.
        performance_data: The dataframe to store the results in.
        portfolio_selector: Path to the selector.
        run_on: Whether to run with Slurm or Local.

    Returns:
        RunRunner Run object regarding the selector call.
    """
    for instance_path in instances:
        performance_data.add_instance(str(instance_path))

    performance_data.add_solver(str(portfolio_selector.parent))

    performance_data.save_csv()

    # TODO: Instead of using run_sparkle_portfolio_core.py, we should do here:
    # 1. Get feature data for every feature extractor
    # 2. Use autofolio call to predict the solver per instance with
    #    a dependency on run object of 1
    # 3. Run the solver and place the results in the performance dataframe w dependency
    #    (Difficult, which solver is determined by 2)

    cmd_list = ["python sparkle/CLI/core/run_sparkle_portfolio_core.py "
                f"--performance-data-csv {performance_data.csv_filepath} "
                f"--instance {instance_path}" for instance_path in instances]
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR,
        base_dir=gv.settings.DEFAULT_tmp_output,
        sbatch_options=gv.settings.get_slurm_extra_options(as_args=True),
        srun_options=["-N1", "-n1"])

    return run
