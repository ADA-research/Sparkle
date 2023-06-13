#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""

import os
import sys
from pathlib import Path

from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh

snapshot_log_file_path = sgh.sparkle_err_path


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


def save_current_sparkle_platform() -> None:
    """Store the current Sparkle platform in a .zip file."""
    my_suffix = sbh.get_time_pid_random_string()
    my_snapshot_filename = f"{sgh.snapshot_dir}/My_Snapshot_{my_suffix}.zip"

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

    my_snapshot_filename_exist = Path(my_snapshot_filename).exists()
    if not my_snapshot_filename_exist:
        if my_flag_instances:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Instances/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_instances:
            os.system(f"zip -g -r {my_snapshot_filename} Instances/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_solvers:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Solvers/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_solvers:
            os.system(f"zip -g -r {my_snapshot_filename} Solvers/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_extractors:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Extractors/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_extractors:
            os.system(f"zip -g -r {my_snapshot_filename} Extractors/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_feature_data:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Feature_Data/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_feature_data:
            os.system(f"zip -g -r {my_snapshot_filename} Feature_Data/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_performance_data:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Performance_Data/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_performance_data:
            os.system(f"zip -g -r {my_snapshot_filename} Performance_Data/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_reference_lists:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Reference_Lists/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_reference_lists:
            os.system(f"zip -g -r {my_snapshot_filename} Reference_Lists/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_sparkle_portfolio_selector:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(f"zip -r {my_snapshot_filename} Sparkle_Portfolio_Selector/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if my_flag_sparkle_portfolio_selector:
            os.system(f"zip -g -r {my_snapshot_filename} Sparkle_Portfolio_Selector/ >> "
                      f"{snapshot_log_file_path}")

    if not my_snapshot_filename_exist:
        if my_flag_sparkle_parallel_portfolio:
            my_snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{my_snapshot_filename} ...")
            os.system(
                f"zip -r {my_snapshot_filename} "
                f"{sgh.sparkle_parallel_portfolio_dir}/ >> {snapshot_log_file_path}")
    else:
        if my_flag_sparkle_parallel_portfolio:
            os.system(
                f"zip -g -r {my_snapshot_filename} "
                f"{sgh.sparkle_parallel_portfolio_dir}/ >> {snapshot_log_file_path}")

    print(f"Snapshot file {my_snapshot_filename} saved successfully!")
    os.system("rm -f " + snapshot_log_file_path)


def cleanup_current_sparkle_platform() -> None:
    """Remove the current Sparkle platform."""
    if Path("Instances/").exists():
        sfh.rmtree(Path("Instances/"))
    if Path("Solvers/").exists():
        sfh.rmtree(Path("Solvers/"))
    if Path("Extractors/").exists():
        sfh.rmtree(Path("Extractors/"))
    if Path("Feature_Data/").exists():
        sfh.rmtree(Path("Feature_Data/"))
    if Path("Performance_Data/").exists():
        sfh.rmtree(Path("Performance_Data/"))
    if Path("Reference_Lists/").exists():
        sfh.rmtree(Path("Reference_Lists/"))
    if Path("Sparkle_Portfolio_Selector").exists():
        sfh.rmtree(Path("Sparkle_Portfolio_Selector/"))
    if sgh.sparkle_parallel_portfolio_dir.exists():
        sfh.rmtree(sgh.sparkle_parallel_portfolio_dir)
    ablation_scenario_dir = f"{sgh.ablation_dir}scenarios/"
    if Path(ablation_scenario_dir).exists():
        sfh.rmtree(Path(ablation_scenario_dir))


def extract_sparkle_snapshot(my_snapshot_filename: str) -> None:
    """Restore a Sparkle platform from a snapshot.

    Args:
      my_snapshot_filename: File path to the file where the current Sparkle
        platform should be stored.
    """
    if not Path(my_snapshot_filename).exists():
        sys.exit()

    if not my_snapshot_filename.endswith(".zip"):
        print(f"File {my_snapshot_filename} is not a .zip file!")
        sys.exit()

    my_suffix = sbh.get_time_pid_random_string()
    my_tmp_directory = f"tmp_directory_{my_suffix}"

    if not Path(sgh.sparkle_tmp_path).exists():
        Path(sgh.sparkle_tmp_path).mkdir()

    os.system(f"unzip -o {my_snapshot_filename} -d {my_tmp_directory} >> "
              f"{snapshot_log_file_path}")
    os.system(r"cp -r " + my_tmp_directory + "/* " + "./")
    sfh.rmtree(Path(my_tmp_directory))
    os.system(r"rm -f " + snapshot_log_file_path)


def load_snapshot(snapshot_file_path: str) -> None:
    """Load a Sparkle platform from a snapshot.

    Args:
        snapshot_file_path: File path to the file where the Sparkle
            platform is stored.
    """
    if not Path(snapshot_file_path).exists():
        print(f"Snapshot file {snapshot_file_path} does not exist!")
        sys.exit()
    if not snapshot_file_path.endswith(".zip"):
        print(f"File {snapshot_file_path} is not a .zip file!")
        sys.exit()
    print("Cleaning existing Sparkle platform ...")
    cleanup_current_sparkle_platform()
    print("Existing Sparkle platform cleaned!")

    print(f"Loading snapshot file {snapshot_file_path} ...")
    extract_sparkle_snapshot(snapshot_file_path)
    print(f"Snapshot file {snapshot_file_path} loaded successfully!")


def remove_snapshot(snapshot_file_path: str) -> None:
    """Remove a snapshot from a Sparkle platform.

    Args:
        snapshot_file_path: File path to the file where the Sparkle
            platform is stored.
    """
    if not Path(snapshot_file_path).exists():
        print(f"Snapshot file {snapshot_file_path} does not exist!")
        sys.exit()

    print(f"Removing snapshot file {snapshot_file_path} ...")
    command_line = f"rm -rf {snapshot_file_path}"
    os.system(command_line)
    print(f"Snapshot file {snapshot_file_path} removed!")
