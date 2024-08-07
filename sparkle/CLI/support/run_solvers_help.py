#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to run solvers."""
from __future__ import annotations
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Run
from runrunner.slurm import SlurmRun

from sparkle.platform import CommandName
from sparkle.instance import InstanceSet
from sparkle.tools.runsolver_parsing import get_solver_output

from sparkle.CLI.help import global_variables as gv
from sparkle.platform.settings_objects import SolutionVerifier
from sparkle.solver import Solver
from sparkle.solver import sat as sh
import sparkle.tools.general as tg
from sparkle.tools.runsolver_parsing import handle_timeouts
from sparkle.types import SolverStatus


def call_solver(
        instance_set: InstanceSet,
        solver: Solver,
        config: str | Path = None,
        seed: int | list[int] = 42,
        outdir: Path = None,
        commandname: CommandName = CommandName.RUN_SOLVERS,
        dependency: SlurmRun | list[SlurmRun] = None,
        run_on: Runner = Runner.SLURM) -> Run:
    """Run a solver on all given instances.

    Args:
        instance_list: A list of all paths in a directory of instances.
        solver: The solver to run on the instances
        config: The configuration with which to run. Can be direct configuration string,
            or file from which to read. If specific line from file is needed, seed
            should be specified.
        seed: The seed for the solver.
        outdir: Path where to place the output files of the (run) solver logs
        commandname: The commandname under which to run the process.
        dependency: The jobs it depends on to finish before starting.
        run_on: Whether the command is run with Slurm or not.

    Returns:
        The Runrunner Run object regarding the call.
    """
    custom_cutoff = gv.settings().get_general_target_cutoff_time()
    cmd_list = []
    runsolver_args_list = []
    solver_params_list = []
    for index, instance_path in enumerate(instance_set.instance_paths):
        raw_result_path = Path(f"{solver.name}_{instance_set._instance_names[index]}"
                               f"_{tg.get_time_pid_random_string()}.rawres")
        runsolver_watch_data_path = raw_result_path.with_suffix(".log")
        runsolver_values_path = raw_result_path.with_suffix(".val")

        runsolver_args = ["--timestamp", "--use-pty",
                          "--cpu-limit", str(custom_cutoff),
                          "-w", runsolver_watch_data_path,
                          "-v", runsolver_values_path,
                          "-o", raw_result_path]
        if isinstance(config, str):
            solver_params = solver.config_str_to_dict(config)
        elif isinstance(config, Path):
            solver_params = {"config_path": config}
        else:
            solver_params = {}
        solver_params["specifics"] = "rawres"
        solver_params["cutoff_time"] = custom_cutoff
        solver_params["run_length"] = "2147483647"  # Arbitrary, not used by SMAC wrapper
        if seed is None:
            solver_params["seed"] = gv.get_seed()
        else:
            # Use the seed to determine the configuration line in the file
            if isinstance(seed, list):
                solver_params["seed"] = seed[index]
            else:
                solver_params["seed"] = seed
        runsolver_args_list.append(runsolver_args)
        solver_params_list.append(solver_params)
        if isinstance(instance_path, list):
            instance_path = [p.absolute() for p in instance_path]
        else:
            instance_path = instance_path.absolute()
        solver_cmd = solver.build_cmd(instance_path,
                                      solver_params, runsolver_args)
        cmd_list.append(" ".join(solver_cmd))

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    srun_options = ["-N1", "-n1"] + sbatch_options
    # Make sure the executable dir exists
    if outdir is None:
        outdir = solver.raw_output_directory
    outdir.mkdir(exist_ok=True, parents=True)

    if run_on == Runner.LOCAL:
        print(f"\nStart running solver on {instance_set.size} instances...")
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=commandname,
        base_dir=gv.settings().DEFAULT_tmp_output,
        path=outdir,
        dependencies=dependency,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    if run_on == Runner.LOCAL:
        # Wait for all jobs to complete before printing
        run.wait()
        # Jobs are sorted in the cmd list order
        for index, job in enumerate(run.jobs):
            # Run the configured solver
            job.wait()
            output_log = outdir / runsolver_args_list[index][-1]
            solver_output = get_solver_output(runsolver_args_list[index],
                                              output_log.read_text(),
                                              solver.raw_output_directory)
            # Output results to user, including path to rawres_solver
            print(f"Execution of {solver.name} on instance {Path(instance_path).name} "
                  f"completed with status {solver_output['status']} in "
                  f"{solver_output['runtime']} seconds.")
            print("Raw output can be found at: "
                  f"{solver.raw_output_directory / raw_result_path}.\n")

    return run


def run_solver_on_instance_and_process_results(
        solver: Solver, instance: Path | list[Path], custom_cutoff: int,
        seed: int) -> tuple[float, float, float, list[float], str, Path]:
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
                        gv.settings().get_penalised_time(custom_cutoff))
    status = verify(instance, raw_result_path, solver, status)
    return (solver_output["cpu_time"], solver_output["wc_time"],
            cpu_time_penalised, solver_output["quality"], status, raw_result_path)


def verify(instance: Path, raw_result: Path, solver: Solver, status: str)\
        -> str:
    """Run a solution verifier on the solution and update the status if needed."""
    verifier = gv.settings().get_general_solution_verifier()
    # Use verifier if one is given and the solver did not time out
    if verifier == SolutionVerifier.SAT and status != SolverStatus.TIMEOUT \
            and status != SolverStatus.UNKNOWN:
        return sh.sat_verify(instance, raw_result, solver)
    return status
