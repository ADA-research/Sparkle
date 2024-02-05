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
            words = line.strip().split()

            if len(words) <= 0:
                continue
            elif line.strip().startswith(solvers_path_str):
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


def get_list_all_directory_recursive(path: str, list_all_directory: list[str]) -> None:
    """Extend a given list of directories with all directories found under a path.

    This includes all directories found in subdirectories of the given path.

    NOTE: Possibly to be merged with get_list_all_cnf_filename() since the CNF extension
    is not considered anymore.

    Args:
      path: Target path.
      list_all_directory: List of directories.
    """
    if Path(path).is_file():
        directory = Path(path).parent
        list_all_directory.append(directory)
        return
    elif Path(path).is_dir():
        if path[-1] != "/":
            this_path = path + "/"
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            get_list_all_directory_recursive(this_path + item, list_all_directory)
    return


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


def get_list_all_jobinfo_filename(filepath: str) -> list[str]:
    """Return a list of jobinfo files in a given path.

    Args:
      filepath: Target path.

    Returns:
      List of jobinfo files.
    """
    jobinfo_list = []
    if not Path(filepath).exists():
        return jobinfo_list

    list_all_items = os.listdir(filepath)
    for item in list_all_items:
        file_extension = Path(item).suffix
        if file_extension == "jobinfo":
            jobinfo_list.append(item)
    return jobinfo_list


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


def add_new_instance_into_file(filepath: str) -> None:
    """Add an instance to a given instance file.

    Args:
      filepath: Path to the instance.
    """
    with sgh.instance_list_path.open("a+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(filepath + "\n")


def add_new_solver_into_file(filepath: str, deterministic: int = 0,
                             solver_variations: int = 1) -> None:
    """Add a solver to an existing file listing solvers and their details.

    Args:
      filepath: Path to the file with solver (details).
      deterministic: 1 for deterministic solvers and 0 for stochastic solvers.
        Default is 0.
      solver_variations: Number of different solver variations. Default is 1.
    """
    with Path(sgh.solver_list_path).open("a+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(f"{filepath} {str(deterministic)} {str(solver_variations)}\n")


def add_new_solver_nickname_into_file(nickname: str, filepath: str) -> None:
    """Add a new solver nickname to a given file.

    Args:
      nickname: Nickname for the solver.
      filepath: Path to the file.
    """
    with Path(sgh.solver_nickname_list_path).open("a+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(nickname + r" " + filepath + "\n")


def add_new_extractor_into_file(filepath: str) -> None:
    """Add a new feature extractor to a given file.

    Args:
      filepath: Path to the target file.
    """
    with Path(sgh.extractor_list_path).open("a+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(filepath + "\n")


def add_new_extractor_feature_vector_size_into_file(filepath: str,
                                                    feature_vector_size: int) -> None:
    """Add a new feature vector size to a given file.

    Args:
      filepath: Path to the target file.
      feature_vector_size: Feature vector size.
    """
    with Path(sgh.extractor_feature_vector_size_list_path).open("a+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(filepath + r" " + str(feature_vector_size) + "\n")


def add_new_extractor_nickname_into_file(nickname: str, filepath: str) -> None:
    """Add a new feature extractor nickname to a given file.

    Args:
      nickname: Nickname for the extractor.
      filepath: Path to the target file.
    """
    with Path(sgh.extractor_nickname_list_path).open("a+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(nickname + r" " + filepath + "\n")


def write_solver_list() -> None:
    """Write the solver list to the default solver list file."""
    with Path(sgh.solver_list_path).open("w+") as fout:
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        for solver in sgh.solver_list:
            fout.write(solver + "\n")


def remove_line_from_file(line_start: str, filepath: Path) -> None:
    """Remove all lines starting with a given string from a given file.

    Args:
      line_start: The prefix string.
      filepath: A Path object representing the file.
    """
    newlines = []

    # Store lines that do not start with the input line
    with filepath.open("r") as infile:
        for current_line in infile:
            if not current_line.startswith(line_start):
                newlines.append(current_line)

    # Overwrite the file with stored lines
    with filepath.open("w") as outfile:
        for current_line in newlines:
            outfile.write(current_line)


def remove_from_solver_list(filepath: str) -> None:
    """Remove a solver from the list and the solver file.

    Args:
      filepath: Path to the solver file.
    """
    newlines = []

    # Store lines that do not contain filepath
    with Path(sgh.solver_list_path).open("r") as infile:
        for line in infile:
            if filepath not in line:
                newlines.append(line)

    # Overwrite the file with stored lines
    with Path(sgh.solver_list_path).open("w") as outfile:
        for line in newlines:
            outfile.write(line)

    # Remove solver from list
    sgh.solver_list.remove(filepath)


def write_data_to_file(target_file: Path, object: list | dict) -> None:
    """Write an object to a file.

    target_file: Path object describing file to write the data to.
    object: Either list or dict, to write to the file. In case of dict, the key is also
            written to the file.
    """
    with target_file.open("w+") as fout:
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        if isinstance(object, dict):
            for key in object:
                fout.write(f"{key} {object[key]}\n")
        elif isinstance(object, list):
            for item in object:
                fout.write(f"{item}\n")


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
