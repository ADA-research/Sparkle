"""This package provides instance set support for Sparkle."""
from sparkle.instance.instances import \
    MultiFileInstanceSet, FileInstanceSet, IterableFileInstanceSet, InstanceSet
from pathlib import Path


def Instance_Set(target: Path) -> InstanceSet:
    """The combined interface for all instance set types."""
    if (target / MultiFileInstanceSet.instance_csv).exists():
        return MultiFileInstanceSet(target)
    elif (not target.exists()) and (target.parent / MultiFileInstanceSet.instance_csv).exists():
        # Single instance
        return MultiFileInstanceSet(target)
    elif target.is_dir() and all([p.suffix in IterableFileInstanceSet.supported_filetypes for p in target.iterdir()]):
        return IterableFileInstanceSet(target)
    return FileInstanceSet(target)
