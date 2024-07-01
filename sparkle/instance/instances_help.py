#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for instance (set) management."""
from pathlib import Path

from sparkle.platform import file_help as sfh


# NOTE: These variables have been copied/moved from global variables
# This is not the cleanest solution and should be solved in SPRK-271
reference_list_dir = Path("Reference_Lists")
instance_list_postfix = "_instance_list.txt"
_instance_list_file = "sparkle_instance_list.txt"


def _check_existence_of_instance_list_file(instances_source: Path) -> bool:
    """Return whether a given instance list file exists."""
    if not instances_source.is_dir():
        return False

    instance_list_file_path = instances_source / _instance_list_file

    return instance_list_file_path.is_file()


def _get_list_instance(instances_source: str) -> list[str]:
    """Return a list of instances."""
    list_instance = []
    instance_list_file_path = Path(instances_source) / _instance_list_file
    lines = Path(instance_list_file_path).open().readlines()

    for line in lines:
        words = line.strip().split()
        if len(words) > 0:
            list_instance.append(line.strip())

    return list_instance


def get_instance_list_from_path(path: Path) -> list[str]:
    """Return a list of instance name strings located in a given path."""
    # Multi-file instances
    if _check_existence_of_instance_list_file(path):
        list_all_filename = _get_list_instance(str(path))
    # Single file instances
    else:
        list_all_filename = [file.name for file in
                             sfh.get_file_paths_recursive(path)]

    return list_all_filename

