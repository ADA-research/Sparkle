#!/usr/bin/env python3
"""Sparkle CLI entry point."""
import sys
import os
from pathlib import Path

module_path = Path(__file__).parent.resolve()

package_cli_entry_points = [
    module_path / "core" / "compute_features.py",
    module_path / "core" / "run_portfolio_selector_core.py",
    module_path.parent / "solver" / "solver_cli.py",
    module_path.parent / "configurator" / "configurator_cli.py",
]


def commands() -> list[str]:
    """Get list of available commands."""
    module_path = Path(__file__).parent.resolve()
    self_name = Path(__file__).name
    return [path.stem for path in module_path.iterdir()
            if path.is_file() and path.suffix == ".py" and path.name != self_name]


def main() -> None:
    """Pass through command to launch CLI commands."""
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
        os.system(f"python3 {command_file} {' '.join(args)}")
    elif command_file.with_suffix(".sh").is_file():
        script_path = command_file.with_suffix(".sh")
        script_path.chmod(0o755)  # Ensure execution rights with shipment
        os.system(f"source {script_path}")
        print("Autocompletion activated")
    else:
        print(f"Sparkle does not understand command <{command}>")


if __name__ == "__main__":
    main()
