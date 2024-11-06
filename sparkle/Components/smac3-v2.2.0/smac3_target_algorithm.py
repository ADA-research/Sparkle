"""Target algorithm for SMAC3 to allow for Slurm scheduling."""
import sys
from pathlib import Path

from ConfigSpace import Configuration
import smac

from sparkle.solver import Solver


def solver_call(config: Configuration, seed: int) -> float:
    """Wrapper function to translate solver call to Solver call."""
    # TODO: config to config dict
    solver.run()
    return None


if __name__ == "__main__":
    # Incoming call from Sparkle:
    args = sys.argv[1:]
    global solver, instance
    solver = Solver(args[0])
    instance = Path(args[1])

    scenario = smac.Scenario()  # From File?
    # Facade Configurable or not?
    smac_facade = smac.HyperparameterOptimizationFacade(scenario, solver_call)
    incumbent = smac_facade.optimize()
