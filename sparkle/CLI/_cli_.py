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
        if "--" in sys.argv[i]:  # Parameter is never part of the command
            break
        command = "_".join(sys.argv[1:i + 1])
        args = sys.argv[i + 1:]
        command_file = module_path / f"{command}.py"
        if command in possible_commands:
            break

    if command_file.is_file():
        os.system(f"python3 {command_file} {' '.join(args)}")
    elif command == "install_autocomplete":
        script_path = module_path / "autocomplete.sh"
        bash_profile = Path.home() / ".bash_profile"
        if not bash_profile.exists():
            bash_profile.open("w+").close()
        bash_profile.open("a").write(
            "\n#----- Sparkle AutoComplete ----\n"
            f"source {script_path.absolute()}"
            "\n#----- Sparkle AutoComplete ----\n")
        print(f"Sparkle autocomplete installed! To enable, run `source {bash_profile}` "
              "or restart your terminal.")
    else:
        print(f"Sparkle does not understand command <{command}>", end="")
        from difflib import SequenceMatcher
        similarities = [SequenceMatcher(None, command, alt).ratio()
                        for alt in possible_commands]

        if max(similarities) > 0.6:
            alternative = possible_commands[similarities.index(max(similarities))]
            print(f". Did you mean <{alternative}>?")
        else:
            print()


if __name__ == "__main__":
    main()
