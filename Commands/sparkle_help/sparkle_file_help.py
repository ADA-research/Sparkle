#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for file manipulation."""

from __future__ import annotations

import os
import sys
import time
import shutil
import random
import fcntl
from pathlib import Path


from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_snapshot_help as snh
from Commands.sparkle_help import sparkle_csv_help as scsv


def create_new_empty_file(filepath: str) -> None:
    """Create a new empty file given a filepath string.

    Args:
      filepath: Path to file.
    """
    fo = Path(filepath).open("w+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.close()


def get_last_level_directory_name(filepath: str) -> str:
    """Return the final path component for a given file path.

    Args:
      filepath: Path to file.

    Returns:
      String representation of the last path component.
    """
    if Path(filepath).is_file():
        return Path(filepath).parent.name
    return Path(filepath).name


def get_instance_list_from_reference(instances_path: Path) -> list[str]:
    """Return a list of instances read from a file.

    Args:
      instances_path: Path object pointing to the directory wehre the instances
        are stored.

    Returns:
      List of instances file paths.
    """
    # Read instances from reference file
    with sgh.instance_list_path.open("r") as infile:
        instance_list = [x.strip() for x in infile.readlines()
                         if x.startswith(str(instances_path))]

    return instance_list


def get_solver_list_from_parallel_portfolio(portfolio_path: Path) -> list[str]:
    """Return a list of solvers for a parallel portfolio specified by its path.

    Args:
      portfolio_path: Path object pointing to the directory where solvers
        are stored.

    Returns:
      List of solvers.
    """
    portfolio_solver_list = []
    solvers_path_str = "Solvers/"

    # Read the included solvers (or solver instances) from file
    portfolio_solvers_file_path = Path(portfolio_path / "solvers.txt")

    with portfolio_solvers_file_path.open("r") as infile:
        lines = infile.readlines()
        for line in lines:
            if line.strip().startswith(solvers_path_str):
                portfolio_solver_list.append(line.strip())

    return portfolio_solver_list


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
        suffix = "." + suffix
    if not filepath.exists():
        return []
    return [str(x) for x in Path.iterdir(filepath) if x.suffix == suffix]


def get_list_all_statusinfo_filename(filepath: str) -> list[str]:
    """Return a list of statusinfo files in a given path.

    Args:
      filepath: Target path.

    Returns:
      List of statusinfo files.
    """
    statusinfo_list = []
    if not Path(filepath).exists():
        return statusinfo_list

    list_all_items = os.listdir(filepath)
    for item in list_all_items:
        if Path(item).suffix == "statusinfo":
            statusinfo_list.append(item)
    return statusinfo_list


def add_remove_platform_item(item: any,
                             file_target: Path,
                             target: list | dict = None,
                             key: str = None,
                             remove: bool = False) -> None:
    """Add an item to or remove from a list or dictionary
       of the platform that must saved to disk.

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
        target = sgh.file_storage_data_mapping[file_target]
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


def append_string_to_file(file: Path, string: str, maxtry: int = 5) -> None:
    """Append 'string' to the file 'file'.

    Use a lock and creates the parents path
    if needed. Try a maximum of 'maxtry' to acquire the lock.
    Raise an OSError exception if it fail to acquire the lock maxtry times.

    Args:
      file: Path object of the target file.
      string: String we want to write to 'file'.
      maxtry: The maximum number of trials. A trial is considered as failed if
        locking 'file' failed. The default is 5.
    """
    write_string_to_file(file, string, append=True, maxtry=maxtry)

    return


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


def check_file_is_executable(file_name: Path) -> None:
    """Check if the given file is executable and create an error if not.

    Args:
      file_name: Path object representing the file.
    """
    if not os.access(file_name, os.X_OK):
        print("Error: The configurator wrapper file "
              f"{file_name} is not executable.\n"
              "Add execution permissions to the file to run the configurator.")
        sys.exit(-1)


def create_temporary_directories() -> None:
    """Create directories for temporary files."""
    tmp_path = Path("Tmp/")
    if not tmp_path.exists():
        tmp_path.mkdir()
        sl.add_output("Tmp/", "Directory with temporary files")

    Path("Components/smac-v2.10.03-master-778/tmp/").mkdir(exist_ok=True)
    Path("Feature_Data/Tmp/").mkdir(parents=True, exist_ok=True)
    Path("Performance_Data/Tmp/").mkdir(parents=True, exist_ok=True)
    sgh.pap_performance_data_tmp_path.mkdir(parents=True, exist_ok=True)
    Path("Log/").mkdir(exist_ok=True)
    return


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    sparkle_help_path = Path("Commands/sparkle_help")
    for filename in sparkle_help_path.glob("*.pyc"):
        shutil.rmtree(sparkle_help_path.joinpath(filename))
    shutil.rmtree(Path("Tmp/"), ignore_errors=True)
    shutil.rmtree(Path("Feature_Data/Tmp/"), ignore_errors=True)
    shutil.rmtree(Path("Performance_Data/Tmp/"), ignore_errors=True)
    shutil.rmtree(sgh.pap_performance_data_tmp_path, ignore_errors=True)
    shutil.rmtree(Path("Log/"), ignore_errors=True)

    for filename in Path(".").glob("slurm-*"):
        shutil.rmtree(filename)

    shutil.rmtree(Path("Components/smac-v2.10.03-master-778/tmp/"),
                  ignore_errors=True)
    return


def initialise_sparkle(argv: list[str]) -> None:
    """Initialize a new Sparkle platform.

    Args:
        argv: The argument list for the log_command
    """
    print("Start initialising Sparkle platform ...")

    sgh.snapshot_dir.mkdir(exist_ok=True)

    if snh.detect_current_sparkle_platform_exists(check_all_dirs=False):
        snh.save_current_sparkle_platform()
        snh.remove_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    # Log command call
    sl.log_command(argv)

    create_temporary_directories()

    for working_dir in sgh.working_dirs:
        working_dir.mkdir(exist_ok=True)
    Path(f"{sgh.ablation_dir}scenarios/").mkdir(exist_ok=True)
    scsv.SparkleCSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(sgh.performance_data_csv_path)
    sgh.pap_performance_data_tmp_path.mkdir(exist_ok=True)

    print("New Sparkle platform initialised!")
