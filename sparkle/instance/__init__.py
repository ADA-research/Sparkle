"""This package provides instance set support for Sparkle."""

from sparkle.instance.instances import (
    MultiFileInstanceSet,
    FileInstanceSet,
    IterableFileInstanceSet,
    InstanceSet,
)
from pathlib import Path


def Instance_Set(target: any) -> InstanceSet:
    """The combined interface for all instance set types."""
    if (
        isinstance(target, Path)
        and (target / MultiFileInstanceSet.instance_csv).exists()
    ) or (
        isinstance(target, list)
        and isinstance(target[0], Path)
        and (target[0].parent / MultiFileInstanceSet.instance_csv).exists()
    ):
        return MultiFileInstanceSet(target)
    elif (not target.exists()) and (
        target.parent / MultiFileInstanceSet.instance_csv
    ).exists():
        # Single instance
        return MultiFileInstanceSet(target)
    elif (
        isinstance(target, Path)
        and target.is_dir()
        and all(
            [
                p.suffix in IterableFileInstanceSet.supported_filetypes
                for p in target.iterdir()
            ]
        )
    ):
        return IterableFileInstanceSet(target)
    elif not target.exists():  # Resolve suffix
        alternatives = [p for p in target.parent.iterdir()]
        for alt in alternatives:
            if target.name == alt.stem:
                target = alt
                break
    return FileInstanceSet(target)
