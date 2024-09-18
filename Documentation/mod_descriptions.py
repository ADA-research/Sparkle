#!/usr/bin/env python3
"""Automatic extraction of library list from their implementations."""
from pathlib import Path
import re
import sparkle

if __name__ == "__main__":
    special_module = re.compile("^__.*__$")
    submodules = sorted([module for module in dir(sparkle) if re.match(special_module, module) is None])
    sphinx_list = []
    sphinx_blocs = []
    for module in submodules:
        sphinx_list.append("- {ref}`mod-" + module + "`\n")
        sphinx_blocs.append(
            f"(mod-{module})=\n"
            "```{eval-rst}\n"
            f"{module}\n"
            "===============\n"
            f".. automodule:: sparkle.{module}\n"
            "    :members:\n"
            "    :imported-members:\n"
            "```\n")

    with Path("source/packagegen.md").open("w") as sphinx_file:
        sphinx_file.write("".join(sphinx_list))
        sphinx_file.write("\n")
        sphinx_file.write("\n".join(sphinx_blocs))
