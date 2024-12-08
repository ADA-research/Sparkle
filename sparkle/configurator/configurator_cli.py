#!/usr/bin/env python3
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
    scenario = Path(args[4])
    run_id = int(args[5])
    configurator_call = args[6:]
    # 1. Resolve for which Configurator we are standardising
    configurator = implementations.resolve_configurator(configurator_name)
    scenario = configurator.scenario_class().from_file(scenario)
    # 2. Execute the call, output is automatically piped to the caller's set output
    subprocess.run(configurator_call)
    # 3. Have the configurator implementation organise the output, standardised
    configurator.organise_output(output_source=output_source,
                                 output_target=output_target,
                                 scenario=scenario,
                                 run_id=run_id)
    print(f"Organising done! See {output_target} for results.")
