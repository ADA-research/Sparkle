#!/usr/bin/env python3
"""Sparkle command to add a feature extractor to the Sparkle platform."""
import sys
import os
from pathlib import Path


def main() -> None:
    """Pass through command to launch CLI commands!"""
    if len(sys.argv) < 2:
        print("Usage: sparkle <command>")
        sys.exit(1)
    command = sys.argv[1]
    commandfile = Path(f"./CLI/{command}.py")
    if commandfile.is_file():
        os.system(f"{commandfile} {' '.join(sys.argv[2:])}")
    else:
        print(f"Does not understand command {command}")

    return


if __name__ == "__main__":
    main()
