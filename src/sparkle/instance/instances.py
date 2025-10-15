"""Objects and methods relating to instances for Sparkle."""

from __future__ import annotations
from pathlib import Path

import csv
import numpy as np


class InstanceSet:
    """Base object representation of a set of instances."""

    def __init__(self: InstanceSet, target: Path | list[str, Path]) -> None:
        """Initialise an Instances object from a directory.

        Args:
            target: The Path, or list of paths to create the instance set from.
        """
        self.directory: Path = target
        self._instance_names: list[str] = []
        self._instance_paths: list[Path] = []

    @property
    def size(self: InstanceSet) -> int:
        """Returns the number of instances in the set."""
        return len(self._instance_paths)

    @property
    def all_paths(self: InstanceSet) -> list[Path]:
        """Returns all file paths in the instance set as a flat list."""
        return self._instance_paths

    @property
    def instance_paths(self: InstanceSet) -> list[Path]:
        """Get processed instance paths."""
        return self._instance_paths

    @property
    def instance_names(self: InstanceSet) -> list[str]:
        """Get processed instance names for instances."""
        return self._instance_names

    @property
    def instances(self: InstanceSet) -> list[str]:
        """Get instance names with relative path."""
        return [str(p.with_suffix("")) for p in self._instance_paths]

    @property
    def name(self: InstanceSet) -> str:
        """Get instance set name."""
        return self.directory.name

    def __str__(self: InstanceSet) -> str:
        """Get the string representation of an Instance Set."""
        return self.name

    def __repr__(self: InstanceSet) -> str:
        """Get detailed representation of an Instance Set."""
        return (
            f"{self.name}:\n"
            f"\t- Type: {type(self).__name__}\n"
            f"\t- Directory: {self.directory}\n"
            f"\t- # Instances: {self.size}"
        )

    def get_path_by_name(self: InstanceSet, name: str) -> Path | list[Path]:
        """Retrieves an instance paths by its name. Returns None upon failure."""
        for idx, instance_name in enumerate(self._instance_names):
            if instance_name == name:
                return self._instance_paths[idx]
        return None


class FileInstanceSet(InstanceSet):
    """Object representation of a set of single-file instances."""

    def __init__(self: FileInstanceSet, target: Path) -> None:
        """Initialise an InstanceSet, where each instance is a file in the directory.

        Args:
            target: Path to the instances directory. If multiple files are found,
                they are assumed to have the same number of instances per file.
        """
        super().__init__(target)
        self._name: str = target.stem
        if target.is_file():
            # Single instance set
            self._instance_paths = [target]
            self._instance_names = [target.stem]
            self.directory = target.parent
        else:
            # Default situation, treat each file in the directory as an instance
            self._instance_paths = [p for p in self.directory.iterdir()]
            self._instance_names = [p.stem for p in self._instance_paths]

    @property
    def name(self: FileInstanceSet) -> str:
        """Get instance set name."""
        return self._name


class MultiFileInstanceSet(InstanceSet):
    """Object representation of a set of multi-file instances."""

    instance_csv = "instances.csv"

    def __init__(self: MultiFileInstanceSet, target: Path) -> None:
        """Initialise an Instances object from a directory.

        Args:
            target: Path to the instances directory. Will read from instances.csv.
        """
        target_dir = target.parent if not target.is_dir() else target
        super().__init__(target_dir)
        # A path pointing to the directory of instances
        self.instance_file = self.directory / MultiFileInstanceSet.instance_csv
        # Read from instance_file
        if not target.is_dir():
            # Single file
            instance_list = [
                line
                for line in csv.reader(self.instance_file.open())
                if target.stem in line
            ]
        else:
            # Multi file
            instance_list = [line for line in csv.reader(self.instance_file.open())]

        for instance in instance_list:
            self._instance_names.append(instance[0])
            self._instance_paths.append(
                [(self.directory / f) if isinstance(f, str) else f for f in instance[1:]]
            )

    @property
    def all_paths(self: MultiFileInstanceSet) -> list[Path]:
        """Returns all file paths in the instance set as a flat list."""
        return [p for instance in self._instance_paths for p in instance] + [
            self.instance_file
        ]

    @property
    def instances(self: InstanceSet) -> list[str]:
        """Get instance names with relative path for multi-file instances."""
        return [self.directory / inst_name for inst_name in self.instance_names]


class IterableFileInstanceSet(InstanceSet):
    """Object representation of files containing multiple instances."""

    supported_filetypes = set([".csv", ".npy"])

    def __init__(self: IterableFileInstanceSet, target: Path) -> None:
        """Initialise an InstanceSet from a single file.

        Args:
            target: Path to the instances directory. If multiple files are found,
                they are assumed to have the same number of instances.
        """
        super().__init__(target)
        self._instance_paths = [
            p
            for p in self.directory.iterdir()
            if p.suffix in IterableFileInstanceSet.supported_filetypes
        ]
        self._size = IterableFileInstanceSet.__determine_size__(self._instance_paths[0])
        self._instance_names = [p.name for p in self._instance_paths]

    @property
    def size(self: IterableFileInstanceSet) -> int:
        """Returns the number of instances in the set."""
        return self._size

    @staticmethod
    def __determine_size__(file: Path) -> int:
        """Determine the number of instances in a file."""
        match file.suffix:
            case ".csv":
                return len(file.open().readlines())
            case ".npy":
                return len(np.load(file))
