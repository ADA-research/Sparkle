#!/usr/bin/env python3
"""Sparkle CLI pass through."""
import sys
import os
from pathlib import Path


def main() -> None:
    """Pass through command to launch CLI commands."""
    if len(sys.argv) < 2:
        print("Usage: sparkle <command>")
        sys.exit(1)
    module_path = Path(__file__).parent.resolve()
    command = sys.argv[1]
    command_file = module_path / "CLI" / f"{command}.py"
    if command_file.is_file():
        os.system(f"{command_file} {' '.join(sys.argv[2:])}")
    else:
        print(f"Does not understand command {command}")


if __name__ == "__main__":
    main()
