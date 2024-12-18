#!/usr/bin/env python3
"""Sparkle command to save the current Sparkle platform in a .zip file."""
import sys

from sparkle.CLI.help import snapshot_help
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
import argparse


def parser_function() -> argparse.ArgumentParser:
    """Parser for save_snapshot."""
    parser = argparse.ArgumentParser(
        description="Save the current platform in a .zip file.",
        epilog="Can be loaded later with the load snapshot command.")
    parser.add_argument(*ac.SnapshotNameArgument.names,
                        **ac.SnapshotNameArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the command."""
    # Log command call
    sl.log_command(sys.argv)
    parser = parser_function()
    args = parser.parse_args(argv)
    snapshot_help.save_current_platform(args.name)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
