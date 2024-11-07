"""Target algorithm for SMAC3 to allow for Slurm scheduling."""
import sys
from pathlib import Path

from ConfigSpace import Configuration
# import smac

# from sparkle.solver import Solver
# from sparkle.instance import Instance
from sparkle.configurator.implementations import SMAC3Scenario


def smac3_solver_call(config: Configuration, seed: int) -> list[float]:
    """Wrapper function to translate solver call to Solver call."""
    # TODO: config to config dict
    output = solver.run(
        instance_set,  # Correct? Or does the call tell us which one?
        objectives,
        seed,
        cutoff_time=cutoff,
        configuration=dict(config),  # Does this need corrections?
        commandname=f"SMAC3 configuration evaluation {config.config_id}"
    )
    return [float(output[objective.name]) for objective in objectives]


if __name__ == "__main__":
    # Incoming call from Sparkle:
    args = sys.argv[1:]
    scenario = SMAC3Scenario(Path(args[0]))  # From File?
    global solver, instance_set, objectives, cutoff
    solver = scenario.solver
    instance_set = scenario.instance_set
    cutoff = scenario.cutoff_time
    objectives = scenario.objectives

    # Facade Configurable or not?
    smac_facade = scenario.facade(scenario, smac3_solver_call)
    incumbent = smac_facade.optimize()
