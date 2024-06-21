#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to run solvers."""
from pathlib import Path

import global_variables as gv
import tools.general as tg
from sparkle.platform import file_help as sfh
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.support import sparkle_job_help as sjh
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SolutionVerifier
from sparkle.solver.solver import Solver
from sparkle.solver import sat_help as sssh
from tools.runsolver_parsing import handle_timeouts


def run_solver_on_instance_and_process_results(
        solver_path: str, instance_path: str, seed_str: str = None,
        custom_cutoff: int = None) -> tuple[float, float, float, list[float], str, str]:
    """Prepare and run a given the solver and instance, and process output."""
    # Prepare paths
    # TODO: Fix result path for multi-file instances (only a single file is part of the
    # result path)
    raw_result_path = (f"{gv.sparkle_tmp_path}"
                       f"{Path(solver_path).name}_"
                       f"{Path(instance_path).name}_"
                       f"{tg.get_time_pid_random_string()}.rawres")
    runsolver_values_path = raw_result_path.replace(".rawres", ".val")

    # Run
    if custom_cutoff is None:
        custom_cutoff = gv.settings.get_general_target_cutoff_time()
    if seed_str is None:
        seed_str = str(gv.get_seed())
    # Prepare runsolver call
    runsolver_values_log = f"{runsolver_values_path}"
    runsolver_watch_data_path = runsolver_values_log.replace("val", "log")
    raw_result_path_option = f"{raw_result_path}"
    solver = Solver(Path(solver_path))
    solver_output = solver.run_solver(
        instance_path,
        configuration={"seed": seed_str,
                       "cutoff_time": custom_cutoff,
                       "specifics": ""},
        runsolver_configuration=["--timestamp", "--use-pty",
                                 "--cpu-limit", str(custom_cutoff),
                                 "-w", runsolver_watch_data_path,
                                 "-v", runsolver_values_log,
                                 "-o", raw_result_path_option],
        cwd=Path.cwd())

    cpu_time_penalised, status =\
        handle_timeouts(solver_output["runtime"],
                        solver_output["status"],
                        custom_cutoff,
                        gv.settings.get_penalised_time(custom_cutoff))
    status = verify(instance_path, raw_result_path, solver_path, status)
    return (solver_output["cpu_time"], solver_output["wc_time"],
            cpu_time_penalised, solver_output["quality"], status, raw_result_path)


def running_solvers(performance_data_csv_path: str, rerun: bool) -> None:
    """Run solvers on all instances.

    If rerun is True, rerun for instances with existing performance data.
    """
    cutoff_time_str = str(gv.settings.get_general_target_cutoff_time())
    perf_measure = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    performance_data = PerformanceDataFrame(performance_data_csv_path)

    if rerun:
        list_performance_computation_job = (
            performance_data.get_list_recompute_performance_computation_job())
    else:
        list_performance_computation_job = (
            performance_data.get_list_remaining_performance_computation_job())

    print("The cutoff time per algorithm run to solve an instance is set to "
          f"{cutoff_time_str} seconds", flush=True)

    total_job_num = sjh.get_num_of_total_job_from_list(list_performance_computation_job)
    current_job_num = 1
    print("The total number of jobs to run is: " + str(total_job_num), flush=True)

    # If there are no jobs, stop
    if total_job_num < 1:
        return
    # If there are jobs update performance data ID
    else:
        update_performance_data_id()

    for job in list_performance_computation_job:
        instance_path = job[0]
        solver_list = job[1]
        for solver_path in solver_list:
            print("")
            # TODO: Fix printing of multi-file instance 'path' (only one file name is
            # printed)
            print(f"Solver {Path(solver_path).name} running on "
                  f"instance {Path(instance_path).name} ...")

            _, _, cpu_time_penalised, quality, status, raw_result_path = (
                run_solver_on_instance_and_process_results(solver_path, instance_path))

            if status == "CRASHED":
                print(f'Warning: Solver "{solver_path}" appears to have crashed on '
                      f'instance "{instance_path}" for details see the solver log file '
                      f"at {raw_result_path}")

            # Handle timeouts
            penalised_str = ""
            if (perf_measure == PerformanceMeasure.RUNTIME
               and (status == "TIMEOUT" or status == "UNKNOWN")):
                penalised_str = " (penalised)"

            # If status == 'WRONG' after verification remove solver
            # TODO: Check whether things break when a solver is removed which still has
            # instances left in the job list
            if status == "WRONG":
                remove_faulty_solver(solver_path, instance_path)
                current_job_num += 1
                continue  # Skip to the next job

            # Update performance CSV
            if perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION or\
               perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
                # TODO: Handle the multi-objective case for quality
                performance_data.set_value(quality[0], solver_path, instance_path)
                print(f"Running Result: Status: {status}, Quality{penalised_str}: "
                      f"{str(quality[0])}", flush=True)
            else:
                performance_data.set_value(cpu_time_penalised, solver_path,
                                           instance_path)
                print(f"Running Result: Status {status}, Runtime{penalised_str}: "
                      f"{str(cpu_time_penalised)}", flush=True)

            print(f"Executing Progress: {str(current_job_num)} out of "
                  f"{str(total_job_num)}", flush=True)
            current_job_num += 1

    performance_data.save_csv()
    print(f"Performance data file {performance_data_csv_path} has been updated!",
          flush=True)


def verify(instance_path: str, raw_result_path: str, solver_path: str, status: str)\
        -> str:
    """Run a solution verifier on the solution and update the status if needed."""
    verifier = gv.settings.get_general_solution_verifier()
    # Use verifier if one is given and the solver did not time out
    if verifier == SolutionVerifier.SAT and status != "TIMEOUT" and status != "UNKNOWN":
        return sssh.sat_verify(instance_path, raw_result_path, solver_path)
    return status


def remove_faulty_solver(solver_path: str, instance_path: str) -> None:
    """Remove a faulty solver from Sparkle.

    Input: Path to solver, path to instance it failed on
    """
    solver_name = Path(solver_path).name
    instance_name = Path(instance_path).name
    print(f"Warning: Solver {solver_name} reports the wrong answer "
          f"on instance {instance_name}!\n"
          f"Warning: Solver {solver_name} will be removed!", flush=True)

    # TODO: Fix solver removal from performanc data CSV file
    # performance_data_csv.remove_solver(solver_path)
    sfh.add_remove_platform_item(solver_path,
                                 gv.solver_list_path,
                                 remove=True)
    sfh.add_remove_platform_item(None,
                                 gv.solver_nickname_list_path,
                                 key=solver_path,
                                 remove=True)

    print(f"Solver {solver_name} is a wrong solver, running on instance {instance_name} "
          " ignored!", flush=True)


def update_performance_data_id() -> None:
    """Update the performance data ID."""
    # Get next pd_id
    pd_id = get_performance_data_id() + 1
    # Write new pd_id
    pd_id_path = gv.performance_data_id_path
    with Path(pd_id_path).open("w") as pd_id_file:
        pd_id_file.write(str(pd_id))

    return


def get_performance_data_id() -> int:
    """Return the current performance data ID."""
    pd_id = 0
    if Path(gv.performance_data_id_path).exists():
        pd_id = int(Path(gv.performance_data_id_path).open("r").readline())
    return pd_id
