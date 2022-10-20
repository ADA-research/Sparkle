#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import time
import random
import fcntl
from pathlib import Path
from typing import List


try:
    from sparkle_help import sparkle_global_help as sgh
except ImportError:
    import sparkle_global_help as sgh


def create_new_empty_file(filepath: str):
    '''Create a new empty file given a filepath string.'''
    fo = open(filepath, 'w+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.close()

    return


def checkout_directory(path, make_if_not_exist=True):
    if (make_if_not_exist) and not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True)
    return os.path.isdir(path)


def get_current_directory_name(filepath: str) -> str:
    '''Return the name of the current directory as str.'''
    if filepath == '':
        print('ERROR: Empty filepath given to get_current_directory_name(), stopping '
              'execution!')
        sys.exit(-1)

    if filepath[-1] == '/':
        filepath = filepath[0:-1]

    right_index = filepath.rfind('/')

    if right_index < 0:
        pass
    else:
        filepath = filepath[0:right_index]
        filepath = get_last_level_directory_name(filepath)

    return filepath


def get_last_level_directory_name(filepath: str) -> str:
    '''Return the final path component for a given string; similar to Path.name.'''
    if filepath[-1] == '/':
        filepath = filepath[0:-1]

    right_index = filepath.rfind('/')

    if right_index < 0:
        pass
    else:
        filepath = filepath[right_index+1:]

    return filepath


def get_file_name(filepath):
    right_index = filepath.rfind('/')
    filename = filepath
    if right_index < 0:
        pass
    else:
        filename = filepath[right_index+1:]
    return filename


def get_directory(filepath):
    right_index = filepath.rfind('/')
    if right_index < 0:
        directory = './'
    else:
        directory = filepath[:right_index+1]
    return directory


def get_file_full_extension(filepath):
    filename = get_file_name(filepath)
    file_extension = ''
    left_index = filename.find('.')
    if left_index < 0:
        pass
    else:
        file_extension = filename[left_index+1:]
    return file_extension


def get_file_least_extension(filepath):
    filename = get_file_name(filepath)
    file_extension = ''
    right_index = filename.rfind('.')
    if right_index < 0:
        pass
    else:
        file_extension = filename[right_index+1:]
    return file_extension


def get_instance_list_from_reference(instances_path: Path) -> List[str]:
    instance_list = []
    instances_path_str = str(instances_path)

    # Read instances from reference file
    instance_list_file_path = sgh.instance_list_path

    with instance_list_file_path.open('r') as infile:
        lines = infile.readlines()

        for line in lines:
            words = line.strip().split()

            if len(words) <= 0:
                continue
            elif line.strip().startswith(instances_path_str):
                instance_list.append(line.strip())

    return instance_list


def get_solver_list_from_parallel_portfolio(portfolio_path: Path) -> list[str]:
    '''Return a list of solvers for a parallel portfolio specified by its path.'''
    portfolio_solver_list = []
    solvers_path_str = 'Solvers/'

    # Read the included solvers (or solver instances) from file
    portfolio_solvers_file_path = Path(portfolio_path / 'solvers.txt')

    with portfolio_solvers_file_path.open('r') as infile:
        lines = infile.readlines()

        for line in lines:
            words = line.strip().split()

            if len(words) <= 0:
                continue
            elif line.strip().startswith(solvers_path_str):
                portfolio_solver_list.append(line.strip())

    return portfolio_solver_list


def get_list_all_cnf_filename_recursive(path, list_all_cnf_filename):
    if os.path.isfile(path):
        # TODO: Possibly add extension check back when we get this information from the
        # user
        # file_extension = get_file_least_extension(path)
        # if file_extension == scch.file_extension:
        filename = get_file_name(path)
        list_all_cnf_filename.append(filename)
        return
    elif os.path.isdir(path):
        if path[-1] != '/':
            this_path = path + '/'
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            get_list_all_cnf_filename_recursive(this_path+item, list_all_cnf_filename)
    return


def get_list_all_cnf_filename(filepath):
    list_all_cnf_filename = []
    get_list_all_cnf_filename_recursive(filepath, list_all_cnf_filename)
    return list_all_cnf_filename


def get_list_all_filename_recursive(path, list_all_filename):
    if os.path.isfile(path):
        filename = get_file_name(path)
        list_all_filename.append(filename)
        return
    elif os.path.isdir(path):
        if path[-1] != '/':
            this_path = path + '/'
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            get_list_all_filename_recursive(this_path+item, list_all_filename)
    return


def get_list_all_filename(filepath):
    list_all_filename = []
    get_list_all_filename_recursive(filepath, list_all_filename)
    return list_all_filename


def get_list_all_directory_recursive(path, list_all_directory):
    if os.path.isfile(path):
        directory = get_directory(path)
        list_all_directory.append(directory)
        return
    elif os.path.isdir(path):
        if path[-1] != '/':
            this_path = path + '/'
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            get_list_all_directory_recursive(this_path+item, list_all_directory)
    return


def get_list_all_directory(filepath):
    list_all_directory = []
    get_list_all_directory_recursive(filepath, list_all_directory)
    return list_all_directory


def get_list_all_csv_filename(filepath):
    csv_list = []
    if not os.path.exists(filepath):
        return csv_list

    list_all_items = os.listdir(filepath)
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == r'csv':
            csv_list.append(list_all_items[i])
    return csv_list


def get_list_all_result_filename(filepath: str) -> list[str]:
    '''Return a list of result files in a given path.'''
    result_list = []
    if not os.path.exists(filepath):
        return result_list

    list_all_items = os.listdir(filepath)
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == 'result':
            result_list.append(list_all_items[i])
    return result_list


def get_list_all_jobinfo_filename(filepath):
    jobinfo_list = []
    if not os.path.exists(filepath):
        return jobinfo_list

    list_all_items = os.listdir(filepath)
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == r'jobinfo':
            jobinfo_list.append(list_all_items[i])
    return jobinfo_list


def get_list_all_statusinfo_filename(filepath):
    statusinfo_list = []
    if not os.path.exists(filepath):
        return statusinfo_list

    list_all_items = os.listdir(filepath)
    for i in range(0, len(list_all_items)):
        file_extension = get_file_least_extension(list_all_items[i])
        if file_extension == r'statusinfo':
            statusinfo_list.append(list_all_items[i])
    return statusinfo_list


def add_new_instance_into_file(filepath):
    fo = open(str(sgh.instance_list_path), 'a+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(filepath + '\n')
    fo.close()
    return


def add_new_solver_into_file(filepath: str, deterministic: int = 0,
                             solver_variations: int = 1):
    '''Add a solver to an existing file listing solvers and their details.'''
    fo = open(sgh.solver_list_path, 'a+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(f'{filepath} {str(deterministic)} {str(solver_variations)}\n')
    fo.close()

    return


def add_new_solver_nickname_into_file(nickname, filepath):
    fo = open(sgh.solver_nickname_list_path, 'a+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(nickname + r' ' + filepath + '\n')
    fo.close()
    return


def add_new_extractor_into_file(filepath):
    fo = open(sgh.extractor_list_path, 'a+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(filepath + '\n')
    fo.close()
    return


def add_new_extractor_feature_vector_size_into_file(filepath, feature_vector_size):
    fo = open(sgh.extractor_feature_vector_size_list_path, 'a+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(filepath + r' ' + str(feature_vector_size) + '\n')
    fo.close()
    return


def add_new_extractor_nickname_into_file(nickname, filepath):
    fo = open(sgh.extractor_nickname_list_path, 'a+')
    fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
    fo.write(nickname + r' ' + filepath + '\n')
    fo.close()
    return


def write_solver_list():
    fout = open(sgh.solver_list_path, 'w+')
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for i in range(0, len(sgh.solver_list)):
        fout.write(sgh.solver_list[i] + '\n')
    fout.close()
    return


def remove_line_from_file(line_start: str, filepath: Path):
    newlines = []

    # Store lines that do not start with the input line
    with filepath.open('r') as infile:
        for current_line in infile:
            if not current_line.startswith(line_start):
                newlines.append(current_line)

    # Overwrite the file with stored lines
    with filepath.open('w') as outfile:
        for current_line in newlines:
            outfile.write(current_line)

    return


def remove_from_solver_list(filepath):
    newlines = []

    # Store lines that do not contain filepath
    with open(sgh.solver_list_path, 'r') as infile:
        for line in infile:
            if filepath not in line:
                newlines.append(line)

    # Overwrite the file with stored lines
    with open(sgh.solver_list_path, 'w') as outfile:
        for line in newlines:
            outfile.write(line)

    # Remove solver from list
    sgh.solver_list.remove(filepath)

    return


def write_solver_nickname_mapping():
    fout = open(sgh.solver_nickname_list_path, 'w+')
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for key in sgh.solver_nickname_mapping:
        fout.write(key + r' ' + sgh.solver_nickname_mapping[key] + '\n')
    fout.close()
    return


def write_extractor_list():
    fout = open(sgh.extractor_list_path, 'w+')
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for i in range(0, len(sgh.extractor_list)):
        fout.write(sgh.extractor_list[i] + '\n')
    fout.close()
    return


def write_extractor_feature_vector_size_mapping():
    fout = open(sgh.extractor_feature_vector_size_list_path, 'w+')
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for key in sgh.extractor_feature_vector_size_mapping:
        fout.write(f'{key} {str(sgh.extractor_feature_vector_size_mapping[key])}\n')
    fout.close()
    return


def write_extractor_nickname_mapping():
    fout = open(sgh.extractor_nickname_list_path, 'w+')
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for key in sgh.extractor_nickname_mapping:
        fout.write(key + r' ' + sgh.extractor_nickname_mapping[key] + '\n')
    fout.close()
    return


def write_instance_list():
    fout = open(str(sgh.instance_list_path), 'w+')
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    for i in range(0, len(sgh.instance_list)):
        fout.write(sgh.instance_list[i] + '\n')
    fout.close()
    return


def write_string_to_file(file: Path, string: str, append: bool = False, maxtry: int = 5):
    ''' Write 'string' to the file 'file' using a lock and creating the parents path
    if needed. If append is True, the 'string' will be appended to the file, otherwise
    the content of the file will be overwritten. Try a maximum of 'maxtry' times to
    acquire the lock, with a random wait time (min 0.2s, max 1.0s) between each try.
    Raise an OSError exception if it fail to acquire the lock maxtry times.

    WARNING: This function does not add line breaks, if those are desired they have to
    be added manually as part of the string.
    '''
    # Create the full path if needed
    Path(file).parent.mkdir(parents=True, exist_ok=True)

    for i in range(maxtry):
        try:
            with open(file, 'a' if append else 'w') as fout:
                fcntl.flock(fout.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fout.write(string)
                fcntl.flock(fout.fileno(), fcntl.LOCK_UN)
            return
        except OSError as e:
            print(f'Warning: locking file {file} failed (try #{i})')
            if i < maxtry:
                time.sleep(random.randint(1, 5) / 5)
            else:
                raise e

    return


def append_string_to_file(file: Path, string: str, maxtry: int = 5):
    ''' Append 'string' to the file 'file'. Use a lock and creates the parents path
    if needed. Try a maximum of 'maxtry' to acquire the lock.
    Raise an OSError exception if it fail to acquire the lock maxtry times.
    '''
    write_string_to_file(file, string, append=True, maxtry=maxtry)

    return


def rmtree(directory: Path):
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


def rmdir(dir_name: Path):
    try:
        dir_name.rmdir()
    except FileNotFoundError:
        pass

    return


def rmfile(file_name: Path):
    file_name.unlink(missing_ok=True)

    return


def check_file_is_executable(file_name: Path) -> bool:
    if os.access(file_name, os.X_OK):
        return True

    return False
