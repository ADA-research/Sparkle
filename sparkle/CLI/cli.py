#!/usr/bin/env python3
"""Sparkle CLI entry point."""
import sys
import os
from pathlib import Path


def commands() -> list[str]:
    """Get list of available commands."""
    module_path = Path(__file__).parent.resolve()
    self_name = Path(__file__).name
    return [path.stem for path in module_path.iterdir()
            if path.is_file() and path.suffix == ".py" and path.name != self_name]


def main() -> None:
    """Pass through command to launch CLI commands."""
    module_path = Path(__file__).parent.resolve()
    max_space = max([path.name.count("_") for path in module_path.iterdir()
                     if path.is_file()])
    if len(sys.argv) < 2:
        print("Usage: sparkle <command>")
        sys.exit(1)
    # Support spaces instead of _
    possible_commands = commands()
    for i in range(1, min(max_space, len(sys.argv))):
        command = "_".join(sys.argv[1:i + 1])
        args = sys.argv[i + 1:]
        command_file = module_path / f"{command}.py"
        if command in possible_commands:
            break
    if command_file.is_file():
        if not os.access(command_file, os.X_OK):  # Pip installation changes exec rights
            command_file.chmod(0o755)
        os.system(f"{command_file} {' '.join(args)}")
    else:
        print(f"Does not understand command {command}")


if __name__ == "__main__":
    main()
