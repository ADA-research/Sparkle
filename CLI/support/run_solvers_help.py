#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to run solvers."""
from __future__ import annotations
from pathlib import Path

from CLI.help import global_variables as gv
from sparkle.platform.settings_objects import SolutionVerifier
from sparkle.solver import Solver
from sparkle.solver import sat_help as sh
import sparkle.tools.general as tg
from sparkle.tools.runsolver_parsing import handle_timeouts


def run_solver_on_instance_and_process_results(
        solver: Solver, instance: Path | list[Path], custom_cutoff: int,
        seed: int) -> tuple[float, float, float, list[float], str, str]:
    """Prepare and run a given the solver and instance, and process output.

    Args:
        solver: The solver to run on the instance
        instance: The path(s) to the instance file(s)
        custom_cutoff: The cutoff time for the solver
        seed: The seed for the solver

    Returns:
        tuple of the form:
            (cpu_time, wc_time, runtime, cpu_times, status, raw_result_path)
    """
    # Prepare paths
    if isinstance(instance, list):
        instance_name = instance[0].name
    else:
        instance_name = instance.name

    # Prepare runsolver call
    raw_result_path = solver.raw_output_directory /\
        f"{solver.name}_{instance_name}_{tg.get_time_pid_random_string()}.rawres"
    runsolver_watch_data_path = raw_result_path.with_suffix(".log")
    runsolver_values_path = raw_result_path.with_suffix(".val")
    solver_output = solver.run(
        instance,
        configuration={"seed": seed,
                       "cutoff_time": custom_cutoff,
                       "specifics": ""},
        runsolver_configuration=["--timestamp", "--use-pty",
                                 "--cpu-limit", str(custom_cutoff),
                                 "-w", runsolver_watch_data_path,
                                 "-v", runsolver_values_path,
                                 "-o", raw_result_path],
        cwd=Path.cwd())

    cpu_time_penalised, status =\
        handle_timeouts(solver_output["runtime"],
                        solver_output["status"],
                        custom_cutoff,
                        gv.settings.get_penalised_time(custom_cutoff))
    status = verify(instance, raw_result_path, solver.directory, status)
    return (solver_output["cpu_time"], solver_output["wc_time"],
            cpu_time_penalised, solver_output["quality"], status, raw_result_path)


def verify(instance_path: str, raw_result_path: str, solver_path: str, status: str)\
        -> str:
    """Run a solution verifier on the solution and update the status if needed."""
    verifier = gv.settings.get_general_solution_verifier()
    # Use verifier if one is given and the solver did not time out
    if verifier == SolutionVerifier.SAT and status != "TIMEOUT" and status != "UNKNOWN":
        return sh.sat_verify(instance_path, raw_result_path, solver_path)
    return status
