"""Helper functions for CLI nicknames."""
from __future__ import annotations
from pathlib import Path
from typing import Callable


def resolve_object_name(name: str | Path,
                        nickname_dict: dict = {},
                        target_dir: Path = Path(),
                        class_name: Callable = None) -> Path | any:
    """Attempts to resolve a (nick) name.

    Args:
        name: The (nick)name to resolve
        target_dir: The location where the file object should exist
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
        path = (target_dir / name)
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
