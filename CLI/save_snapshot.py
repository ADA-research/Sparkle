#!/usr/bin/env python3
"""Sparkle command to save the current Sparkle platform in a .zip file."""
import sys

from sparkle.platform import snapshot_help
import sparkle_logging as sl
import argparse


def parser_function() -> argparse.ArgumentParser:
    """Parser for save_snapshot."""
    return argparse.ArgumentParser()


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)
    snapshot_help.save_current_sparkle_platform()
