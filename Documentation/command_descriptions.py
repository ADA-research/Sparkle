#!/usr/bin/env python3
import os

if __name__ == "__main__":
    command_dir = "../Commands"

    commands = []

    for file in os.listdir(command_dir):
        filepath = os.path.join(command_dir, file)
        if os.path.isfile(filepath) and file[-3:] == ".py" and file[0] != "_":
            commands.append(file)

    commands = sorted(commands)

    sphinx_file = open("source/userguide/commandlist.rst", "w")
    for command in commands:
        sphinx_file.write("*  :ref:`cmd:{name}`\n".format(name=command.replace(".py", "")))
    sphinx_file.close()

    string = """
.. _cmd:{name}:

.. autoprogram:: {name}:parser_function()
   :prog: {name}.py

    """
    sphinx_file = open("source/userguide/commandsautoprogram.rst", "w")
    for command in commands:
        sphinx_file.write(string.format(name=command.replace(".py", "")))
    sphinx_file.close()