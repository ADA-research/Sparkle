"""Helper functions for CLI nicknames"""
from pathlib import Path

def resolve_object_name(name: str | Path,
                        nickname_dict: dict = {},
                        target_dir: Path = Path()) -> Path:
    """Attempts to resolve a (nick) name.

    Args:
        name: The (nick)name to resolve
        target_dir: The location where the file object should exist

    Returns:
        Path to the object, None if unresolvable.
    """
    # First check if the name itself exists as a path
    if Path(name).exists():
        return name
    # Second check if its a nickname registered in Sparkle
    if name in nickname_dict:
        return nickname_dict[name]
    # Third check if we can create a valid path with the name
    if (target_dir / name).exists():
        return (target_dir / name)
    return None