"""Target algorithm for SMAC3 to allow for Slurm scheduling."""
import sys
from pathlib import Path

from ConfigSpace import Configuration
from sparkle.configurator.implementations import SMAC3, SMAC3Scenario


def smac3_solver_call(config: Configuration, instance: str, seed: int) -> list[float]:
    """Wrapper function to translate solver call to Solver call."""
    # TODO: config to config dict
    output = solver.run(
        instance,  # Correct?
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
    scenario = SMAC3Scenario.from_file(Path(args[0]))  # From File?
    global solver, objectives, cutoff
    solver = scenario.solver
    cutoff = scenario.cutoff_time
    objectives = scenario.sparkle_objectives

    # Facade Configurable
    smac_facade = scenario.smac_facade(scenario.smac3_scenario, smac3_solver_call)
    incumbent = smac_facade.optimize()
    SMAC3.organise_output(scenario.results_directory, scenario.directory)
