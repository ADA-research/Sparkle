"""Configurator CLI wrapper class to standardise I/O of Configurators."""

import sys
import subprocess

from configurator import Configurator

if __name__ == "__main__":
    args = sys.argv[1:]
    configurator_name = args[1]
    configurator_call = args[2:]
    # 1. Resolve for which Configurator we are standardising
    configurator = Configurator.resolve_subclass(configurator_name)

    # 2. Execute the call
    process = subprocess.run(configurator_call, capture_output=True)

    # 3. Standardise the output for Sparkle
    configurator.organise_output()
    