#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for file manipulation."""

import os
import sys
import time
import shutil
import random
import fcntl
from pathlib import Path
from sparkle_help import sparkle_logging as sl

try:
    from Commands.sparkle_help import sparkle_global_help as sgh
    from Commands.sparkle_help import sparkle_snapshot_help as snh
    from Commands.sparkle_help import sparkle_csv_help as scsv
except ImportError:
    import sparkle_snapshot_help as snh
    import sparkle_csv_help as scsv
    import sparkle_global_help as sgh


def create_new_empty_file(filepath: str) -> None:
    """Create a new empty file given a filepath string.

    Args:
      filepath: Path to file.
    """
    fo = Path(filepath).open("w+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.close()


def get_current_directory_name(filepath: str) -> str:
    """Return the name of the current directory as a string.

    Args:
      filepath: Path to file.

    Returns:
      String representation of directory base name.
    """
    if filepath == "":
        print("ERROR: Empty filepath given to get_current_directory_name(), stopping "
              "execution!")
        sys.exit(-1)

    if filepath[-1] == "/":
        filepath = filepath[0:-1]

    # find the last separator
    right_index = filepath.rfind("/")

    if right_index < 0:
        pass
    else:
        filepath = filepath[0:right_index]
        filepath = get_last_level_directory_name(filepath)

    return filepath


def get_last_level_directory_name(filepath: str) -> str:
    """Return the final path component for a given file path.

    Args:
      filepath: Path to file.

    Returns:
      String representation of the last path component.
    """
    if filepath[-1] == "/":
        filepath = filepath[0:-1]

    right_index = filepath.rfind("/")

    if right_index >= 0:
        filepath = filepath[right_index + 1:]

    return filepath


def get_file_name(filepath: str) -> str:
    """Return the name of the file.

    Args:
      filepath: Path to file.

    Returns:
      The actual file name.
    """
    right_index = filepath.rfind("/")
    if right_index >= 0:
        filepath = filepath[right_index + 1:]
    return filepath


def get_directory(filepath: str) -> str:
    """Return the directory component of a path (without the filename).

    Args:
      filepath: Path to file.

    Returns:
      A string with the directory component.
    """
    right_index = filepath.rfind("/")
    if right_index < 0:
        return "./"
    return filepath[:right_index + 1]


def get_file_least_extension(filepath: str) -> str:
    """Return the least file extension  (without the filename) given a file path.

    Args:
      filepath: Path to file.

    Returns:
      A string with the file extension or an empty string if the file has no
      file extension.
    """
    filename = get_file_name(filepath)
    right_index = filename.rfind(".")
    if right_index < 0:
        return ""
    return filename[right_index + 1:]


def get_instance_list_from_reference(instances_path: Path) -> list[str]:
    """Return a list of instances read from a file.

    Args:
      instances_path: Path object pointing to the directory wehre the instances
        are stored.

    Returns:
      List of instances file paths.
    """
    instance_list = []
    instances_path_str = str(instances_path)

    # Read instances from reference file
    instance_list_file_path = sgh.instance_list_path

    with instance_list_file_path.open("r") as infile:
        lines = infile.readlines()

        for line in lines:
            words = line.strip().split()

            if len(words) <= 0:
                continue
            elif line.strip().startswith(instances_path_str):
                instance_list.append(line.strip())

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


def get_list_all_cnf_filename_recursive(path: str,
                                        list_all_cnf_filename: list[str]) -> None:
    """Extend a given list of filenames with all files found under a path.

    This includes all files found in subdirectories of the given path.

    NOTE: Possibly to be merged with get_list_all_filename() since the CNF extension is
    not considered anymore.

    Args:
      path: Target path.
      list_all_cnf_filename: List of filenames (may be empty).
    """
    if Path(path).is_file():
        # TODO: Possibly add extension check back when we get this information from the
        # user
        # file_extension = get_file_least_extension(path)
        # if file_extension == scch.file_extension:
        filename = get_file_name(path)
        list_all_cnf_filename.append(filename)
        return
    elif Path(path).is_dir():
        if path[-1] != "/":
            this_path = path + "/"
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            get_list_all_cnf_filename_recursive(this_path + item, list_all_cnf_filename)
    return


def get_list_all_cnf_filename(filepath: str) -> list[str]:
    """Return list of filenames with all files found under a path.

    Args:
      filepath: Target path.

    Returns:
      List of string filenames.
    """
    list_all_cnf_filename = []
    get_list_all_cnf_filename_recursive(filepath, list_all_cnf_filename)
    return list_all_cnf_filename


def get_list_all_filename_recursive(path: str, list_all_filename: list[str]) -> None:
    """Extend a given list of filenames with all files found under a path.

    This includes all files found in subdirectories of the given path.

    NOTE: Possibly to be merged with get_list_all_cnf_filename() since the CNF extension
    is not considered anymore.

    Args:
      path: Target path.
      list_all_filename: List of filenames (may be empty).
    """
    if Path(path).is_file():
        filename = get_file_name(path)
        list_all_filename.append(filename)
        return
    elif Path(path).is_dir():
        if path[-1] != "/":
            this_path = path + "/"
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            get_list_all_filename_recursive(this_path + item, list_all_filename)


def get_list_all_filename(filepath: str) -> list[str]:
    """Return list of filenames with all files found under a path.

    Args:
      filepath: Target path.

    Returns:
      List of string filenames.
    """
    list_all_filename = []
    get_list_all_filename_recursive(filepath, list_all_filename)
    return list_all_filename


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
        directory = get_directory(path)
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


def get_list_all_directory(filepath: str) -> list[str]:
    """Return a list of directories with all directories found under a path.

    Args:
      filepath: Target path.

    Returns:
      List of directories.
    """
    list_all_directory = []
    get_list_all_directory_recursive(filepath, list_all_directory)
    return list_all_directory


def get_list_all_csv_filename(filepath: str) -> list[str]:
    """Return a list of all CSV files in a given path.

    Args:
      filepath: Target path.

    Returns:
      List of CSV filenames.
    """
    csv_list = []
    if not Path(filepath).exists():
        return csv_list

    list_all_items = os.listdir(filepath)
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == r"csv":
            csv_list.append(list_all_items[i])
    return csv_list


def get_list_all_result_filename(filepath: str) -> list[str]:
    """Return a list of result files in a given path.

    Args:
      filepath: Target path.

    Returns:
      List of result files.
    """
    result_list = []
    if not Path(filepath).exists():
        return result_list

    list_all_items = os.listdir(filepath)
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == "result":
            result_list.append(list_all_items[i])
    return result_list


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
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == "jobinfo":
            jobinfo_list.append(list_all_items[i])
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
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == "statusinfo":
            statusinfo_list.append(list_all_items[i])
    return statusinfo_list


def add_new_instance_into_file(filepath: str) -> None:
    """Add an instance to a given instance file.

    Args:
      filepath: Path to the instance.
    """
    fo = Path(str(sgh.instance_list_path)).open("a+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(filepath + "\n")
    fo.close()


def add_new_solver_into_file(filepath: str, deterministic: int = 0,
                             solver_variations: int = 1) -> None:
    """Add a solver to an existing file listing solvers and their details.

    Args:
      filepath: Path to the file with solver (details).
      deterministic: 1 for deterministic solvers and 0 for stochastic solvers.
        Default is 0.
      solver_variations: Number of different solver variations. Default is 1.
    """
    fo = Path(sgh.solver_list_path).open("a+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(f"{filepath} {str(deterministic)} {str(solver_variations)}\n")
    fo.close()


def add_new_solver_nickname_into_file(nickname: str, filepath: str) -> None:
    """Add a new solver nickname to a given file.

    Args:
      nickname: Nickname for the solver.
      filepath: Path to the file.
    """
    fo = Path(sgh.solver_nickname_list_path).open("a+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(nickname + r" " + filepath + "\n")
    fo.close()


def add_new_extractor_into_file(filepath: str) -> None:
    """Add a new feature extractor to a given file.

    Args:
      filepath: Path to the target file.
    """
    fo = Path(sgh.extractor_list_path).open("a+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(filepath + "\n")
    fo.close()


def add_new_extractor_feature_vector_size_into_file(filepath: str,
                                                    feature_vector_size: int) -> None:
    """Add a new feature vector size to a given file.

    Args:
      filepath: Path to the target file.
      feature_vector_size: Feature vector size.
    """
    fo = Path(sgh.extractor_feature_vector_size_list_path).open("a+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(filepath + r" " + str(feature_vector_size) + "\n")
    fo.close()


def add_new_extractor_nickname_into_file(nickname: str, filepath: str) -> None:
    """Add a new feature extractor nickname to a given file.

    Args:
      nickname: Nickname for the extractor.
      filepath: Path to the target file.
    """
    fo = Path(sgh.extractor_nickname_list_path).open("a+")
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(nickname + r" " + filepath + "\n")
    fo.close()


def write_solver_list() -> None:
    """Write the solver list to the default solver list file."""
    fout = Path(sgh.solver_list_path).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for i in range(0, len(sgh.solver_list)):
        fout.write(sgh.solver_list[i] + "\n")
    fout.close()


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


def write_solver_nickname_mapping() -> None:
    """Write the mapping between solvers and nicknames to file."""
    fout = Path(sgh.solver_nickname_list_path).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for key in sgh.solver_nickname_mapping:
        fout.write(key + r" " + sgh.solver_nickname_mapping[key] + "\n")
    fout.close()


def write_extractor_list() -> None:
    """Write the list of extractors to the default file."""
    fout = Path(sgh.extractor_list_path).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for i in range(0, len(sgh.extractor_list)):
        fout.write(sgh.extractor_list[i] + "\n")
    fout.close()


def write_extractor_feature_vector_size_mapping() -> None:
    """Write the mapping between feature extractors and feature vector sizes to file."""
    fout = Path(sgh.extractor_feature_vector_size_list_path).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for key in sgh.extractor_feature_vector_size_mapping:
        fout.write(f"{key} {str(sgh.extractor_feature_vector_size_mapping[key])}\n")
    fout.close()


def write_extractor_nickname_mapping() -> None:
    """Write the mapping between feature extractors and nicknames to file."""
    fout = Path(sgh.extractor_nickname_list_path).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for key in sgh.extractor_nickname_mapping:
        fout.write(key + r" " + sgh.extractor_nickname_mapping[key] + "\n")
    fout.close()


def write_instance_list() -> None:
    """Write the instance list to the default file."""
    fout = Path(str(sgh.instance_list_path)).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for i in range(0, len(sgh.instance_list)):
        fout.write(sgh.instance_list[i] + "\n")
    fout.close()


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


def rmtree(directory: Path) -> None:
    """Remove a directory and all subdirectories and files under it.

    Args:
      directory: Path object representing the directory.
    """
    if directory.is_dir():
        for path in directory.iterdir():
            if path.is_dir():
                rmtree(path)
            else:
                rmfile(path)
        rmdir(directory)
    else:
        rmfile(directory)

    return


def rmdir(dir_name: Path) -> None:
    """Remove an empty directory.

    Args:
      dir_name: Path object representing the directory.
    """
    try:
        dir_name.rmdir()
    except FileNotFoundError:
        pass


def rmfile(file_name: Path) -> None:
    """Remove a file.

    Args:
      file_name: Path object representing the file.
    """
    file_name.unlink(missing_ok=True)


def check_file_is_executable(file_name: Path) -> None:
    """Check if the given file is executable and create an error if not.

    Args:
      file_name: Path object representing the file.
    """
    if not os.access(file_name, os.X_OK):
        print(
            f"Error: The smac wrapper file {sgh.sparkle_smac_wrapper} is not "
            "executable.\nAdd execution permissions to the file to run the configurator."
        )
        sys.exit()


def create_temporary_directories() -> None:
    """Create directories for temporary files."""
    if not Path("Tmp/").exists():
        Path("Tmp/").mkdir()
        sl.add_output("Tmp/", "Directory with temporary files")

    Path("Tmp/SBATCH_Extractor_Jobs/").mkdir(exist_ok=True)
    Path("Tmp/SBATCH_Solver_Jobs/").mkdir(exist_ok=True)
    Path("Tmp/SBATCH_Portfolio_Jobs/").mkdir(exist_ok=True)
    Path("Tmp/SBATCH_Report_Jobs/").mkdir(exist_ok=True)
    Path("Components/smac-v2.10.03-master-778/tmp/").mkdir(exist_ok=True)
    Path("Feature_Data/Tmp/").mkdir(parents=True, exist_ok=True)
    Path("Performance_Data/Tmp/").mkdir(parents=True, exist_ok=True)
    Path("Performance_Data/Tmp_Pap/").mkdir(parents=True, exist_ok=True)
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
    shutil.rmtree(Path("Performance_Data/Tmp_PaP/"), ignore_errors=True)
    shutil.rmtree(Path("Log/"), ignore_errors=True)

    for filename in Path(".").glob("slurm-*"):
        shutil.rmtree(filename)

    shutil.rmtree(Path("Components/smac-v2.10.03-master-778/tmp/"),
                  ignore_errors=True)

    return


def initialise_sparkle() -> None:
    """Initialize a new Sparkle platform."""
    print("Start initialising Sparkle platform ...")

    sgh.snapshot_dir.mkdir(exist_ok=True)

    if snh.detect_current_sparkle_platform_exists():
        snh.save_current_sparkle_platform()
        snh.remove_current_sparkle_platform()

        print("Current Sparkle platform found!")
        print("Current Sparkle platform recorded!")

    create_temporary_directories()
    pap_sbatch_path = Path(sgh.sparkle_tmp_path) / "SBATCH_Parallel_Portfolio_Jobs"
    pap_sbatch_path.mkdir(exist_ok=True)
    sgh.test_data_dir.mkdir()
    sgh.instance_dir.mkdir()
    sgh.solver_dir.mkdir()
    sgh.extractor_dir.mkdir()
    sgh.reference_list_dir.mkdir()
    sgh.sparkle_algorithm_selector_dir.mkdir()
    sgh.sparkle_parallel_portfolio_dir.mkdir()
    Path(f"{sgh.ablation_dir}scenarios/").mkdir()
    scsv.SparkleCSV.create_empty_csv(sgh.feature_data_csv_path)
    scsv.SparkleCSV.create_empty_csv(sgh.performance_data_csv_path)
    sgh.pap_performance_data_tmp_path.mkdir()
    print("New Sparkle platform initialised!")
