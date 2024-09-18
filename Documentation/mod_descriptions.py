#!/usr/bin/env python3
"""Automatic extraction of library list from their implementations."""
from pathlib import Path
import re
import sparkle
import inspect

if __name__ == "__main__":
    special_module = re.compile("^__.*__$")
    submodules = [(name, obj) for name, obj in inspect.getmembers(sparkle)
                  if re.match(special_module, name) is None]
    sphinx_list = []
    sphinx_blocs = []
    for module_name, obj in submodules:
        module_methods = [method_name for method_name, _ in 
                          inspect.getmembers(obj, inspect.isfunction)]
        module_classes = [class_name for class_name, class_obj in 
                          inspect.getmembers(obj, inspect.isclass)
                          if class_obj.__module__.startswith(sparkle.__name__)]
        listed_members = ",".join(module_methods + module_classes)
        sphinx_list.append("- {ref}`mod-" + f"{module_name}`\n")
        sphinx_blocs.append(
            f"(mod-{module_name})=\n"
            "```{eval-rst}\n"
            f"{module_name}\n"
            "===============\n"
            f".. automodule:: sparkle.{module_name}\n"
            f"    :members: {listed_members}\n"
            "```\n")

    with Path("source/packagegen.md").open("w") as sphinx_file:
        sphinx_file.write("\n".join(sphinx_blocs))
