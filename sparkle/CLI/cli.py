#!/usr/bin/env python3
"""Sparkle CLI entry point."""
import sys
import os
from pathlib import Path


def main() -> None:
    """Pass through command to launch CLI commands."""
    module_path = Path(__file__).parent.resolve()
    max_space = max([path.name.count("_") for path in module_path.iterdir()
                     if path.is_file()])
    if len(sys.argv) < 2:
        print("Usage: sparkle <command>")
        sys.exit(1)
    # Support spaces instead of _
    for i in range(1, min(max_space, len(sys.argv))):
        command = "_".join(sys.argv[1:i + 1])
        args = sys.argv[i + 1:]
        command_file = module_path / f"{command}.py"
        if command_file.is_file():
            break
    if command_file.is_file():
        if not os.access(command_file, os.X_OK):  # Pip installation changes exec rights
            command_file.chmod(0o755)
        os.system(f"{command_file} {' '.join(args)}")
    else:
        print(f"Does not understand command {command}")


if __name__ == "__main__":
    main()
