#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for instance (set) management."""
import shutil
from pathlib import Path
from typing import Union

from sparkle.platform import file_help as sfh
import global_variables as gv


__sparkle_instance_list_file = "sparkle_instance_list.txt"


def get_list_all_path(instances_directory: Union[str, Path]) -> list[Path]:
    """Return a list with all instance paths."""
    p = Path(instances_directory)

    return [f for f in p.rglob("*") if f.is_file()]


def _check_existence_of_instance_list_file(instances_source: str) -> bool:
    """Return whether a given instance list file exists."""
    if not Path(instances_source).is_dir():
        return False

    instance_list_file_path = Path(instances_source) / __sparkle_instance_list_file

    if Path(instance_list_file_path).is_file():
        return True
    else:
        return False


def _get_list_instance(instances_source: str) -> list[str]:
    """Return a list of instances."""
    list_instance = []
    instance_list_file_path = Path(instances_source) / __sparkle_instance_list_file
    infile = Path(instance_list_file_path).open()
    lines = infile.readlines()

    for line in lines:
        words = line.strip().split()

        if len(words) <= 0:
            continue
        list_instance.append(line.strip())

    infile.close()

    return list_instance


def get_instance_list_from_path(path: Path) -> list[str]:
    """Return a list of instance name strings located in a given path."""
    # Multi-file instances
    if _check_existence_of_instance_list_file(str(path)):
        list_all_filename = _get_list_instance(str(path))
    # Single file instances
    else:
        list_all_filename = [file.name for file in
                             sfh.get_list_all_filename_recursive(path)]

    return list_all_filename


def _copy_instance_list_to_reference(instances_source: Path) -> None:
    """Copy an instance list to the reference list directory."""
    instance_list_path = Path(instances_source / Path(__sparkle_instance_list_file))
    target_path = Path(gv.reference_list_dir
                       / Path(instances_source.name + gv.instance_list_postfix))
    shutil.copy(instance_list_path, target_path)
    return


def count_instances_in_reference_list(instance_set_name: str) -> int:
    """Return the number of instances in a given instance set.

    Args:
        instance_set_name: The name of the instance set.

    Returns:
        An integer indicating the number of instances in this set.
    """
    count = 0
    instance_list_path = Path(gv.reference_list_dir
                              / Path(instance_set_name + gv.instance_list_postfix))

    # Count instances in instance list file
    with instance_list_path.open("r") as infile:
        for line in infile:
            # If the line does not only contain white space, count it
            if line.strip():
                count = count + 1

    return count


def check_existence_of_reference_instance_list(instance_set_name: str) -> bool:
    """Return whether a file with a list of instances exists for a given instance set.

    Args:
        instance_set_name: The name of the instance set.

    Returns:
        A bool indicating whether a reference list of the instances in this set exists.
    """
    instance_list_path = Path(gv.reference_list_dir
                              / Path(instance_set_name + gv.instance_list_postfix))
    return instance_list_path.is_file()


def remove_reference_instance_list(instance_set_name: str) -> None:
    """Remove a file with a list of instances."""
    instance_list_path = Path(gv.reference_list_dir
                              / Path(instance_set_name + gv.instance_list_postfix))

    sfh.rmfiles(instance_list_path)

    return


def copy_reference_instance_list(target_file: Path, instance_set_name: str,
                                 path_modifier: str) -> None:
    """Copy a file with a list of instances."""
    instance_list_path = Path(gv.reference_list_dir
                              / Path(instance_set_name + gv.instance_list_postfix))
    outlines = []

    # Add quotes around instances in instance list file
    with instance_list_path.open("r") as infile:
        for line in infile:
            outline = '\"'

            # Modify path for each instance file
            for word in line.strip().split():
                outline = outline + path_modifier + word + " "

            outline = outline + '\"\n'
            outlines.append(outline)

    # Write quoted instance list to SMAC instance file
    with target_file.open("w") as outfile:
        for line in outlines:
            outfile.write(line)

    return
