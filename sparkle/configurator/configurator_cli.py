"""Configurator CLI wrapper class to standardise I/O of Configurators."""

import sys
import subprocess
from pathlib import Path
import implementations

if __name__ == "__main__":
    args = sys.argv
    configurator_name = args[1]
    output_source = Path(args[2])
    output_target = Path(args[3])
    configurator_call = args[4:]
    # 1. Resolve for which Configurator we are standardising
    configurator = implementations.resolve_configurator(configurator_name)
    # 2. Execute the call, output is automatically piped to the caller's set output
    subprocess.run(configurator_call)
    # 3. Standardise the output for Sparkle
    # 3a. Make sure the output file exists
    output_target.open("a").close()
    # 3b. Have the configurator implementation organise the output
    configurator.organise_output(output_source=output_source,
                                 output_target=output_target)
    print(f"Organising done! See {output_target}")
