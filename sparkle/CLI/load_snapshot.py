#!/usr/bin/env python3
"""Sparkle command to load a Sparkle platform from a .zip file."""
import sys
import argparse
from pathlib import Path

from sparkle.CLI.help import snapshot_help
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(description="Load a platform from a zip file.")
    parser.add_argument(*ac.SnapshotArgument.names,
                        **ac.SnapshotArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the command."""
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args(argv)
    snapshot_help.load_snapshot(Path(args.snapshot_file_path))
    # Make sure we have Solver execution rights again after unpacking
    for solver in gv.settings().DEFAULT_solver_dir.iterdir():
        if solver.is_dir():
            for file in solver.iterdir():
                if file.is_file():
                    file.chmod(0o755)
    # Reset Global variables as they should be re-read from snapshot
    gv.__settings = None
    gv.__latest_scenario = None
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
