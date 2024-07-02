"""Objects and methods relating to instances for Sparkle."""
from __future__ import annotations
from pathlib import Path
import csv


class InstanceSet:
    """Object representation of a set of instances."""
    instance_csv = "instances.csv"

    def __init__(self: InstanceSet, directory: Path) -> None:
        """Initialise an Instances object from a directory.

        Args:
            directory: Path to the instances directory. If it contains an instance list
                for multi file instances, will read from instance_list.csv. If the path
                is a file, will create an Instance set of size one.
        """
        self.directory = directory
        self.name = directory.name
        self.multi_file = False
        self.instance_names = []
        self.instance_paths = []

        if self.directory.is_file():
            # Single instance set
            self.instance_paths = [self.directory]
            self.instance_names = [self.directory.name]
            self.directory = self.directory.parent
        elif (self.directory / InstanceSet.instance_csv).exists():
            # Dealing with multiple files per instance
            self.multi_file = True
            # A multi instance file describes per line: InstanceName, File1, File2, ...
            # where each file is present in the self.directory
            for line in csv.reader((self.directory / InstanceSet.instance_csv).open()):
                self.instance_names.append(line[0])
                self.instance_paths.append([(self.directory / f) for f in line[1:]])
        else:
            # Default situation, treat each file in the directory as an instance
            self.instance_paths = [p for p in self.directory.iterdir()]
            self.instance_names = [p.name for p in self.instance_paths]

    @property
    def size(self: InstanceSet) -> int:
        """Returns the number of instances in the set."""
        return len(self.instance_paths)

    @property
    def all_paths(self: InstanceSet) -> list[Path]:
        """Returns all file paths in the instance set as a flat list."""
        if self.multi_file:
            return [p for instance in self.instance_paths for p  in instance] + [
                self.directory / InstanceSet.instance_csv]
        return self.instance_paths
