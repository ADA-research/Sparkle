#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""General Wrapper class to use different executables for programs."""

from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import time


class Wrapper:
    """General Sparkle Wrapper."""
    # Good options it should/needs to have:
    # Return solver output (can be raw)
    # Return results for a configurator
    # Call with given parameter settings
    # Be able to return the name of the solver executable (to check for execution rights)

    def __init__(self: Wrapper, executable_path: Path) -> None:
        """Initialize the Wrapper."""
        self.executable = executable_path
        self.output = None
        self.raw_output = None
        self.err_output = None
        self.parser = argparse.ArgumentParser()
        self.args = []
        self.seed = 42
        return

    def get_arguments(self: Wrapper) -> None:
        """Gets arguments."""
        # Has the argparse logic and performs checks on them
        # Returns an args object that has:
        # args.instance # path to instance or string
        # args.seed # integer
        # args.budget # dictionary with different cutoff (Walltime, CPUtime, qualitative)
        # args.configuration # dictionary: {"param": 0, "param2": "a"}
        return

    def parse_output(self: Wrapper, output: str) -> None:
        """Parses output."""
        return

    def run_executable(self: Wrapper) -> float:
        """Runs the wrapped executable."""
        # Should we do this with runrunner?
        start_time = time.time()
        p = subprocess.run([self.executable] + self.args,  # Correct?
                           stdout=self.raw_output,
                           stderr=self.err_output)
        print(p)
        run_time = time.time() - start_time

        return run_time


class SmacWrapper(Wrapper):
    """Sparkle Smac Wrapper.

    A specific implementation to configure an executable with SMAC.
    """

    def __init__(self: SmacWrapper, executable_path: Path) -> None:
        """Docstring."""
        return
