"""This package provides instance set support for Sparkle."""
from sparkle.instance.instances import \
    MultiFileInstanceSet, FileInstanceSet, IterableFileInstanceSet, InstanceSet
from pathlib import Path


def Instance_Set(target: any) -> InstanceSet:
    """The combined interface for all instance set types."""
    if ((isinstance(target, Path)
            and (target / MultiFileInstanceSet.instance_csv).exists())
            or isinstance(target, list)):
        return MultiFileInstanceSet(target)
    elif (isinstance(target, Path) and target.is_dir()
          and all([p.suffix in IterableFileInstanceSet.supported_filetypes
                   for p in target.iterdir()])):
        return IterableFileInstanceSet(target)
    return FileInstanceSet(target)
