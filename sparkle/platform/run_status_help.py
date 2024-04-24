#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to communicate run statuses of various commands."""
from pathlib import Path

import global_variables as sgh
from CLI.support import sparkle_job_help as sjh
from sparkle.platform import file_help as sfh
from CLI.help.status_info import (SolverRunStatusInfo,
                                  StatusInfoType,
                                  ConfigureSolverStatusInfo,
                                  ConstructParallelPortfolioStatusInfo,
                                  ConstructPortfolioSelectorStatusInfo,
                                  GenerateReportStatusInfo)
from CLI.help.command_help import CommandName


def get_jobs_for_command(jobs: list[dict[str, str, str]], command: CommandName) \
        -> list[dict[str, str, str]]:
    """Filter jobs by a command.

    Args:
      jobs: List of jobs
      command: The command to filter for

    Returns:
      Jobs that belong to the given command.
    """
    return [x for x in jobs if x["command"].split("-")[0].lower() == command.lower()]


def get_running_jobs_for_command(command: CommandName) -> str:
    """Print all the running jobs.

    Args:
        command: name of the command to search for.

    Returns:
        string with job ids.
    """
    jobs = sjh.get_active_jobs()

    command_jobs = get_jobs_for_command(jobs, command.name)
    command_jobs_ids = " ".join([x["job_id"] for x in command_jobs])

    return command_jobs_ids


def print_running_solver_jobs() -> None:
    """Print a list of currently active run solver job."""
    command = CommandName.RUN_SOLVERS
    command_jobs_ids = get_running_jobs_for_command(command)
    tmp_directory = f"{sgh.sparkle_tmp_path}/{StatusInfoType.SOLVER_RUN}/"
    statusinfo_files = sfh.get_list_all_extensions(Path(tmp_directory), ".statusinfo")
    if len(command_jobs_ids) > 0:
        print(f"The command {command} is running "
              f"with job IDs {command_jobs_ids}")
        if len(statusinfo_files) > 0:
            print("Running solver jobs:")
            for statusinfo_filename in statusinfo_files:
                statusinfo_filepath = Path(
                    tmp_directory
                    + Path(statusinfo_filename).name)
                status_info = SolverRunStatusInfo.from_file(statusinfo_filepath)
                print(f"Start Time: {status_info.get_start_time()}")
                print(f"Solver: {status_info.get_solver()}")
                print(f"Instance: {status_info.get_instance()}")
                print()
    else:
        print("No running solver jobs")


def print_running_configuration_jobs() -> None:
    """Print a list of currently active run solver job."""
    command = CommandName.CONFIGURE_SOLVER
    command_jobs_ids = get_running_jobs_for_command(command)
    tmp_directory = f"{sgh.sparkle_tmp_path}/{StatusInfoType.CONFIGURE_SOLVER}/"
    statusinfo_files = sfh.get_list_all_extensions(Path(tmp_directory), ".statusinfo")
    if len(command_jobs_ids) > 0:
        print(f"The command {command} is running "
              f"with job IDs {command_jobs_ids}")
        if len(statusinfo_files) > 0:
            print("Running configuration jobs:")
            for statusinfo_filename in statusinfo_files:
                statusinfo_filepath = Path(
                    tmp_directory + Path(statusinfo_filename).parent)
                status_info = ConfigureSolverStatusInfo.from_file(statusinfo_filepath)
                print(f"Start Time: {status_info.get_start_time()}")
                print(f"Solver: {status_info.get_solver()}")
                print(f"Instance set test: {status_info.get_instance_set_test()}")
                print(f"Instance set train: {status_info.get_instance_set_train()}")
                print()
    else:
        print("No running configuration jobs")


def print_running_parallel_portfolio_construction_jobs() -> None:
    """Print a list of currently active pap construction jobs."""
    command = CommandName.CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO
    command_jobs_ids = get_running_jobs_for_command(command)
    tmp_directory = (f"{sgh.sparkle_tmp_path}/"
                     f"{StatusInfoType.CONSTRUCT_PARALLEL_PORTFOLIO}/")
    statusinfo_files = sfh.get_list_all_extensions(Path(tmp_directory), ".statusinfo")
    if len(command_jobs_ids) > 0:
        print(f"The command {command} is running "
              f"with job IDs {command_jobs_ids}")
        if len(statusinfo_files) > 0:
            print("Running parallel portfolio construction jobs:")
            for statusinfo_filename in statusinfo_files:
                statusinfo_filepath = Path(
                    tmp_directory
                    + Path(statusinfo_filename).parent)
                status_info = (ConstructParallelPortfolioStatusInfo
                               .from_file(statusinfo_filepath))
                print(f"Start Time: {status_info.get_start_time()}")
                print(f"Portfolio Name: {status_info.get_portfolio_name()}")
                print(f"Solver List: {str(status_info.get_list_of_solvers())}")
                print()
    else:
        print("No running parallel portfolio construction jobs")


def print_running_portfolio_selector_construction_jobs() -> None:
    """Print a list of currently active ps construction jobs."""
    command = CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR
    command_jobs_ids = get_running_jobs_for_command(command)
    tmp_directory = (f"{sgh.sparkle_tmp_path}/"
                     f"{StatusInfoType.CONSTRUCT_PORTFOLIO_SELECTOR}/")
    statusinfo_files = sfh.get_list_all_extensions(Path(tmp_directory), ".statusinfo")
    if len(command_jobs_ids) > 0:
        print(f"The command {command} is running "
              f"with job IDs {command_jobs_ids}")
        if len(statusinfo_files) > 0:
            print("Running portfolio selector construction jobs:")
            for statusinfo_filename in statusinfo_files:
                statusinfo_filepath = Path(
                    tmp_directory
                    + Path(statusinfo_filename).parent)
                status_info = (ConstructPortfolioSelectorStatusInfo
                               .from_file(statusinfo_filepath))
                print(f"Start Time: {status_info.get_start_time()}")
                print(f"Algorithm Selector: {status_info.get_algorithm_selector_path()}")
                print(f"Feature data csv: "
                      f"{str(status_info.get_feature_data_csv_path())}")
                print(f"Performance data csv: "
                      f"{str(status_info.get_performance_data_csv_path())}")
                print()
    else:
        print("No running portfolio selector construction jobs")


def print_running_generate_report_jobs() -> None:
    """Print a list of currently active generate report jobs."""
    tmp_directory = (f"{sgh.sparkle_tmp_path}/"
                     f"{StatusInfoType.GENERATE_REPORT}/")
    statusinfo_files = sfh.get_list_all_extensions(Path(tmp_directory), ".statusinfo")
    if len(statusinfo_files) > 0:
        print("Running generate report jobs:")
        for statusinfo_filename in statusinfo_files:
            statusinfo_filepath = Path(
                tmp_directory
                + Path(statusinfo_filename).parent)
            status_info = (GenerateReportStatusInfo
                           .from_file(statusinfo_filepath))
            print(f"Start Time: {status_info.get_start_time()}")
            print(f"Report Type: {status_info.get_report_type()}")
            print()
    else:
        print("No running generate report jobs")
