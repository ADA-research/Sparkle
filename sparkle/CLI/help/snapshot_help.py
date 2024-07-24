#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""
import shutil
import sys
from pathlib import Path
import zipfile

from sparkle.CLI.help import global_variables as gv
from sparkle.tools.general import get_time_pid_random_string
from sparkle.platform import file_help as sfh


def detect_current_sparkle_platform_exists(check_all_dirs: bool) -> bool:
    """Return whether a Sparkle platform is currently active.

    Args:
        check_all_dirs: variable indicating, if all the directories for a sparkle
            platform should be checked or if just finding one directory is fine
    Returns:
      Boolean value indicating whether a Sparkle platform is active or not.
    """
    if check_all_dirs:
        return all([x.exists() for x in gv.working_dirs])
    return any([x.exists() for x in gv.working_dirs])


def save_current_sparkle_platform() -> None:
    """Store the current Sparkle platform in a .zip file."""
    snapshot_filename = gv.snapshot_dir / f"My_Snapshot_{get_time_pid_random_string()}"
    for working_dir in gv.working_dirs:
        if working_dir.exists():
            shutil.make_archive(snapshot_filename, "zip", working_dir)

    print(f"Snapshot file {snapshot_filename}.zip saved successfully!")


def remove_current_sparkle_platform() -> None:
    """Remove the current Sparkle platform."""
    print("Cleaning existing Sparkle platform ...")
    sfh.remove_temporary_files()
    for working_dir in gv.working_dirs:
        shutil.rmtree(working_dir, ignore_errors=True)
    print("Existing Sparkle platform cleaned!")


def extract_sparkle_snapshot(snapshot_file: Path) -> None:
    """Restore a Sparkle platform from a snapshot.

    Args:
      snapshot_file: Path to the where the current Sparkle platform should be stored.
    """
    tmp_directory = Path(f"tmp_directory_{get_time_pid_random_string()}")
    gv.sparkle_tmp_path.mkdir(exist_ok=True)
    with zipfile.ZipFile(snapshot_file, "r") as zip_ref:
        zip_ref.extractall(tmp_directory)
    shutil.copytree(tmp_directory, "./", dirs_exist_ok=True)
    shutil.rmtree(tmp_directory)


def load_snapshot(snapshot_file: Path) -> None:
    """Load a Sparkle platform from a snapshot.

    Args:
        snapshot_file: File path to the file where the Sparkle platform is stored.
    """
    if not snapshot_file.exists():
        print(f"ERROR: Snapshot file {snapshot_file} does not exist!")
        sys.exit(-1)
    if not snapshot_file.suffix == ".zip":
        print(f"ERROR: File {snapshot_file} is not a .zip file!")
        sys.exit(-1)
    print("Cleaning existing Sparkle platform ...")
    remove_current_sparkle_platform()
    print("Existing Sparkle platform cleaned!")

    print(f"Loading snapshot file {snapshot_file} ...")
    extract_sparkle_snapshot(snapshot_file)
    print(f"Snapshot file {snapshot_file} loaded successfully!")
