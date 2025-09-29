#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to log which output was created by Sparkle where."""

from __future__ import annotations
import time
from pathlib import Path

from runrunner.logger import Log as RunRunnerLog

from sparkle.platform import Settings


# Keep track of which command called Sparkle
global caller
caller: str = "unknown"

# Current caller file path
global caller_log_path
caller_log_path: Path = "not set"

# Root output directory for the calling command in the form of
# Output/<timestamp>_<command_name>/
global caller_out_dir
caller_out_dir: Path = Path(".")

# Log directory for the calling command in the form of
# Output/<timestamp>_<command_name>/Log/
global caller_log_dir
caller_log_dir: Path = Path(".")


def _update_caller(argv: list[str]) -> None:
    """Update which command is currently active.

    Args:
        argv: List containing the command line arguments derived from sys.argv.

    """
    global caller
    caller = Path(argv[0]).stem


def _update_caller_file_path(timestamp: str) -> None:
    """Create a new file path for the caller with the given timestamp.

    Args:
        timestamp: String representation of the time.

    """
    caller_file = caller + "_main_log.txt"
    caller_dir = Path(caller + "_" + timestamp)
    log_dir = Settings.DEFAULT_log_output
    # Set caller directory for other Sparkle functions to use
    global caller_out_dir
    caller_out_dir = Path(caller_dir)
    global caller_log_path
    caller_log_path = Path(log_dir / caller_out_dir / caller_file)
    global caller_log_dir
    caller_log_dir = log_dir / caller_out_dir

    # Create needed directories if they don't exist
    caller_dir = caller_log_path.parents[0]
    caller_dir.mkdir(parents=True, exist_ok=True)
    caller_log_dir.mkdir(parents=True, exist_ok=True)

    # If the caller output file does not exist yet, write the header
    if not caller_log_path.is_file():
        output_header = "\t Timestamp\t\t\t\t\t\t\t  Path\t\t\t\t\t\t\t Description\n"
        with caller_log_path.open("a") as output_file:
            output_file.write(output_header)


def add_output(output_path: str, description: str) -> None:
    """Add output location and description to the log of the current command.

    Args:
        output_path: The file path of where output is written to.
        description: A short description of what kind of output is written to this file.

    """
    # Prepare logging information
    timestamp = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime(time.time()))
    output_str = f"{timestamp}\t{output_path}\t{description}\n"
    # Write output path and description to caller file
    with caller_log_path.open("a") as output_file:
        output_file.write(output_str)


def log_command(argv: list[str], seed: int = None) -> None:
    """Write to file which command was executed.

    Includes information on when it was executed, with which arguments, and
    where details about it's output are stored (if any).

    Args:
        argv: List containing the command line arguments derived from sys.argv.
        seed: Optionally, the seed that corresponds to the set random state.
    """
    # Determine caller
    _update_caller(argv)

    # Prepare logging information
    timestamp = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime(time.time()))
    _update_caller_file_path(timestamp)
    args = " ".join(argv)
    log_str = f"{timestamp}   {args}   {str(caller_log_path)}"
    log_str += "\n" if seed is None else f"   {seed}\n"

    # If the log file does not exist yet, write the header
    log_path = Settings.DEFAULT_output / "sparkle.log"
    if not log_path.is_file():
        log_header = "\t Timestamp\t\t\t\t\t\t\t  Command\t\t\t\t\t\t\t Output details\t\t\t\t\t\t\t  Seed\n"
        log_str = log_header + log_str

    # Write to log file
    with log_path.open("a") as log_file:
        log_file.write(log_str)

    # Pipe RunRunner log to the caller log
    RunRunnerLog.set_log_file(caller_log_path)
