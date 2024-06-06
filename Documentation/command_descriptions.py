#!/usr/bin/env python3
"""Automatic extraction of command list from their implementations."""

import os
from pathlib import Path

if __name__ == "__main__":
    command_dir = "../CLI"

    commands = []

    for file in os.listdir(command_dir):
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
        sphinx_file.write(
            f"""(cmd-{command.replace(".py", "").replace("_", "-")})=\n"""
            f"""\n```{{eval-rst}}\n"""
            f""".. autoprogram:: {command.replace(".py", "")}:parser_function()\n"""
            f"""   :prog: {command.replace(".py", "")}.py\n\n"""
            f"""```\n""")
        if not i == len(commands) - 1:
            sphinx_file.write("\n")
    sphinx_file.close()
