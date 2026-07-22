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


def resolve_instance_name(
    instance_set: str,
    instance_name: str,
    search_location: str | Path | list[InstanceSet],
) -> str | Path | list[Path] | None:
    """Attempts to resolve an instance to its file path(s).

    The inverse of resolve_instance_pair, which maps a path back to its (set, instance).

    Args:
        instance_set: The name of the set the instance belongs to. Used to look in the
            correct set, so instances sharing a name across different sets are not
            confused with one another.
        instance_name: The name of the instance to resolve.
        search_location: Where to look for the instance. Either a str/Path to a
            directory containing instance sets, or the instance sets themselves as
            a list.

    Returns:
        The Path of the instance, or None if it cannot be resolved. Multi-file instances
        are returned as a space-joined string of their paths, as they are passed on to
        a command line as a single argument.
    """
    # Check if the name is already an instance file path
    name_path = Path(instance_name)
    if name_path.exists() and name_path.is_file():
        return name_path
    # Attempt to find files
    matches = [path for path in name_path.parent.glob(name_path.name + ".*")]
    if matches:
        return " ".join(str(path) for path in matches)  # Concat for multi file instance
    # Normalise search_location into a list of InstanceSet objects. A str/Path points to
    # a directory that contains instance set directories.
    if isinstance(search_location, (str, Path)):
        instance_sets = [
            Instance_Set(instance_dir)
            for instance_dir in Path(search_location).iterdir()
            if instance_dir.is_dir()
        ]
    else:
        instance_sets = search_location
    # We know which set the instance belongs to: restrict the search to that set so a
    # shared instance name in another set cannot shadow it. Fall back to all sets if the
    # named set is not among those given.
    matching_sets = [
        inst_set for inst_set in instance_sets if inst_set.name == instance_set
    ]
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


def resolve_instance_pair(instance_path: Path | list[Path]) -> tuple[str, str]:
    """Resolve an instance file path to its canonical (set_name, instance_name) pair.

    The inverse of resolve_instance_name, which maps a (set, instance) back to its path.

    The data frames are keyed by the pair, but the CLIs that write to them only receive
    a file path. The instance name cannot be derived from the path, because each
    InstanceSet subclass names its instances differently (FileInstanceSet uses the
    stem, IterableFileInstanceSet the full name with suffix, and MultiFileInstanceSet
    reads them from its instances.csv). Rather than guess, reconstruct the owning set
    from the parent directory and look the pair up by path, so the subclass supplies
    its own naming convention.

    Args:
        instance_path: Path to the instance file, or the list of files that make up a
            single multi-file instance.

    Returns:
        The (set_name, instance_name) pair as it is stored in the data frames. Falls
        back to (parent directory name, file stem) if the path matches no instance.
    """
    first_path = instance_path[0] if isinstance(instance_path, list) else instance_path
    target = first_path.resolve()
    # Instance_Set() picks the same subclass (file / iterable / multi-file) that was
    # used originally, so its instance_pairs carry the exact stored naming convention.
    instance_set = Instance_Set(first_path.parent)
    return next(
        (
            pair
            for pair, pair_path in zip(
                instance_set.instance_pairs, instance_set.instance_paths
            )
            # pair_path may be a list (multi-file instance), so normalise to a list.
            if target
            in [
                path.resolve()
                for path in (pair_path if isinstance(pair_path, list) else [pair_path])
            ]
        ),
        (first_path.parent.name, first_path.stem),
    )
