#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""

import os
import shutil
import sys
from pathlib import Path

from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_file_help as sfh

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
    suffix = sbh.get_time_pid_random_string()
    snapshot_filename = f"{sgh.snapshot_dir}/My_Snapshot_{suffix}.zip"

    Path(snapshot_filename).mkdir(exist_ok=True)

    for act_dir in sgh.working_dirs:
        if act_dir.exists():
            os.system(f"zip -g -r {snapshot_filename} {act_dir} >> "
                      f"{snapshot_log_file_path}")

    print(f"Snapshot file {snapshot_filename} saved successfully!")
    os.system("rm -f " + snapshot_log_file_path)


def remove_current_sparkle_platform() -> None:
    """Remove the current Sparkle platform."""
    print("Cleaning existing Sparkle platform ...")
    sfh.remove_temporary_files()

    for act_dir in sgh.working_dirs:
        shutil.rmtree(act_dir, ignore_errors=True)

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
