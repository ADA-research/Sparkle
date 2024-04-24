#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to run solvers."""
import os
import subprocess
import sys
import ast
import shutil
import fcntl
from pathlib import Path

from CLI.sparkle_help import sparkle_global_help as sgh
from sparkle.platform import file_help as sfh
from sparkle.sparkle_performance_dataframe import PerformanceDataFrame
from CLI.sparkle_help import sparkle_job_help as sjh
from sparkle.types.sparkle_objective import PerformanceMeasure
from sparkle.platform.settings_help import SolutionVerifier
from sparkle.solver import SAT_help as sssh

import functools
print = functools.partial(print, flush=True)


def get_solver_call_from_wrapper(solver_wrapper_path: str, instance_path: str,
                                 seed_str: str = None) -> str:
    """Return the command line call string retrieved from the solver wrapper."""
    if seed_str is None:
        seed_str = str(sgh.get_seed())

    cmd_solver_call = ""
    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    cmd_get_solver_call = (f'{solver_wrapper_path} --print-command "{instance_path}"'
                           f" --seed {seed_str} --cutoff-time {cutoff_time_str}")
    solver_call_rawresult = os.popen(cmd_get_solver_call)
    solver_call_result = solver_call_rawresult.readlines()[0].strip()

    if len(solver_call_result) > 0:
        cmd_solver_call = solver_call_result
    else:
        # TODO: Add instructions for the user that might fix the issue?
        print('ERROR: Failed to get valid solver call command from wrapper at "'
              f'{solver_wrapper_path}" stopping execution!')
        sys.exit(-1)

    return cmd_solver_call


def run_solver_on_instance(solver_path: str, solver_wrapper_path: str,
                           instance_path: str, raw_result_path: str,
                           runsolver_values_path: str, seed_str: str = None,
                           custom_cutoff: int = None) -> None:
    """Prepare for execution, run the solver on an instance, check output for errors."""
    if not Path(solver_wrapper_path).is_file():
        print(f'ERROR: Wrapper named "{solver_wrapper_path}" not found, stopping '
              "execution!")
        sys.exit(-1)

    # Get the solver call command from the wrapper
    cmd_solver_call = get_solver_call_from_wrapper(solver_wrapper_path, instance_path,
                                                   seed_str)

    run_solver_on_instance_with_cmd(Path(solver_path), cmd_solver_call,
                                    Path(raw_result_path),
                                    Path(runsolver_values_path), custom_cutoff)

    return


def run_solver_on_instance_with_cmd(solver_path: Path, cmd_solver_call: str,
                                    raw_result_path: Path, runsolver_values_path: Path,
                                    custom_cutoff: int = None,
                                    is_configured: bool = False) -> Path:
    """Run the solver on the given instance, with a given command line call."""
    if custom_cutoff is None:
        custom_cutoff = sgh.settings.get_general_target_cutoff_time()

    # For configured solvers change the directory to accommodate sparkle_smac_wrapper
    original_path = Path.cwd()
    exec_path = original_path

    rs_prefix = ""
    if is_configured:
        # Update paths to match configured solver dirs
        rs_prefix = "../../"
        exec_path = str(raw_result_path).replace(".rawres", "_exec_dir/")
        # Copy files
        shutil.copytree(solver_path, exec_path, dirs_exist_ok=True)
        # Executable is now in "current dir"
        solver_path = "."

    # Prepare runsolver call
    runsolver_path = rs_prefix + sgh.runsolver_path
    runsolver_values_log = f"{rs_prefix}{runsolver_values_path}"
    runsolver_watch_data_path = runsolver_values_log.replace("val", "log")
    raw_result_path_option = f"{rs_prefix}{raw_result_path}"
    cmd_solver_name, cmd_solver_args = cmd_solver_call.split(" ", 1)
    cmd = [runsolver_path, "--timestamp", "--use-pty",
           "--cpu-limit", str(custom_cutoff),
           "-w", runsolver_watch_data_path,
           "-v", runsolver_values_log,
           "-o", raw_result_path_option,
           f"{solver_path}/{cmd_solver_name}", cmd_solver_args]

    process = subprocess.run(cmd, cwd=exec_path, capture_output=True)
    if process.returncode != 0:
        print("WARNING: Solver execution seems to have failed!\n"
              f"The used command was: {cmd}")
    else:
        # Clean up on success
        if is_configured:
            tmp_raw_res = f"{exec_path}tmp/"
            tmp_paths = list(Path(tmp_raw_res).glob("*.rawres"))

            # The result should exist
            if len(tmp_paths) == 0:
                print(f"WARNING: Raw result not found in {tmp_raw_res}. Writing from "
                      "subprocess...")
                Path(raw_result_path).open("w").write(process.stdout.decode())

            if check_solver_output_for_errors(Path(raw_result_path)):
                sfh.rmfiles(runsolver_watch_data_path)

    return raw_result_path


def check_solver_output_for_errors(raw_result_path: Path) -> bool:
    """Check solver output for known errors.

    Args:
        raw_result_path: Path to the file to verify.
    """
    # Check if we can decode the output dictionary
    raw_output_str = raw_result_path.open("r").read()
    try:
        raw_output_dict_str =\
            raw_output_str[raw_output_str.find("{"), raw_output_str.find("}")]
        ast.literal_eval(raw_output_dict_str)
    except Exception as ex:
        print(f"WARNING: Possible error detected in {raw_result_path}. "
              f"Decoding the output dictionary threw exception: {ex}")
        return False
    return True


def run_solver_on_instance_and_process_results(
        solver_path: str, instance_path: str, seed_str: str = None,
        custom_cutoff: int = None) -> tuple[float, float, float, list[float], str, str]:
    """Prepare and run a given the solver and instance, and process output."""
    # Prepare paths
    # TODO: Fix result path for multi-file instances (only a single file is part of the
    # result path)
    raw_result_path = (f"{sgh.sparkle_tmp_path}"
                       f"{Path(solver_path).name}_"
                       f"{Path(instance_path).name}_"
                       f"{sgh.get_time_pid_random_string()}.rawres")
    runsolver_values_path = raw_result_path.replace(".rawres", ".val")
    solver_wrapper_path = Path(solver_path) / sgh.sparkle_run_default_wrapper

    # Run
    run_solver_on_instance(solver_path, solver_wrapper_path, instance_path,
                           raw_result_path, runsolver_values_path, seed_str,
                           custom_cutoff)

    # Process results
    cpu_time, wc_time, quality, status = process_results(
        raw_result_path, solver_wrapper_path, runsolver_values_path)
    cpu_time_penalised, status = handle_timeouts(cpu_time, status, custom_cutoff)
    status = verify(instance_path, raw_result_path, solver_path, status)

    return cpu_time, wc_time, cpu_time_penalised, quality, status, raw_result_path


def running_solvers(performance_data_csv_path: str, rerun: bool) -> None:
    """Run solvers on all instances.

    If rerun is True, rerun for instances with existing performance data.
    """
    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    perf_measure = sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    performance_data = PerformanceDataFrame(performance_data_csv_path)

    if rerun:
        list_performance_computation_job = (
            performance_data.get_list_recompute_performance_computation_job())
    else:
        list_performance_computation_job = (
            performance_data.get_list_remaining_performance_computation_job())

    print("The cutoff time per algorithm run to solve an instance is set to "
          f"{cutoff_time_str} seconds")

    total_job_num = sjh.get_num_of_total_job_from_list(list_performance_computation_job)
    current_job_num = 1
    print("The total number of jobs to run is: " + str(total_job_num))

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
                      f"{str(quality[0])}")
            else:
                performance_data.set_value(cpu_time_penalised, solver_path,
                                           instance_path)
                print(f"Running Result: Status {status}, Runtime{penalised_str}: "
                      f"{str(cpu_time_penalised)}")

            print(f"Executing Progress: {str(current_job_num)} out of "
                  f"{str(total_job_num)}")
            current_job_num += 1

    performance_data.save_csv()
    print(f"Performance data file {performance_data_csv_path} has been updated!")


def handle_timeouts(runtime: float, status: str,
                    custom_cutoff: int = None) -> tuple[float, str]:
    """Check if there is a timeout and return the status and penalised runtime."""
    if custom_cutoff is None:
        cutoff_time = sgh.settings.get_general_target_cutoff_time()
    else:
        cutoff_time = custom_cutoff

    if runtime > cutoff_time and status != "CRASHED":
        status = "TIMEOUT"  # Overwrites possible user status, unless it is 'CRASHED'
    if status == "TIMEOUT" or status == "UNKNOWN":
        runtime_penalised = sgh.settings.get_penalised_time(cutoff_time)
    else:
        runtime_penalised = runtime

    return runtime_penalised, status


def verify(instance_path: str, raw_result_path: str, solver_path: str, status: str)\
        -> str:
    """Run a solution verifier on the solution and update the status if needed."""
    verifier = sgh.settings.get_general_solution_verifier()

    # Use verifier if one is given and the solver did not time out
    if verifier == SolutionVerifier.SAT and status != "TIMEOUT" and status != "UNKNOWN":
        status = sssh.sat_verify(instance_path, raw_result_path, solver_path)

    return status


def process_results(
        raw_result_path: str, solver_wrapper_path: str,
        runsolver_values_path: str) -> tuple[float, float, list[float], str]:
    """Process results from raw output, the wrapper, and runsolver."""
    # By default runtime comes from runsolver, may be overwritten by user wrapper
    cpu_time, wc_time = get_runtime_from_runsolver(runsolver_values_path)

    # Get results from the wrapper
    cmd_get_results_from_wrapper = (
        f"{solver_wrapper_path} --print-output {raw_result_path}")
    results = os.popen(cmd_get_results_from_wrapper)
    result_lines = results.readlines()

    if len(result_lines) <= 0:
        # TODO: Add instructions for the user that might fix the issue?
        print(f'ERROR: Failed to get output from wrapper at "{solver_wrapper_path}" '
              "stopping execution!")
        sys.exit(-1)

    # Check if Sparkle should use it's own parser
    first_line = result_lines[0]
    first_line_parts = first_line.strip().split()

    if (len(first_line_parts) == 4 and first_line_parts[0].lower() == "use"
       and first_line_parts[1].lower() == "sparkle"):
        if first_line_parts[2].lower() == "sat":
            quality = []  # Not defined for SAT
            # TODO: Handle wc_time when user can choose which to use
            status = sssh.sparkle_sat_parser(raw_result_path, cpu_time)
        else:
            parser_list = "SAT"
            print(f'ERROR: Wrapper at "{solver_wrapper_path}" requested Sparkle to use '
                  "an internal parser that does not exist")
            print(f"Possible internal parsers: {parser_list}")
            print("If your problem domain is not in the list, please parse the output in"
                  " the wrapper.")
            print("Stopping execution!")
            sys.exit(-1)
    else:
        # Read output
        quality = []
        status = "UNKNOWN"
        for line in result_lines:
            parts = line.strip().split()
            # Skip empty lines
            if len(parts) <= 0:
                continue
            # Handle lines that are too short
            if len(parts) <= 1:
                print(f'Warning: The line "{line.strip()}" contains no result '
                      "information or is not formatted correctly: "
                      "<quality/status/runtime> VALUE")
            if parts[0].lower() == "quality":
                quality = get_quality_from_wrapper(parts)
            elif parts[0].lower() == "status":
                status = get_status_from_wrapper(parts[1])
            elif parts[0].lower() == "runtime":
                cpu_time = float(parts[1])
                wc_time = cpu_time
            # TODO: Handle unknown keywords?

    return cpu_time, wc_time, quality, status


# quality -- comma separated list of quality measurements; [required when one or more
# quality objectives are used, optional otherwise]
def get_quality_from_wrapper(result_list: list[str]) -> list[float]:
    """Return a list based on the quality performances returned from by the wrapper."""
    quality = []
    start_index = 1  # 0 is the keyword 'quality'

    for i in range(start_index, len(result_list)):
        quality.append(float(result_list[i]))

    return quality


# NOTE: This should be an ENUM, but its hard coded in many places of Sparkle
def get_status_from_wrapper(result: str) -> str:
    """Return the status reported by the wrapper as standardised str."""
    status_list = "<SUCCESS/TIMEOUT/CRASHED/SAT/UNSAT/WRONG/UNKNOWN>"
    status = "SUCCESS"

    if result.upper() == "SUCCESS":
        status = "SUCCESS"
    elif result.upper() == "TIMEOUT":
        status = "TIMEOUT"
    elif result.upper() == "CRASHED":
        status = "CRASHED"
    elif result.upper() == "SAT":
        status = "SAT"
    elif result.upper() == "UNSAT":
        status = "UNSAT"
    elif result.upper() == "WRONG":
        status = "WRONG"
    elif result.upper() == "UNKNOWN":
        status = "UNKNOWN"
    else:
        print(f'ERROR: Invalid status "{result}" given, possible statuses are: '
              f"{status_list}\nStopping execution!")
        sys.exit(-1)

    return status


# NOTE: This method is actually usefull, but not coded very neatly
def get_runtime_from_runsolver(runsolver_values_path: str) -> tuple[float, float]:
    """Return the CPU and wallclock time reported by runsolver."""
    cpu_time = -1.0
    wc_time = -1.0
    if Path(runsolver_values_path).exists():
        with Path(runsolver_values_path).open("r+") as infile:
            fcntl.flock(infile.fileno(), fcntl.LOCK_EX)
            lines = [line.strip().split("=") for line in infile.readlines()
                     if len(line.split("=")) == 2]
            for keyword, value in lines:
                if keyword == "WCTIME":
                    wc_time = float(value)
                elif keyword == "CPUTIME":
                    cpu_time = float(value)
                    # Order is fixed, CPU is the last thing we want to read, so break
                    break
    return cpu_time, wc_time


def remove_faulty_solver(solver_path: str, instance_path: str) -> None:
    """Remove a faulty solver from Sparkle.

    Input: Path to solver, path to instance it failed on
    """
    solver_name = Path(solver_path).name
    instance_name = Path(instance_path).name
    print(f"Warning: Solver {solver_name} reports the wrong answer "
          f"on instance {instance_name}!\n"
          f"Warning: Solver {solver_name} will be removed!")

    # TODO: Fix solver removal from performanc data CSV file
    # performance_data_csv.remove_solver(solver_path)
    sfh.add_remove_platform_item(solver_path,
                                 sgh.solver_list_path,
                                 remove=True)
    sfh.add_remove_platform_item(None,
                                 sgh.solver_nickname_list_path,
                                 key=solver_path,
                                 remove=True)

    print(f"Solver {solver_name} is a wrong solver")
    print(f"Solver {solver_name} running on instance {instance_name} ignored!")


def update_performance_data_id() -> None:
    """Update the performance data ID."""
    # Get next pd_id
    pd_id = get_performance_data_id() + 1
    # Write new pd_id
    pd_id_path = sgh.performance_data_id_path
    with Path(pd_id_path).open("w") as pd_id_file:
        pd_id_file.write(str(pd_id))

    return


def get_performance_data_id() -> int:
    """Return the current performance data ID."""
    pd_id = 0
    if Path(sgh.performance_data_id_path).exists():
        pd_id = int(Path(sgh.performance_data_id_path).open("r").readline())
    return pd_id
