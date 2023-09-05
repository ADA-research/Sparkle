#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to communicate run statuses of various commands."""

import os
import time
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_job_help as sjh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_command_help as sch
from Commands.Structures.status_info import SolverRunStatusInfo, StatusInfoType


def get_jobs_for_command(jobs: list[dict[str, str, str]], command: str) \
        -> list[dict[str, str, str]]:
    """Filter jobs by a command.

    Args:
      jobs: List of jobs
      command: The command to filter for

    Returns:
      Jobs that belong to the given command.
    """
    return [x for x in jobs if x["command"] == command]


def print_running_jobs() -> None:
    """Print all the running jobs."""
    sjh.cleanup_active_jobs()
    jobs = sjh.read_active_jobs()
    commands = list(set([x["command"] for x in jobs]))
    for command in commands:
        command_jobs = get_jobs_for_command(jobs, command)
        command_jobs_ids = " ".join([x["job_id"] for x in command_jobs])

        if len(command_jobs) > 1:
            print(f"The command {command} is running "
                  f"with job IDs {command_jobs_ids}")
        else:
            print(f"The command {command} is running "
                  f"with job ID {command_jobs_ids}")


def print_running_solver_jobs() -> None:
    """Return a list of currently active run solver job."""
    tmp_directory = f"{sgh.sparkle_tmp_path}/{StatusInfoType.SOLVER_RUN}/"
    list_all_statusinfo_filename = sfh.get_list_all_statusinfo_filename(tmp_directory)
    print("Running Solver Jobs:")
    for statusinfo_filename in list_all_statusinfo_filename:
        statusinfo_filepath = Path(
            tmp_directory + sfh.get_last_level_directory_name(statusinfo_filename))
        status_info = SolverRunStatusInfo.from_file(statusinfo_filepath)
        print(status_info.get_solver())
        print(status_info.get_instance())
        print(status_info.get_status())
        print(status_info.get_start_time())
        print()


def print_algorithm_selector_info() -> None:
    """Print information about the Sparkle algorithm selector."""
    sparkle_algorithm_selector_path = sgh.sparkle_algorithm_selector_path
    print("")
    print("Status of algorithm selector in Sparkle:")

    key_str = "construct_sparkle_algorithm_selector"
    task_run_status_path = f"Tmp/{sgh.algorithm_selector_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle algorithm selector is constructing ...")
    elif Path(sparkle_algorithm_selector_path).is_file():
        print(f"Path: {sparkle_algorithm_selector_path}")
        print("Last modified time: "
              f"{get_file_modify_time(sparkle_algorithm_selector_path)}")
    else:
        print("No algorithm selector exists!")
    print("")
    return


def print_parallel_portfolio_info() -> None:
    """Print information about the Sparkle parallel portfolio."""
    sparkle_parallel_portfolio_path = sgh.sparkle_parallel_portfolio_path
    print("")
    print("Status of parallel portfolio in Sparkle:")

    key_str = "construct_sparkle_parallel_portfolio"
    task_run_status_path = f"Tmp/{sgh.pap_sbatch_tmp_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle parallel portfolio is constructing ...")
    elif Path(sparkle_parallel_portfolio_path).is_file():
        print(f"Path: {sparkle_parallel_portfolio_path}")
        print("Last modified time: "
              f"{get_file_modify_time(sparkle_parallel_portfolio_path)}")
    else:
        print("No parallel portfolio exists!")
    print("")
    return


def print_algorithm_configuration_info() -> None:
    """Print information about the Sparkle algorithm configuration."""
    print("")
    print("Status of algorithm configuration in Sparkle:")

    key_str = "algorithm_configuration"
    task_run_status_path = f"Tmp/{sgh.configuration_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle configurator is constructing ...")
    elif sgh.latest_scenario is not None:
        solver = sgh.latest_scenario.get_config_solver()
        instance_set_train = sgh.latest_scenario.get_config_instance_set_train()
        last_configuration_file_path = Path(
            sgh.smac_dir,
            "example_scenarios",
            f"{solver.name}_{instance_set_train.name}",
            sgh.sparkle_last_configuration_file_name
        )
        if last_configuration_file_path.is_file():
            print(f"Path: {last_configuration_file_path}")
            print("Last modified time: "
                  f"{get_file_modify_time(last_configuration_file_path)}")
    else:
        print("No configurator exists!")
    print("")


def print_algorithm_selection_report_info() -> None:
    """Print the current status of a Sparkle algorithm selection report."""
    sparkle_report_path = Path("Components/Sparkle-latex-generator/Sparkle_Report.pdf")
    print("")
    print("Status of algorithm selection report in Sparkle:")

    key_str = f"generate_report_{sgh.ReportType.ALGORITHM_SELECTION}"
    task_run_status_path = f"Tmp/{sgh.report_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle algorithm selection report is generating ...")
    elif Path(sparkle_report_path).is_file():
        print(f"Path :{sparkle_report_path}")
        print(f"Last modified time: {get_file_modify_time(sparkle_report_path)}")
    else:
        print("No algorithm selection report exists!")
    print("")
    return


def print_algorithm_configuration_report_info() -> None:
    """Print the current status of the Sparkle algorithm configuration report."""
    sparkle_report_base_path = Path("Configuration_Reports")
    report_file_name = \
        "Sparkle-latex-generator-for-configuration/Sparkle_Report_for_Configuration.pdf"
    print("")
    print("Status of algorithm configuration report in Sparkle:")

    key_str = f"generate_report_{sgh.ReportType.ALGORITHM_CONFIGURATION}"
    task_run_status_path = f"Tmp/{sgh.report_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle algorithm configuration report is generating ...")
    elif sparkle_report_base_path.is_dir():
        for folder in [x for x in sparkle_report_base_path.iterdir() if x.is_dir()]:
            act_path = (folder / report_file_name)
            if act_path.is_file():
                print(f"Path: {str(act_path)}")
                print(f"Last modified time: {get_file_modify_time(act_path)}")
                print("")
    else:
        print("No algorthm configuration report exists!")
    print("")
    return


def print_parallel_portfolio_report_info() -> None:
    """Print the current status of a Sparkle parallel portfolio report."""
    sparkle_report_path = Path("Components/Sparkle-latex-generator"
                               + "-for-parallel-portfolio/template-Sparkle.pdf")
    print("")
    print("Status of parallel portfolio report in Sparkle:")

    key_str = f"generate_report_{sgh.ReportType.ALGORITHM_SELECTION}"
    task_run_status_path = f"Tmp/{sgh.report_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle parallel portfolio report is generating ...")
    elif Path(sparkle_report_path).is_file():
        print(f"Path: {sparkle_report_path}")
        print(f"Last modified time: {get_file_modify_time(sparkle_report_path)}")
    else:
        print("No parallel portfolio report exists!")
    print("")
    return


def timestamp_to_time(timestamp: float) -> str:
    """Return a timestamp as a readable str."""
    time_struct = time.gmtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_struct)


def get_file_modify_time(file_path: str) -> str:
    """Return the last time a file was modified."""
    timestamp = os.path.getmtime(file_path)
    return timestamp_to_time(timestamp) + " (UTC+0)"


def generate_task_run_status(command_name: sch.CommandName, job_path: Path) -> None:
    """Generate run status info files for Slurm batch jobs.

    Args:
        command_name: enum name of the executed command
        job_path: path to the commands job folder
    """
    task_run_status_path = Path(f"{job_path}/{command_name}.statusinfo")
    status_info_str = "Status: Running\n"
    sfh.write_string_to_file(task_run_status_path, status_info_str)

    return


def delete_task_run_status(command_name: sch.CommandName, job_path: Path) -> None:
    """Remove run status info files for Slurm batch jobs.

    Args:
        command_name: enum name of the executed command
        job_path: path to the commands job folder
    """
    task_run_status_path = Path(f"{job_path}/{command_name}.statusinfo")
    task_run_status_path.unlink()

    return
