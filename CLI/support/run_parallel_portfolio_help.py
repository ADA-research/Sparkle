#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a parallel portfolio."""
import time
import csv
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner
from runrunner.slurm import Status

import global_variables as gv
from sparkle.platform import slurm_help as ssh
from sparkle.solver.solver import Solver
from CLI.help.command_help import CommandName
from tools.runsolver_parsing import get_runtime, get_status


def run_parallel_portfolio(instances: list[Path],
                           portfolio_path: Path,
                           solvers: list[Solver],
                           run_on: Runner = Runner.SLURM) -> None:
    """Run the parallel algorithm portfolio.

    Args:
        instances: List of instance Paths.
        portfolio_path: Path to the parallel portfolio.
        solvers: List of solvers to run on the instances.
        run_on: Currently only supports Slurm.
    """
    solver_list = [solver.directory for solver in solvers]
    num_solvers, num_instances = len(solver_list), len(instances)
    num_jobs = num_solvers * num_instances
    parallel_jobs = min(gv.settings.get_slurm_number_of_runs_in_parallel(), num_jobs)
    if parallel_jobs > num_jobs:
        print("WARNING: Not all jobs will be started at the same time due to the "
              "limitation of number of Slurm jobs that can be run in parallel. Check"
              " your Sparkle Slurm Settings.")
    cmd_list, runsolver_logs = [], []
    cutoff = gv.settings.get_general_target_cutoff_time()
    log_timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.gmtime(time.time()))
    run_status_path = portfolio_path / "run-status-path"
    run_status_path.mkdir()
    # Create a command for each instance-solver combination
    for instance in instances:
        for solver in solvers:
            runsolver_watch_log =\
                run_status_path / f"{solver.name}_{instance.name}_{log_timestamp}.log"
            runsolver_values_log =\
                run_status_path / f"{solver.name}_{instance.name}_{log_timestamp}.var"
            raw_result_path =\
                run_status_path / f"{solver.name}_{instance.name}_{log_timestamp}.raw"
            solver_call_list = solver.build_solver_cmd(
                str(instance),
                configuration={"specifics": "",
                               "seed": 1,
                               "cutoff_time": cutoff,
                               "run_length": cutoff},
                runsolver_configuration=["--timestamp", "--use-pty",
                                         "--cpu-limit", str(cutoff),
                                         "-w", runsolver_watch_log,
                                         "-v", runsolver_values_log,
                                         "-o", raw_result_path])

            cmd_list.append((" ".join(solver_call_list)).replace("'", '"'))
            runsolver_logs.append([runsolver_watch_log,
                                   runsolver_values_log,
                                   raw_result_path])

    # Jobs are added in to the runrunner object in the same order they are provided
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO,
        parallel_jobs=parallel_jobs,
        path=".",
        base_dir=gv.sparkle_tmp_path,
        srun_options=["-N1", "-n1"] + ssh.get_slurm_options_list(),
        sbatch_options=ssh.get_slurm_options_list()
    )

    check_interval = 4 #NOTE: This should be a setting
    instances_done = [False] * num_instances
    job_output_dict = {instance.name: {solver.name: {"killed": False,
                                                     "cpu-time": -1.0,
                                                     "wc-time": -1.0,
                                                     "status": "UNKNOWN"}
                                       for solver in solvers}
                       for instance in instances}
    while not all(instances_done):
        time.sleep(check_interval)
        job_status_list = [r.status for r in run.jobs]
        job_status_completed = [status == Status.COMPLETED for status in job_status_list]
        # The jobs are sorted by instance
        for i, instance in enumerate(instances):
            if instances_done[i]:
                continue
            if any(job_status_completed[i * num_solvers:(i + 1) * num_solvers]):
                instances_done[i] = True
                # Kill all running jobs for this instance
                for job_index in range(i * num_solvers, (i + 1) * num_solvers):
                    if not job_status_completed[job_index]:
                        run.jobs[job_index].kill()
                        solver_name = solvers[job_index % num_solvers].name
                        job_output_dict[instance.name][solver_name]["killed"] = True
                        job_output_dict[instance.name][solver_name]["status"] = "KILLED"

    # Now we iterate over the logs to get the runtime values
    for index, solver_logs in enumerate(runsolver_logs):
        solver_name = solvers[index % num_solvers].name
        instance_name = instances[int(index / num_solvers)].name
        if not solver_logs[1].exists(): # Runsolver is still wrapping up
            time.sleep(5)
        cpu_time, wallclock_time = get_runtime(solver_logs[1])
        job_output_dict[instance_name][solver_name]["cpu-time"] = cpu_time
        job_output_dict[instance_name][solver_name]["wc-time"] = wallclock_time
        if not job_output_dict[instance_name][solver_name]["killed"]:
            job_output_dict[instance_name][solver_name]["status"] =\
                get_status(solver_logs[1], solver_logs[2])

    for index, instance in enumerate(instances):
        index_print = f"[{index + 1}/{num_instances}] "
        if not instances_done[index]:
            print(f"{index_print}{instance.name} was not solved within the cutoff-time.")
            continue
        print(f"\n{index_print}{instance.name} yielded the following Solver results:")
        for sindex in range(index * num_solvers, (index + 1) * num_solvers):
            solver_name = solvers[sindex % num_solvers].name
            job_info = job_output_dict[instance.name][solver_name]
            print(f"\t- {solver_name} ended with status {job_info['status']} in "
                  f"{job_info['cpu-time']}s CPU-Time ({job_info['wc-time']}s WC-Time)")

    # Write the results to a CSV
    csv_path = portfolio_path / "result.csv"
    with csv_path.open("w") as out:
        writer = csv.writer(out)
        for instance_name in job_output_dict.keys():
            for solver_name in job_output_dict[instance_name].keys():
                job_o = job_output_dict[instance_name][solver_name]
                writer.writerow((instance_name, solver_name,
                                 job_o["status"], job_o["cpu-time"], job_o["wc-time"]))
