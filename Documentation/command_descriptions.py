#!/usr/bin/env python3
"""Automatic extraction of command list from their implementations."""

import os
from pathlib import Path

if __name__ == "__main__":
    command_dir = "../sparkle/CLI"

    commands = []

    for file in os.listdir(command_dir):
        if file == "cli.py":
            continue
        filepath = Path(command_dir) / file
        if Path(filepath).is_file() and file[-3:] == ".py" and file[0] != "_":
            commands.append(file)

    commands = sorted(commands)

    sphinx_file = Path("source/userguide/commandlist.md").open("w")
    for command in commands:
        sphinx_file.write(
            f"- {{ref}}`cmd-{command.replace('.py', '').replace('_', '-')}`\n")
    sphinx_file.close()

    sphinx_file = Path("source/userguide/commandsautoprogram.md").open("w")
    for i, command in enumerate(commands):
        c_name = command.replace(".py", "")
        sphinx_file.write(
            f"""(cmd-{c_name.replace("_", "-")})=\n"""
            f"""\n```{{eval-rst}}\n"""
            f""".. autoprogram:: sparkle.CLI.{c_name}:parser_function()\n"""
            f"""   :prog: {c_name}.py\n\n"""
            f"""```\n""")
        if not i == len(commands) - 1:
            sphinx_file.write("\n")
    sphinx_file.close()
