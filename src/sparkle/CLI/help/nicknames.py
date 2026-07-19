"""Helper functions for CLI nicknames."""

from __future__ import annotations
from pathlib import Path
from typing import Callable
from sparkle.instance import Instance_Set, InstanceSet, MultiFileInstanceSet


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
    instance_pair: tuple[str, str],
    instance_set: str | Path | list[InstanceSet],
) -> str | Path | list[Path] | None:
    """Attempts to resolve an instance pair to its file path(s).

    Args:
        instance_pair: The (set_name, instance_name) pair to resolve. The set_name is
            used to look in the correct set, so instances sharing a name across
            different sets are not confused with one another.
        instance_set: Where to look for the instance. Either a str/Path to a directory
            containing instance sets, or the instance sets themselves as a list.

    Returns:
        The path of the instance (multi-file instances are returned as a space-joined
        string of their paths), or None if it cannot be resolved.
    """
    set_name, instance_name = instance_pair

    # Check if the name is already an instance file path
    name_path = Path(instance_name)
    if name_path.exists() and name_path.is_file():
        return instance_name
    # Attempt to find files
    matches = [path for path in name_path.parent.glob(name_path.name + ".*")]
    if matches:
        return " ".join(str(path) for path in matches)  # Concat for multi file instance
    # Normalise instance_set into a list of InstanceSet objects. A str/Path points to a
    # directory that contains instance set directories.
    if isinstance(instance_set, (str, Path)):
        instance_sets = [
            Instance_Set(instance_dir)
            for instance_dir in Path(instance_set).iterdir()
            if instance_dir.is_dir()
        ]
    else:
        instance_sets = instance_set
    # We know which set the instance belongs to: restrict the search to that set so a
    # shared instance name in another set cannot shadow it. Fall back to all sets if the
    # named set is not among those given.
    matching_sets = [inst_set for inst_set in instance_sets if inst_set.name == set_name]
    search_sets = matching_sets if matching_sets else instance_sets

    instance_path = None
    for current_set in search_sets:
        instance_path = current_set.get_path_by_name(instance_name)
        if instance_path is None:
            continue
        # Handle multi file instance
        if isinstance(current_set, MultiFileInstanceSet):
            instance_path = (
                [instance_path] if not isinstance(instance_path, list) else instance_path
            )
            instance_path = " ".join(str(path) for path in instance_path)
        break
    return instance_path
