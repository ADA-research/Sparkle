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


def resolve_instance_pair(
    instance_path: Path | list[Path],
) -> tuple[str, str] | list[tuple[str, str]]:
    """Resolve instance file path(s) to their canonical (set_name, instance_name) pairs.

    The inverse of resolve_instance_name, which maps a (set, instance) back to its path.

    The data frames are keyed by the pair, but the CLIs that write to them only receive
    file paths. The instance name cannot be derived from the path, because each
    InstanceSet subclass names its instances differently (FileInstanceSet uses the
    stem, IterableFileInstanceSet the full name with suffix, and MultiFileInstanceSet
    reads them from its instances.csv). Rather than guess, reconstruct the owning set
    from the parent directory and look each pair up by path, so the subclass supplies
    its own naming convention.

    Args:
        instance_path: A single instance file path, or a list of paths. Each path is
            resolved independently to its own pair.

    Returns:
        For a single Path, the (set_name, instance_name) pair. For a list of paths, the
        list of pairs, one per path, in the same order as the input. A pair falls back to
        (parent directory name, file stem) when the path matches no instance.
    """
    single = isinstance(instance_path, Path)
    instance_paths = [instance_path] if single else instance_path
    instance_pairs = []
    for path in instance_paths:
        target = path.resolve()
        # Instance_Set() picks the same subclass (file / iterable / multi-file) that was
        # used originally, so its instance_pairs carry the exact stored naming convention.
        instance_set = Instance_Set(path.parent)
        resolved_pair = next(
            (
                pair
                for pair, pair_path in zip(
                    instance_set.instance_pairs, instance_set.instance_paths
                )
                # pair_path may be a list (multi-file instance), so normalise to a list.
                if target
                in [
                    file.resolve()
                    for file in (
                        pair_path if isinstance(pair_path, list) else [pair_path]
                    )
                ]
            ),
            (path.parent.name, path.stem),
        )
        instance_pairs.append(resolved_pair)
    # A single Path in yields its pair directly, a list yields a pair per path.
    return instance_pairs[0] if single else instance_pairs
