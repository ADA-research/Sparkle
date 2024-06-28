#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a (configured) solver on instances."""
from __future__ import annotations

from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

import global_variables as gv
import tools.general as tg
from CLI.help.command_help import CommandName
from sparkle.solver import Solver
from tools.runsolver_parsing import get_solver_output


def call_solver(
        instances_list: list[list[Path]],
        solver: Solver,
        config: str | Path = None,
        seed: int | list[int] = None,
        outdir: Path = None,
        commandname: CommandName = CommandName.RUN_SOLVERS,
        dependency: rrr.SlurmRun | list[rrr.SlurmRun] = None,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
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
        str: The Slurm job id str, SlurmJob if RunRunner Slurm or empty string if local
    """
    # Create an instance list[str] keeping in mind possible multi-file instances
    for index, value in enumerate(instances_list):
        # Flatten the second dimension
        if isinstance(value, list):
            instances_list[index] = " ".join([str(path) for path in value])

    num_jobs = len(instances_list)
    custom_cutoff = gv.settings.get_general_target_cutoff_time()
    cmd_list = []
    runsolver_args_list = []
    solver_params_list = []
    for index, instance_path in enumerate(instances_list):
        instance_path = Path(instance_path)
        raw_result_path = Path(f"{solver.name}_{instance_path.name}"
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
        solver_cmd = solver.build_solver_cmd(instance_path.absolute(),
                                             solver_params, runsolver_args)
        cmd_list.append(" ".join(solver_cmd))

    sbatch_options = gv.settings.get_slurm_extra_options(as_args=True)
    srun_options = ["-N1", "-n1"] + sbatch_options
    # Make sure the executable dir exists
    if outdir is None:
        outdir = solver.raw_output_directory
    outdir.mkdir(exist_ok=True, parents=True)

    if run_on == Runner.LOCAL:
        print(f"\nStart running solver on {len(instances_list)} instances...")
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=commandname,
        parallel_jobs=num_jobs,
        base_dir=gv.sparkle_tmp_path,
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
