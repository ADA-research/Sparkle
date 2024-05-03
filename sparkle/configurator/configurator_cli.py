"""Configurator CLI wrapper class to standardise I/O of Configurators."""

import sys
import subprocess
from pathlib import Path
import implementations

if __name__ == "__main__":
    args = sys.argv[1:]
    configurator_name = args[1]
    output_source = Path(args[2])
    output_target = Path(args[3])
    configurator_call = args[4:]
    # 1. Resolve for which Configurator we are standardising
    configurator = implementations.resolve_configurator(configurator_name)

    # 2. Execute the call
    process = subprocess.run(configurator_call, capture_output=True)

    # 3. Standardise the output for Sparkle
    configurator.organise_output(output_source, output_target)
    