#!/usr/bin/env python3
"""Sparkle CLI entry point."""

import sys
import os
from pathlib import Path

module_path = Path(__file__).parent.resolve()

package_cli_entry_points = [
    module_path.parent / "solver" / "solver_cli.py",
    module_path.parent / "selector" / "selector_cli.py",
    module_path.parent / "selector" / "extractor_cli.py",
    module_path.parent / "configurator" / "configurator_cli.py",
]


def commands() -> list[str]:
    """Get list of available commands."""
    module_path = Path(__file__).parent.resolve()
    self_name = Path(__file__).name
    return [
        path.stem
        for path in module_path.iterdir()
        if path.is_file()
        and path.suffix == ".py"
        and path.name != self_name
        and path.name != "__init__.py"
    ]


def main() -> None:
    """Pass through command to launch CLI commands."""
    max_space = max(
        [path.name.count("_") for path in module_path.iterdir() if path.is_file()]
    )
    if len(sys.argv) < 2:
        print("Usage: sparkle <command>")
        sys.exit(1)
    if " ".join(sys.argv[1:]) == "install autocomplete":
        import urllib.request

        print(sys.prefix)
        if sys.prefix == sys.base_prefix:
            print(
                "Sparkle is not installed in a virtual environment! "
                "Autocomplete must be installed manually, see the documentation."
            )
            sys.exit(-1)
        # TODO: Update this URL to link to the file on main
        code_inject = (
            urllib.request.urlopen(
                "https://raw.githubusercontent.com/ADA-research/Sparkle/refs/heads/development/Resources/Other/venv_autocomplete.sh"
            )
            .read()
            .decode()
        )
        venv_profile_path = Path(sys.prefix) / "bin" / "activate"
        if venv_profile_path.is_file():
            if code_inject in venv_profile_path.read_text():
                print(
                    f"[{Path(sys.prefix).name}] Sparkle autocomplete is already installed in the virtual environment! Exit."
                )
                sys.exit(-1)
            with venv_profile_path.open("a") as f:
                f.write(code_inject)
            print(
                f"[{Path(sys.prefix).name}] Sparkle autocomplete has been installed in the virtual environment!"
            )
            sys.exit(0)
        print(
            "Virtual environment not found! Manual installation in activation script required, see the documentation."
        )
        sys.exit(-1)
    # Support spaces instead of _
    possible_commands = commands()
    command, command_file = "", Path()
    for i in range(1, min(max_space, len(sys.argv))):
        if "--" in sys.argv[i]:  # Parameter is never part of the command
            break
        command = "_".join(sys.argv[1 : i + 1])
        args = sys.argv[i + 1 :]
        command_file = module_path / f"{command}.py"
        if command in possible_commands:
            break

    if command_file.is_file():
        os.system(f"python3 {command_file} {' '.join(args)}")
        sys.exit(0)
    else:
        print(f"Sparkle does not understand command <{command}>", end="")
        from difflib import SequenceMatcher

        similarities = [
            SequenceMatcher(None, command, alt).ratio() for alt in possible_commands
        ]

        if max(similarities) > 0.6:
            alternative = possible_commands[similarities.index(max(similarities))]
            print(f". Did you mean <{alternative}>?")
            sys.exit(-2)

        sys.exit(-1)


if __name__ == "__main__":
    main()
