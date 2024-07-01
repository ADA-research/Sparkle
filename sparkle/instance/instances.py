"""Objects and methods relating to instances for Sparkle."""
from __future__ import annotations
from pathlib import Path
import csv


class Instances:
    """Object representation of instances."""
    instance_list = "instance_list.csv"

    def __init__(self: Instances, directory: Path) -> None:
        """Initialise an Instances object from a directory."""
        self.directory = directory
        self.multi_file = False
        self.instance_names = []
        self.instance_paths = []

        if (self.directory / Instances.instance_list).exists():
            # Dealing with multiple files per instance
            self.multi_file = True
            # A multi instance file describes per line: InstanceName, File1, File2, ...
            # where each file is present in the self.directory
            for line in csv.reader((self.directory / Instances.instance_list).open()):
                self.instance_names.append(line[0])
                self.instance_paths.append((self.directory / file) for file
                                           in line[1:])
        else:
            self.instance_paths = [self.directory / p for p in self.directory.iterdir()]
            self.instance_names = [p.name for p in self.instance_paths]
        return
