#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""

import os
import shutil
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
    if sgh.instance_dir.exists():
        return True
    if sgh.output_dir.exists():
        return True
    if sgh.solver_dir.exists():
        return True
    if sgh.extractor_dir.exists():
        return True
    if sgh.feature_data_dir.exists():
        return True
    if sgh.performance_data_dir.exists():
        return True
    if sgh.reference_list_dir.exists():
        return True
    if sgh.sparkle_portfolio_selector_dir.exists():
        return True
    if sgh.sparkle_parallel_portfolio_dir.exists():
        return True

    return False


def save_current_sparkle_platform() -> None:
    """Store the current Sparkle platform in a .zip file."""
    suffix = sbh.get_time_pid_random_string()
    snapshot_filename = f"{sgh.snapshot_dir}/My_Snapshot_{suffix}.zip"

    flag_instances = False
    flag_solvers = False
    flag_extractors = False
    flag_feature_data = False
    flag_performance_data = False
    flag_reference_lists = False
    flag_sparkle_portfolio_selector = False
    flag_sparkle_parallel_portfolio = False

    flag_test_data = False
    flag_output_data = False

    if sgh.test_data_dir.exists():
        flag_test_data = True
    if sgh.output_dir.exists():
        flag_output_data = True
    if sgh.instance_dir.exists():
        flag_instances = True
    if sgh.solver_dir.exists():
        flag_solvers = True
    if sgh.extractor_dir.exists():
        flag_extractors = True
    if sgh.feature_data_dir.exists():
        flag_feature_data = True
    if sgh.performance_data_dir.exists():
        flag_performance_data = True
    if sgh.reference_list_dir.exists():
        flag_reference_lists = True
    if sgh.sparkle_portfolio_selector_dir.exists():
        flag_sparkle_portfolio_selector = True
    if sgh.sparkle_parallel_portfolio_dir.exists():
        flag_sparkle_parallel_portfolio = True

    if not Path(sgh.sparkle_tmp_path).exists():
        Path(sgh.sparkle_tmp_path).mkdir()

    snapshot_filename_exist = Path(snapshot_filename).exists()

    if not snapshot_filename_exist:
        if flag_test_data:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Test_Data/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_test_data:
            os.system(f"zip -g -r {snapshot_filename} Test_Data/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_output_data:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Output/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_output_data:
            os.system(f"zip -g -r {snapshot_filename} Output/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_instances:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Instances/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_instances:
            os.system(f"zip -g -r {snapshot_filename} Instances/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_solvers:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Solvers/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_solvers:
            os.system(f"zip -g -r {snapshot_filename} Solvers/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_extractors:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Extractors/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_extractors:
            os.system(f"zip -g -r {snapshot_filename} Extractors/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_feature_data:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Feature_Data/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_feature_data:
            os.system(f"zip -g -r {snapshot_filename} Feature_Data/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_performance_data:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Performance_Data/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_performance_data:
            os.system(f"zip -g -r {snapshot_filename} Performance_Data/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_reference_lists:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Reference_Lists/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_reference_lists:
            os.system(f"zip -g -r {snapshot_filename} Reference_Lists/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_sparkle_portfolio_selector:
            snapshot_filename_exist = True
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(f"zip -r {snapshot_filename} Sparkle_Portfolio_Selector/ >> "
                      f"{snapshot_log_file_path}")
    else:
        if flag_sparkle_portfolio_selector:
            os.system(f"zip -g -r {snapshot_filename} Sparkle_Portfolio_Selector/ >> "
                      f"{snapshot_log_file_path}")

    if not snapshot_filename_exist:
        if flag_sparkle_parallel_portfolio:
            print("Now recording current Sparkle platform in file "
                  f"{snapshot_filename} ...")
            os.system(
                f"zip -r {snapshot_filename} "
                f"{sgh.sparkle_parallel_portfolio_dir}/ >> {snapshot_log_file_path}")
    else:
        if flag_sparkle_parallel_portfolio:
            os.system(
                f"zip -g -r {snapshot_filename} "
                f"{sgh.sparkle_parallel_portfolio_dir}/ >> {snapshot_log_file_path}")

    print(f"Snapshot file {snapshot_filename} saved successfully!")
    os.system("rm -f " + snapshot_log_file_path)


def remove_current_sparkle_platform() -> None:
    """Remove the current Sparkle platform."""
    sfh.remove_temporary_files()
    shutil.rmtree(sgh.output_dir, ignore_errors=True)
    shutil.rmtree(sgh.instance_dir, ignore_errors=True)
    shutil.rmtree(sgh.solver_dir, ignore_errors=True)
    shutil.rmtree(sgh.test_data_dir, ignore_errors=True)
    shutil.rmtree(sgh.extractor_dir, ignore_errors=True)
    shutil.rmtree(sgh.reference_list_dir, ignore_errors=True)
    shutil.rmtree(sgh.sparkle_portfolio_selector_dir, ignore_errors=True)
    shutil.rmtree(sgh.sparkle_parallel_portfolio_dir, ignore_errors=True)
    ablation_scenario_dir = f"{sgh.ablation_dir}scenarios/"
    shutil.rmtree(Path(ablation_scenario_dir), ignore_errors=True)


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
    remove_current_sparkle_platform()
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
