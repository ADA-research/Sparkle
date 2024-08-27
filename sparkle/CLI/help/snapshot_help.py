#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to record and restore a Sparkle platform."""
import shutil
import sys
import os
import time
from pathlib import Path
import zipfile

from sparkle.CLI.help import global_variables as gv
from sparkle.tools.general import get_time_pid_random_string


def save_current_sparkle_platform() -> None:
    """Store the current Sparkle platform in a .zip file."""
    time_stamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    snapshot_tmp_path = gv.settings().DEFAULT_snapshot_dir /\
        f"Snapshot_{os.getlogin()}_{time_stamp}"
    snapshot_tmp_path.mkdir(parents=True)  # Create temporary directory for zip
    for working_dir in gv.settings().DEFAULT_working_dirs:
        if working_dir.exists():
            shutil.copytree(working_dir, snapshot_tmp_path / working_dir.name)
    shutil.make_archive(snapshot_tmp_path, "zip", snapshot_tmp_path)
    shutil.rmtree(snapshot_tmp_path)
    print(f"Snapshot file {snapshot_tmp_path}.zip saved successfully!")


def remove_current_platform() -> None:
    """Remove the current Sparkle platform."""
    for working_dir in gv.settings().DEFAULT_working_dirs:
        shutil.rmtree(working_dir, ignore_errors=True)


def create_working_dirs() -> None:
    """Create working directories."""
    for working_dir in gv.settings().DEFAULT_working_dirs:
        working_dir.mkdir(parents=True, exist_ok=True)


def extract_snapshot(snapshot_file: Path) -> None:
    """Restore a Sparkle platform from a snapshot.

    Args:
      snapshot_file: Path to the where the current Sparkle platform should be stored.
    """
    tmp_directory = Path(f"tmp_directory_{get_time_pid_random_string()}")
    gv.settings().DEFAULT_tmp_output.mkdir(exist_ok=True)
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
    remove_current_platform()
    print("Existing Sparkle platform cleaned!")

    print(f"Loading snapshot file {snapshot_file} ...")
    extract_snapshot(snapshot_file)
    print(f"Snapshot file {snapshot_file} loaded successfully!")
