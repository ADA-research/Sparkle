#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for file manipulation."""
from __future__ import annotations
from filelock import FileLock
import shutil
from pathlib import Path


def add_remove_platform_item(item: any,
                             file_target: Path,
                             target: list | dict,
                             key: str = None,
                             remove: bool = False) -> None:
    """Add/remove item from a list or dictionary of the platform that must saved to disk.

    Args:
        item: The item to be added to the data structure.
        file_target: Path to the file where we want to keep the disk storage.
        target: Either a list or dictionary to add the item to.
        key: Optional string, in case we use a dictionary.
        remove: If true, remove the item from platform.
                If the target is a dict, the key is used to remove the entry.
    """
    # ast.literal_eval can't deal with Path objects
    if isinstance(item, Path):
        item = str(item)
    if isinstance(file_target, str):
        file_target = Path(file_target)
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
    lock = FileLock(f"{file_target}.lock")
    with lock.acquire(timeout=60):
        file_target.open("w").write(str(target))


def create_temporary_directories() -> None:
    """Create directories for temporary files."""
    tmp_path = Path("Tmp/")
    if not tmp_path.exists():
        tmp_path.mkdir()
    Path("Log/").mkdir(exist_ok=True)


def remove_temporary_files() -> None:
    """Remove temporary files. Only removes files not affecting the sparkle state."""
    cli_help_path = Path("sparkle/CLI/help")
    for filename in cli_help_path.glob("*.pyc"):
        shutil.rmtree(cli_help_path.joinpath(filename))
    shutil.rmtree(Path("Tmp/"), ignore_errors=True)
    shutil.rmtree(Path("Feature_Data/Tmp/"), ignore_errors=True)
    shutil.rmtree(Path("Log/"), ignore_errors=True)
