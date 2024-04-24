#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""
import shutil
import sys
from pathlib import Path
import zipfile

import global_variables as sgh
from sparkle.platform import file_help as sfh

snapshot_log_file_path = sgh.sparkle_err_path


def detect_current_sparkle_platform_exists(check_all_dirs: bool) -> bool:
    """Return whether a Sparkle platform is currently active.

    Args:
        check_all_dirs: variable indicating, if all the directories for a sparkle
            platform should be checked or if just finding one directory is fine
    Returns:
      Boolean value indicating whether a Sparkle platform is active or not.
    """
    if check_all_dirs:
        return all([x.exists() for x in sgh.working_dirs])
    else:
        return any([x.exists() for x in sgh.working_dirs])


def save_current_sparkle_platform() -> None:
    """Store the current Sparkle platform in a .zip file."""
    suffix = sgh.get_time_pid_random_string()
    snapshot_filename = f"{sgh.snapshot_dir}/My_Snapshot_{suffix}"
    for working_dir in sgh.working_dirs:
        if working_dir.exists():
            shutil.make_archive(snapshot_filename, "zip", working_dir)

    print(f"Snapshot file {snapshot_filename}.zip saved successfully!")


def remove_current_sparkle_platform() -> None:
    """Remove the current Sparkle platform."""
    print("Cleaning existing Sparkle platform ...")
    sfh.remove_temporary_files()

    for working_dir in sgh.working_dirs:
        shutil.rmtree(working_dir, ignore_errors=True)

    ablation_scenario_dir = f"{sgh.ablation_dir}scenarios/"
    shutil.rmtree(Path(ablation_scenario_dir), ignore_errors=True)
    Path("Components/Sparkle-latex-generator/Sparkle_Report.pdf").unlink(missing_ok=True)
    print("Existing Sparkle platform cleaned!")


def extract_sparkle_snapshot(my_snapshot_filename: str) -> None:
    """Restore a Sparkle platform from a snapshot.

    Args:
      my_snapshot_filename: File path to the file where the current Sparkle
        platform should be stored.
    """
    my_suffix = sgh.get_time_pid_random_string()
    my_tmp_directory = f"tmp_directory_{my_suffix}"

    Path(sgh.sparkle_tmp_path).mkdir(exist_ok=True)

    with zipfile.ZipFile(my_snapshot_filename, "r") as zip_ref:
        zip_ref.extractall(my_tmp_directory)
    shutil.copytree(my_tmp_directory, "./", dirs_exist_ok=True)
    shutil.rmtree(Path(my_tmp_directory))


def load_snapshot(snapshot_file_path: str) -> None:
    """Load a Sparkle platform from a snapshot.

    Args:
        snapshot_file_path: File path to the file where the Sparkle
            platform is stored.
    """
    if not Path(snapshot_file_path).exists():
        print(f"ERROR: Snapshot file {snapshot_file_path} does not exist!")
        sys.exit(-1)
    if not snapshot_file_path.endswith(".zip"):
        print(f"ERROR: File {snapshot_file_path} is not a .zip file!")
        sys.exit(-1)
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
        sys.exit(-1)

    print(f"Removing snapshot file {snapshot_file_path} ...")
    shutil.rmtree(snapshot_file_path)
    print(f"Snapshot file {snapshot_file_path} removed!")
