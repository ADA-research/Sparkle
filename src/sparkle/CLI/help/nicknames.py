"""Helper functions for CLI nicknames."""

from __future__ import annotations
from pathlib import Path
from typing import Callable
import glob
from sparkle.instance import Instance_Set, InstanceSet


def resolve_object_name(
    name: str | Path,
    nickname_dict: dict = {},
    target_dir: Path = Path(),
    class_name: Callable = None,
) -> Path | any:
    """Attempts to resolve a (nick) name.

    Args:
        name: The (nick)name to resolve
        target_dir: The location where the file object should exist
        nickname_dict: Nicknames
        class_name: If passed, will attempt to return an object
            that is constructed from this Path.

    Returns:
        Path to the object, None if unresolvable.
    """
    path = None
    # We cannot handle None as a name
    if name is None:
        return None
    # First check if the name already is a path
    if isinstance(name, (str, Path)) and Path(name).exists():
        path = Path(name)
    # Second check if its a nickname registered in Sparkle
    elif str(name) in nickname_dict:
        path = Path(nickname_dict[str(name)])
    # Third check if we can create a valid path with the name
    elif isinstance(name, (str, Path)) and (target_dir / name).exists():
        path = target_dir / name
    # Finally, attempt to construct the object from the Path
    try:
        if class_name is not None:
            if path is not None:
                return class_name(path)
            if name is not None:
                return class_name(name)
    except Exception:
        return None
    return path


def resolve_instance_name(
    name: str, target: Path | list[InstanceSet], return_path: bool = True
) -> str | InstanceSet:
    """Attempts to resolve an instance name.

    Args:
        name: The name to resolve
        target: Path to look for instance sets or the instance sets directly
        return_path: Whether to return the path of the instance or the instance set

    Returns:
        The path or the instance set of the given instance name
    """
    # Check if name is a multi file instance path
    matches = glob.glob(name + ".*")

    # Check if the name is already an instance file path
    name_path = Path(name)
    if name_path.exists() and name_path.is_file():
        return name
    # Concat multi file instance
    elif matches:
        return " ".join(str(p) for p in matches)
    # Target is a path to a directory that contains instance directories
    elif isinstance(target, Path):
        instances = []
        for instance_dir in target.iterdir():
            if instance_dir.is_dir():
                instances.append(Instance_Set(instance_dir))
        target = instances

    out_set = None
    for instance_set in target:
        instance_path = instance_set.get_path_by_name(name)
        if instance_path is None:
            continue
        out_set = instance_set
        # Handle multi file instance
        instance_path = (
            [instance_path] if not isinstance(instance_path, list) else instance_path
        )
        instance_path = " ".join(str(p) for p in instance_path)
        break

    return instance_path if return_path else out_set
