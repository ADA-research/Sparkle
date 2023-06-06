#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""

import os
import sys
import shutil
from pathlib import Path

from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh


global record_log_file_path
record_log_file_path = sgh.sparkle_err_path


def detect_current_sparkle_platform_exists() -> bool:
    """Return whether a Sparkle platform is currently active.

    Returns:
      Boolean value indicating whether a Sparkle platform is active or not.
    """
    if Path("Instances/").exists():
        return True
    if Path("Solvers/").exists():
        return True
    if Path("Extractors/").exists():
        return True
    if Path("Feature_Data/").exists():
        return True
    if Path("Performance_Data/").exists():
        return True
    if Path("Reference_Lists/").exists():
        return True
    if Path("Sparkle_Portfolio_Selector/").exists():
        return True
    if sgh.sparkle_parallel_portfolio_dir.exists():
        return True

    return False


def save_current_sparkle_platform(my_record_filename: str) -> None:
    """Store the current Sparkle platform in a .zip file.

    Args:
      my_record_filename: File path to the file where the current Sparkle
        platform should be stored.
    """
    my_flag_instances = False
    my_flag_solvers = False
    my_flag_extractors = False
    my_flag_feature_data = False
    my_flag_performance_data = False
    my_flag_reference_lists = False
    my_flag_sparkle_portfolio_selector = False
    my_flag_sparkle_parallel_portfolio = False

    if Path("Instances/").exists():
        my_flag_instances = True
    if Path("Solvers/").exists():
        my_flag_solvers = True
    if Path("Extractors/").exists():
        my_flag_extractors = True
    if Path("Feature_Data/").exists():
        my_flag_feature_data = True
    if Path("Performance_Data/").exists():
        my_flag_performance_data = True
    if Path("Reference_Lists/").exists():
        my_flag_reference_lists = True
    if Path("Sparkle_Portfolio_Selector/").exists():
        my_flag_sparkle_portfolio_selector = True
    if sgh.sparkle_parallel_portfolio_dir.exists():
        my_flag_sparkle_parallel_portfolio = True

    if not Path(sgh.sparkle_tmp_path).exists():
        Path(sgh.sparkle_tmp_path).mkdir()

    my_record_filename_exist = Path(my_record_filename).exists()
    if not my_record_filename_exist:
        if my_flag_instances:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Instances/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_instances:
            os.system(f"zip -g -r {my_record_filename} Instances/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_solvers:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Solvers/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_solvers:
            os.system(f"zip -g -r {my_record_filename} Solvers/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_extractors:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Extractors/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_extractors:
            os.system(f"zip -g -r {my_record_filename} Extractors/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_feature_data:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Feature_Data/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_feature_data:
            os.system(f"zip -g -r {my_record_filename} Feature_Data/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_performance_data:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Performance_Data/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_performance_data:
            os.system(f"zip -g -r {my_record_filename} Performance_Data/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_reference_lists:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Reference_Lists/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_reference_lists:
            os.system(f"zip -g -r {my_record_filename} Reference_Lists/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_sparkle_portfolio_selector:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(f"zip -r {my_record_filename} Sparkle_Portfolio_Selector/ >> "
                      f"{record_log_file_path}")
    else:
        if my_flag_sparkle_portfolio_selector:
            os.system(f"zip -g -r {my_record_filename} Sparkle_Portfolio_Selector/ >> "
                      f"{record_log_file_path}")

    if not my_record_filename_exist:
        if my_flag_sparkle_parallel_portfolio:
            my_record_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_record_filename} ...")
            os.system(
                f"zip -r {my_record_filename} "
                f"{sgh.sparkle_parallel_portfolio_dir}/ >> {record_log_file_path}")
    else:
        if my_flag_sparkle_parallel_portfolio:
            os.system(
                f"zip -g -r {my_record_filename} "
                f"{sgh.sparkle_parallel_portfolio_dir}/ >> {record_log_file_path}")

    os.system("rm -f " + record_log_file_path)


def remove_current_sparkle_platform() -> None:
    """Remove the current Sparkle platform."""
    if Path("Instances/").exists():
        shutil.rmtree(Path("Instances/"), ignore_errors=True)
    if Path("Solvers/").exists():
        shutil.rmtree(Path("Solvers/"), ignore_errors=True)
    if Path("Extractors/").exists():
        shutil.rmtree(Path("Extractors/"), ignore_errors=True)
    if Path("Feature_Data/").exists():
        shutil.rmtree(Path("Feature_Data/"), ignore_errors=True)
    if Path("Performance_Data/").exists():
        shutil.rmtree(Path("Performance_Data/"), ignore_errors=True)
    if Path("Reference_Lists/").exists():
        shutil.rmtree(Path("Reference_Lists/"), ignore_errors=True)
    if Path("Sparkle_Portfolio_Selector").exists():
        shutil.rmtree(Path("Sparkle_Portfolio_Selector/"), ignore_errors=True)
    if sgh.sparkle_parallel_portfolio_dir.exists():
        shutil.rmtree(sgh.sparkle_parallel_portfolio_dir, ignore_errors=True)
    ablation_scenario_dir = f"{sgh.ablation_dir}scenarios/"
    if Path(ablation_scenario_dir).exists():
        shutil.rmtree(Path(ablation_scenario_dir), ignore_errors=True)


def extract_sparkle_record(my_record_filename: str) -> None:
    """Restore a Sparkle platform from a record.

    Args:
      my_record_filename: File path to the file where the current Sparkle
        platform should be stored.
    """
    if not Path(my_record_filename).exists():
        sys.exit()

    my_suffix = sbh.get_time_pid_random_string()
    my_tmp_directory = f"tmp_directory_{my_suffix}"

    if not Path(sgh.sparkle_tmp_path).exists():
        Path(sgh.sparkle_tmp_path).mkdir()

    os.system(f"unzip -o {my_record_filename} -d {my_tmp_directory} >> "
              f"{record_log_file_path}")
    os.system(r"cp -r " + my_tmp_directory + "/* " + "./")
    sfh.rmtree(Path(my_tmp_directory))
    os.system(r"rm -f " + record_log_file_path)
