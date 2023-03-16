#!/usr/bin/env python3
"""Automatic extraction of command list from their implementations."""

import os
from pathlib import Path

if __name__ == "__main__":
    command_dir = "../Commands"

    commands = []

    for file in os.listdir(command_dir):
        filepath = Path(command_dir) / file
        if Path(filepath).is_file() and file[-3:] == ".py" and file[0] != "_":
            commands.append(file)

    commands = sorted(commands)

    sphinx_file = Path("source/userguide/commandlist.md").open("w")
    for command in commands:
        sphinx_file.write(
            "*  :ref:`cmd:{name}`\n".format(name=command.replace(".py", "")))
    sphinx_file.close()

    string = """
.. _cmd:{name}:

.. autoprogram:: {name}:parser_function()
   :prog: {name}.py

    """
    sphinx_file = Path("source/userguide/commandsautoprogram.md").open("w")
    for command in commands:
        sphinx_file.write(string.format(name=command.replace(".py", "")))
    sphinx_file.close()
