#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to communicate run statuses of various commands."""

from pathlib import Path
import fcntl

from Commands.sparkle_help import sparkle_file_help as sfh


def get_list_running_extractor_jobs():
    """Return a list of currently active feature extraction jobs."""
    list_running_extractor_jobs = []

    tmp_directory = "Tmp/SBATCH_Extractor_Jobs/"
    list_all_statusinfo_filename = sfh.get_list_all_statusinfo_filename(tmp_directory)
    for statusinfo_filename in list_all_statusinfo_filename:
        statusinfo_filepath = (
            tmp_directory + sfh.get_last_level_directory_name(statusinfo_filename))
        try:
            fin = Path(statusinfo_filepath).open("r+")
            fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
            mylist1 = fin.readline().strip().split()
            status_str = mylist1[1]
            if not status_str == "Running":
                fin.close()
                continue
            else:
                mylist2 = fin.readline().strip().split()
                extractor_name = mylist2[1]
                mylist3 = fin.readline().strip().split()
                instance_name = mylist3[1]
                mylist4 = fin.readline().strip().split()
                start_time_str = mylist4[2] + " " + mylist4[3]
                fin.readline()
                mylist5 = fin.readline().strip().split()
                cutoff_time_str = mylist5[2]
                fin.close()
                list_running_extractor_jobs.append([status_str, extractor_name,
                                                    instance_name, start_time_str,
                                                    cutoff_time_str])
        except OSError:
            continue

    return list_running_extractor_jobs


def print_running_extractor_jobs(verbose: bool = False):
    """Print whether currently a feature extraction job is active.

    Args:
        verbose: Indicating if output should be verbose
    """
    job_list = get_list_running_extractor_jobs()
    print("")
    print(
        f"Currently Sparkle has {str(len(job_list))} running feature computation jobs:")

    if verbose:
        current_job_num = 1

        for i in range(0, len(job_list)):
            status_str = job_list[i][0]
            instance_name = job_list[i][1]
            extractor_name = job_list[i][2]
            start_time_str = job_list[i][3]
            cutoff_time_str = job_list[i][4]
            print(f"[{str(current_job_num)}]: Extractor: {extractor_name}, Instance: "
                  f"{instance_name}, Start Time: {start_time_str}, Cutoff Time: "
                  f"{cutoff_time_str} second(s), Status: {status_str}")
            current_job_num += 1

    print("")
    return


def get_list_running_solver_jobs():
    """Return a list of currently active run solver job."""
    list_running_solver_jobs = []

    tmp_directory = "Tmp/SBATCH_Solver_Jobs/"
    list_all_statusinfo_filename = sfh.get_list_all_statusinfo_filename(tmp_directory)

    for statusinfo_filename in list_all_statusinfo_filename:
        statusinfo_filepath = (
            tmp_directory + sfh.get_last_level_directory_name(statusinfo_filename))
        fin = Path(statusinfo_filepath).open("r+")
        fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
        mylist1 = fin.readline().strip().split()
        status_str = mylist1[1]
        if not status_str == "Running":
            fin.close()
            continue
        else:
            mylist2 = fin.readline().strip().split()
            solver_name = mylist2[1]
            mylist3 = fin.readline().strip().split()
            instance_name = mylist3[1]
            mylist4 = fin.readline().strip().split()
            start_time_str = mylist4[2] + " " + mylist4[3]
            fin.readline()
            mylist5 = fin.readline().strip().split()
            cutoff_time_str = mylist5[2]
            fin.close()
            list_running_solver_jobs.append([status_str, solver_name, instance_name,
                                             start_time_str, cutoff_time_str])
    return list_running_solver_jobs


def print_running_solver_jobs(verbose: bool = False):
    """Print whether currently a run solvers job is active.

    Args:
        verbose: Indicating if output should be verbose
    """
    job_list = get_list_running_solver_jobs()
    print("")
    print(f"Currently Sparkle has {str(len(job_list))}"
          " running performance computation jobs:")

    if verbose:
        current_job_num = 1
        for i in range(0, len(job_list)):
            status_str = job_list[i][0]
            instance_name = job_list[i][1]
            solver_name = job_list[i][2]
            start_time_str = job_list[i][3]
            cutoff_time_str = job_list[i][4]
            print(f"[{str(current_job_num)}]: Solver: {solver_name}, Instance: "
                  f"{instance_name}, Start Time: {start_time_str}, Cutoff Time: "
                  f"{cutoff_time_str} second(s), Status: {status_str}")
            current_job_num += 1

    print("")
    return


def print_running_portfolio_selector_jobs():
    """Print whether currently a portfolio construction job is active."""
    print("")
    key_str = "construct_sparkle_portfolio_selector"
    task_run_status_path = "Tmp/SBATCH_Portfolio_Jobs/" + key_str + ".statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle portfolio selecotr is constructing ...")
    else:
        print("No currently running Sparkle portfolio selector construction job!")
    print("")
    return


def print_running_report_jobs():
    """Print whether currently a report generation job is active."""
    print("")
    key_str = "generate_report"
    task_run_status_path = "Tmp/SBATCH_Report_Jobs/" + key_str + ".statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle report is generating ...")
    else:
        print("No currently running Sparkle report generation job!")
    print("")
    return
