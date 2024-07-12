#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to run solvers."""
from __future__ import annotations
from pathlib import Path

import global_variables as gv
import tools.general as tg
from sparkle.platform.settings_help import SolutionVerifier
from sparkle.solver import Solver
from sparkle.solver import sat_help as sh
from tools.runsolver_parsing import handle_timeouts


def run_solver_on_instance_and_process_results(
        solver: Solver, instance_path: str | list[str], seed_str: str = None,
        custom_cutoff: int = None) -> tuple[float, float, float, list[float], str, str]:
    """Prepare and run a given the solver and instance, and process output."""
    # Prepare paths
    if isinstance(instance_path, list):
        instance_name = Path(instance_path[0]).name
    else:
        instance_name = Path(instance_path).name
    raw_result_path = (f"{gv.sparkle_tmp_path}/"
                       f"{solver.name}_"
                       f"{instance_name}_"
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
    solver_output = solver.run(
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
    status = verify(instance_path, raw_result_path, solver.directory, status)
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
