"""Target algorithm for SMAC3 to allow for Slurm scheduling."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Callable
import copy
import inspect
import math
import traceback
from functools import partial

import numpy as np
from ConfigSpace import Configuration
from smac.runner.abstract_runner import StatusType
from smac.runner.abstract_serial_runner import AbstractSerialRunner
from smac.scenario import Scenario

from sparkle.configurator.implementations import SMAC3, SMAC3Scenario


def smac3_solver_call(config: Configuration, instance: str, seed: int) -> list[float]:
    """Wrapper function."""
    return solver.run(
        instance,
        objectives,
        seed,
        cutoff_time=cutoff,
        configuration=dict(config),
        log_dir=log_dir
    )


class SparkleTargetFunctionRunner(AbstractSerialRunner):
    """Sparkle override class to execute target functions which are python functions.

    Evaluates Solver for given configuration and resource limit.

    Parameters
    ----------
    target_function: Callable
        The target function. Set to default to smac3_solver_call.
    scenario: Scenario
    required_arguments: list[str], defaults to []
        A list of required arguments, which are passed to the target function.
    """

    def __init__(
            self: SparkleTargetFunctionRunner,
            scenario: Scenario,
            target_function: Callable = smac3_solver_call,
            required_arguments: list[str] = None) -> None:
        """Initialize SparkleTargetFunctionRunner."""
        if required_arguments is None:
            required_arguments = []
        super().__init__(scenario=scenario, required_arguments=required_arguments)
        self._target_function = target_function

        # Signatures here
        signature = inspect.signature(self._target_function).parameters
        for argument in required_arguments:
            if argument not in signature.keys():
                raise RuntimeError(
                    f"Target function needs to have the arguments {required_arguments} "
                    f"but could not find {argument}."
                )

        # Now we check for additional arguments which are not used by SMAC
        # However, we only want to warn the user and not
        for key in list(signature.keys())[1:]:
            if key not in required_arguments:
                print(f"The argument {key} is not set by SMAC: Consider removing it "
                      "from the target function.")

        # Pynisher limitations
        if (memory := self._scenario.trial_memory_limit) is not None:
            unit = None
            if isinstance(memory, (tuple, list)):
                memory, unit = memory
            memory = int(math.ceil(memory))
            if unit is not None:
                memory = (memory, unit)

        if (time := self._scenario.trial_walltime_limit) is not None:
            time = int(math.ceil(time))

        self._memory_limit = memory
        self._algorithm_walltime_limit = time

    @property
    def meta(self: SparkleTargetFunctionRunner) -> dict[str, Any]:  # noqa: D102
        meta = super().meta

        # Partial's don't have a __code__ attribute but are a convenient
        # way a user might want to pass a function to SMAC, specifying
        # keyword arguments.
        f = self._target_function
        if isinstance(f, partial):
            f = f.func
            meta.update({"code": str(f.__code__.co_code)})
            meta.update({"code-partial-args": repr(f)})
        else:
            meta.update({"code": str(self._target_function.__code__.co_code)})

        return meta

    def run(
        self: SparkleTargetFunctionRunner,
        config: Configuration,
        instance: str | None = None,
        budget: float | None = None,
        seed: int | None = None,
        **dask_data_to_scatter: dict[str, Any],
    ) -> tuple[StatusType, float | list[float], float, dict]:
        """Calls the target function and parses output values for SMAC3.

        Parameters
        ----------
        config: Configuration
            Configuration to be passed to the target function.
        instance: str | None, defaults to None
            The Problem instance.
        budget: float | None, defaults to None
            A positive, real-valued number representing an arbitrary limit to the
            target function handled by the target function internally.
        seed: int | None, defaults to None
            The seed to use.
        dask_data_to_scatter: dict[str, Any]
            This kwargs must be empty when we do not use dask! ()
            When a user scatters data from their local process to the distributed
            network, this data is distributed in a round-robin fashion grouping
            by number of cores. Roughly speaking, we can keep this data in memory and
            then we do not have to (de-)serialize the data every time we would like
            to execute a target function with a big dataset. For example, when your
            target function has a big dataset shared across all the target function,
            this argument is very useful.

        Returns
        -------
        status: StatusType
            Status of the trial.
        cost: float | list[float]
            Resulting cost(s) of the trial.
        runtime: float
            The time the target function took to run.
        additional_info: dict
            All further additional trial information.
        """
        # The kwargs are passed to the target function.
        kwargs: dict[str, Any] = {}
        kwargs.update(dask_data_to_scatter)

        if "seed" in self._required_arguments:
            kwargs["seed"] = seed

        if "instance" in self._required_arguments:
            kwargs["instance"] = instance

        if "budget" in self._required_arguments:
            kwargs["budget"] = budget

        # Presetting
        cost: float | list[float] = self._crash_cost
        runtime = 0.0
        additional_info = {}
        status = StatusType.CRASHED

        target_function: Callable
        target_function = self._target_function

        # We don't want the user to change the configuration
        config_copy = copy.deepcopy(config)

        # Call target function
        try:
            # Parse the data yielded by solver/runsolver
            result = self(config_copy, target_function, kwargs)
            status = SMAC3.convert_status(result["status"])
            del result["status"]
            runtime = result["cpu_time"]
            del result["cpu_time"]
            # RunSolver also records Wallclock time and memory in the output
            # Maybe in the future we can communicate it to SMAC3
            del result["wall_time"]
            del result["memory"]
            result = {key: value
                      for key, value in result.items() if key in self._objectives}
        except Exception as e:
            cost = np.asarray(cost).squeeze().tolist()
            additional_info = {
                "traceback": traceback.format_exc(),
                "error": repr(e),
            }
            status = StatusType.CRASHED

        if status == StatusType.CRASHED:
            return status, cost, runtime, additional_info

        # Do some sanity checking (for multi objective)
        error = f"Returned costs {result} does not match "\
                f"the number of objectives {self._objectives}."

        # If dict convert to array and make sure the order is correct
        if isinstance(result, dict):
            if len(result) != len(self._objectives):
                raise RuntimeError(error)

            ordered_cost: list[float] = []
            for name in self._objectives:
                if name not in result:
                    raise RuntimeError(
                        f"Objective {name} was not found in the returned costs.")

                ordered_cost.append(result[name])

            result = ordered_cost

        if isinstance(result, list):
            if len(result) != len(self._objectives):
                raise RuntimeError(error)

        if isinstance(result, float):
            if isinstance(self._objectives, list) and len(self._objectives) != 1:
                raise RuntimeError(error)

        cost = result

        if cost is None:
            status = StatusType.CRASHED
            cost = self.crash_cost

        # We want to get either a float or a list of floats.
        cost = np.asarray(cost).squeeze().tolist()

        return status, cost, runtime, additional_info

    def __call__(
        self: SparkleTargetFunctionRunner,
        config: Configuration,
        algorithm: Callable,
        algorithm_kwargs: dict[str, Any],
    ) -> (
        float
        | list[float]
        | dict[str, float]
        | tuple[float, dict]
        | tuple[list[float], dict]
        | tuple[dict[str, float], dict]
    ):
        """Calls the algorithm, which is processed in the ``run`` method."""
        return algorithm(config, **algorithm_kwargs)


if __name__ == "__main__":
    # Incoming call from Sparkle:
    args = sys.argv[1:]
    scenario_file = Path(args[0])
    run_index = int(args[1])
    output_path = Path(args[2])
    scenario = SMAC3Scenario.from_file(scenario_file, run_index=run_index)
    global solver, objectives, cutoff, log_dir
    solver = scenario.solver
    cutoff = scenario.cutoff_time
    objectives = scenario.sparkle_objectives
    log_dir = scenario.log_dir
    kwargs = {}
    if scenario.max_ratio is not None:  # Override the default initial design
        kwargs["initial_design"] = scenario.smac_facade.get_initial_design(
            scenario=scenario.smac3_scenario, max_ratio=scenario.max_ratio)
    # Facade Configurable
    smac_facade = scenario.smac_facade(scenario.smac3_scenario,
                                       smac3_solver_call,
                                       **kwargs)
    # Override the target function runner to control resource management
    smac_facade._runner = SparkleTargetFunctionRunner(
        scenario.smac3_scenario,
        required_arguments=smac_facade._get_signature_arguments())
    # Refresh the optimiser with new target class
    smac_facade._optimizer = smac_facade._get_optimizer()

    incumbent = smac_facade.optimize()
    print(incumbent)
    # TODO: Fix taking first objective, how do we determine 'best configuration' from
    # a multi objective run?
    SMAC3.organise_output(scenario.smac3_scenario.output_directory / "runhistory.json",
                          output_target=output_path,
                          scenario=scenario,
                          run_id=run_index)
