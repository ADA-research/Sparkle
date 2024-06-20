#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for file manipulation."""

from __future__ import annotations

import os
import time
import shutil
import random
import fcntl
from pathlib import Path

import sparkle_logging as sl
import global_variables as gv


def create_new_empty_file(filepath: str) -> None:
    """Create a new empty file given a filepath string.

    Args:
      filepath: Path to file.
    """
    Path(filepath).write_text("")


def get_list_all_filename_recursive(path: Path) -> list[Path]:
    """Extend a given list of filenames with all files found under a path.

    This includes all files found in subdirectories of the given path.

    Args:
      path: Target path.
      list_all_filename: List of filenames (may be empty).
    """
    if isinstance(path, str):
        path = Path(path)
    return [p for p in Path(path).rglob("*") if p.is_file()]


def get_list_all_extensions(filepath: Path, suffix: str) -> list[str]:
    """Return a list of files with a certain suffix in a given path.

    Args:
      filepath: Target path.

    Returns:
      List of result files.
    """
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    if not filepath.exists():
        return []
    return [str(x) for x in Path.iterdir(filepath) if x.suffix == suffix]


def add_remove_platform_item(item: any,
                             file_target: Path,
                             target: list | dict = None,
                             key: str = None,
                             remove: bool = False) -> None:
    """Add/remove item from a list or dictionary of the platform that must saved to disk.

    Args:
        item: The item to be added to the data structure.
        target: Either a list or dictionary to add the item to.
        file_target: Path to the file where we want to keep the disk storage.
        key: Optional string, in case we use a dictionary.
        remove: If true, remove the item from platform.
                If the target is a dict, the key is used to remove the entry.
    """
    # ast.literal_eval can't deal with Path objects
    if isinstance(item, Path):
        item = str(item)
    if isinstance(file_target, str):
        file_target = Path(file_target)
    # Determine object if not present
    if target is None:
        target = gv.file_storage_data_mapping[file_target]
    # Add/Remove item to/from object
    if isinstance(target, dict):
        if remove:
            del target[key]
        else:
            target[key] = item
    else:
        if remove:
            target.remove(item)
        else:
            target.append(item)
    # (Over)Write data structure to path
    with file_target.open("w") as fout:
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        fout.write(str(target))


def write_string_to_file(file: Path, string: str,
                         append: bool = False, maxtry: int = 5) -> None:
    """Write 'string' to the file 'file'.

    A lock is used when writing and creating the parents path
    if needed. If append is True, the 'string' will be appended to the file, otherwise
    the content of the file will be overwritten. Try a maximum of 'maxtry' times to
    acquire the lock, with a random wait time (min 0.2s, max 1.0s) between each try.
    Raise an OSError exception if it fail to acquire the lock maxtry times.

    WARNING: This function does not add line breaks, if those are desired they have to
    be added manually as part of the string.

    Args:
      file: Path object of the target file.
      string: String we want to write to 'file'.
      append: Boolean indicating whether 'string' should be appended to the file.
        The default is False, i.e., the file content is overwritten with 'string'.
      maxtry: The maximum number of trials. A trial is considered as failed if
        locking 'file' failed. The default is 5.
    """
    # Create the full path if needed
    Path(file).parent.mkdir(parents=True, exist_ok=True)

    for i in range(maxtry):
        # TODO: This is a strange make-shift construct of handling file locks.
        # Especially the part of randomizing the sleep seconds. This code must be
        # refactored to work with standard Python methods/libraries.
        try:
            with Path(file).open("a" if append else "w") as fout:
                fcntl.flock(fout.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fout.write(string)
                fcntl.flock(fout.fileno(), fcntl.LOCK_UN)
            return
        except OSError as e:
            print(f"Warning: locking file {file} failed (try #{i})")
            if i < maxtry:
                time.sleep(random.randint(1, 5) / 5)
            else:
                raise e


def rmfiles(files: list[Path]) -> None:
    """Remove one or more files.

    Args:
      files: List of path object representing the file.
    """
    if not isinstance(files, list):
        files = [files]

    for file in files:
        if isinstance(file, str):
            file = Path(file)
        file.unlink(missing_ok=True)


def check_file_is_executable(file_name: Path) -> bool:
    """Check if the given file is executable and create an error if not.

    Args:
      file_name: Path object representing the file.
    """
    return os.access(file_name, os.X_OK)


def create_temporary_directories() -> None:
    """Create directories for temporary files."""
    tmp_path = Path("Tmp/")
    if not tmp_path.exists():
        tmp_path.mkdir()
        sl.add_output("Tmp/", "Directory with temporary files")
    Path("Feature_Data/Tmp/").mkdir(parents=True, exist_ok=True)
    Path("Performance_Data/Tmp/").mkdir(parents=True, exist_ok=True)
    gv.pap_performance_data_tmp_path.mkdir(parents=True, exist_ok=True)
    Path("Log/").mkdir(exist_ok=True)


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    sparkle_help_path = Path("CLI/sparkle_help")
    for filename in sparkle_help_path.glob("*.pyc"):
        shutil.rmtree(sparkle_help_path.joinpath(filename))
    shutil.rmtree(Path("Tmp/"), ignore_errors=True)
    shutil.rmtree(Path("Feature_Data/Tmp/"), ignore_errors=True)
    shutil.rmtree(Path("Performance_Data/Tmp/"), ignore_errors=True)
    shutil.rmtree(gv.pap_performance_data_tmp_path, ignore_errors=True)
    shutil.rmtree(Path("Log/"), ignore_errors=True)

    for filename in Path("../../CLI/sparkle_help").glob("slurm-*"):
        shutil.rmtree(filename)
