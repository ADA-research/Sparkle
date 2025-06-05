"""File to handle a Selector for selecting Solvers."""
from __future__ import annotations
from pathlib import Path

from sklearn.base import ClassifierMixin, RegressorMixin
from asf.cli import cli_train as asf_cli
from asf.scenario.scenario_metadata import ScenarioMetadata
from asf.predictors import AbstractPredictor
from asf.selectors.abstract_model_based_selector import AbstractModelBasedSelector

import runrunner as rrr
from runrunner import Runner, Run
import pandas as pd

from sparkle.types import SparkleObjective, resolve_objective
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame


class Selector:
    """The Selector class for handling Algorithm Selection."""

    def __init__(
            self: Selector,
            selector_class: AbstractModelBasedSelector,
            model_class: AbstractPredictor | ClassifierMixin | RegressorMixin) -> None:
        """Initialize the Selector object.

        Args:
            selector_class: The Selector class to construct.
            model_class: The model class the selector will use.
        """
        self.selector_class = selector_class
        self.model_class = model_class

    @property
    def name(self: Selector) -> str:
        """Return the name of the selector."""
        return f"{self.selector_class.__name__}_{self.model_class.__name__}"

    def construct(self: Selector,
                  selection_scenario: SelectionScenario,
                  run_on: Runner = Runner.SLURM,
                  job_name: str = None,
                  sbatch_options: list[str] = None,
                  slurm_prepend: str | list[str] | Path = None,
                  base_dir: Path = Path()) -> Run:
        """Construct the Selector.

        Args:
            selector_scenario: The scenario to construct the Selector for.
            run_on: Which runner to use. Defaults to slurm.
            job_name: Name to give the construction job when submitting.
            sbatch_options: Additional options to pass to sbatch.
            slurm_prepend: Slurm script to prepend to the sbatch
            base_dir: The base directory to run the Selector in.

        Returns:
            The construction Run
        """
        selection_scenario.create_scenario()
        selector = self.selector_class(
            self.model_class, ScenarioMetadata(
                algorithms=selection_scenario.performance_data.columns.to_list(),
                features=selection_scenario.feature_data.columns.to_list(),
                performance_metric=selection_scenario.objective.name,
                maximize=not selection_scenario.objective.minimise,
                budget=selection_scenario.solver_cutoff
            )
        )
        cmd = asf_cli.build_cli_command(selector,
                                        selection_scenario.feature_target_path,
                                        selection_scenario.performance_target_path,
                                        selection_scenario.selector_file_path)
        cmd = [" ".join([str(c) for c in cmd])]

        job_name = job_name or f"Selector Construction: {selection_scenario.name}"
        construct = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=job_name,
            base_dir=base_dir,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend)

        if run_on == Runner.LOCAL:
            construct.wait()
            if not selection_scenario.selector_file_path.is_file():
                print(f"Selector construction of {self.name} failed!")
        return construct

    def run(self: Selector,
            selector_path: Path,
            instance: str,
            feature_data: FeatureDataFrame) -> list:
        """Run the Selector, returning the prediction schedule upon success."""
        instance_features = feature_data.dataframe[[instance, ]]
        instance_features.index = instance_features.index.map("_".join)  # Reduce
        instance_features = instance_features.T  # ASF dataframe structure
        selector = self.selector_class.load(selector_path)
        schedule = selector.predict(instance_features)
        if schedule is None:
            print(f"ERROR: Selector {self.name} failed predict schedule!")
            return None
        # ASF presents result as schedule per instance, we only use one in this setting
        schedule = schedule[instance]
        for index, (solver, time) in enumerate(schedule):
            # Split solver name back into solver and config id
            solver_name, conf_index = solver.split("_", maxsplit=1)
            schedule[index] = (solver_name, conf_index, time)
        return schedule


class SelectionScenario:
    """A scenario for a Selector."""

    def __init__(self: SelectionScenario,
                 parent_directory: Path,
                 selector: Selector,
                 objective: SparkleObjective,
                 performance_data: PerformanceDataFrame | Path,
                 feature_data: FeatureDataFrame | Path,
                 solver_cutoff: int | float = None,
                 ablate: bool = False,
                 subdir_path: Path = None
                 ) -> None:
        """Initialize a scenario for a selector."""
        self.selector: Selector = selector
        self.objective: SparkleObjective = objective
        self.solver_cutoff: float = solver_cutoff
        if subdir_path is not None:
            self.directory = parent_directory / subdir_path
        elif isinstance(performance_data, PerformanceDataFrame):
            self.directory: Path =\
                parent_directory / selector.name / "_".join(
                    [Path(s).name for s in performance_data.solvers])
        else:
            self.directory = performance_data.parent
        self.name = f"{selector.name} on {self.directory.name}"
        self.selector_file_path: Path = self.directory / "portfolio_selector"
        self.scenario_file: Path = self.directory / "scenario.txt"

        if isinstance(performance_data, PerformanceDataFrame):  # Convert
            # Convert the dataframes to Selector Format
            new_column_names = []
            for solver, config_id, _ in performance_data.columns:
                if f"{solver}_{config_id}" not in new_column_names:
                    new_column_names.append(f"{solver}_{config_id}")
            self.performance_data = performance_data.drop(
                [PerformanceDataFrame.column_seed],
                axis=1, level=2)
            self.performance_data = self.performance_data.droplevel([
                PerformanceDataFrame.column_configuration,
                PerformanceDataFrame.column_meta], axis=1)
            self.performance_data = self.performance_data.droplevel(
                PerformanceDataFrame.index_objective, axis=0)
            self.performance_data.columns = new_column_names
            # Requires instances as index for both, columns as features / solvers
            # TODO: This should be an aggregation instead?
            self.performance_data.index = self.performance_data.index.droplevel("Run")
            # Enforce data type to be numeric
            self.performance_data = self.performance_data.astype(float)
            self.performance_target_path = self.directory / "performance_data.csv"
        else:  # Read from Path
            self.performance_data: pd.DataFrame = pd.read_csv(performance_data,
                                                              index_col=0)
            self.performance_target_path: Path = performance_data

        if isinstance(feature_data, FeatureDataFrame):  # Convert
            # Features requires instances as index, columns as feature names
            feature_target = feature_data.dataframe.copy()
            feature_target.index = feature_target.index.map("_".join)  # Reduce Index
            # ASF -> feature columns, instance rows
            self.feature_data: pd.DataFrame = feature_target.T.astype(float)
            self.feature_target_path: Path = self.directory / "feature_data.csv"
        else:  # Read from Path
            self.feature_data: pd.DataFrame = pd.read_csv(feature_data)
            self.feature_target_path: Path = feature_data

        self.ablation_scenarios = None
        if ablate and len(self.performance_data.columns) > 2:
            self.ablation_scenarios: list[SelectionScenario] = []
            for solver in self.performance_data.columns:
                solver_key, conf_id = solver.split("_", maxsplit=1)
                ablate_subdir = Path(f"ablated_{Path(solver).name}")
                ablated_directory = self.directory / ablate_subdir
                if (ablated_directory / "performance_data.csv").exists():
                    ablated_pd = ablated_directory / "performance_data.csv"
                elif isinstance(performance_data, PerformanceDataFrame):
                    ablated_pd = performance_data.clone()
                    ablated_pd.remove_configuration(solver_key, conf_id)
                else:  # Note we could do this but it would be hacky?
                    raise ValueError("Cannot ablate scenario after loading from file! "
                                     "Requires original PerformanceDataFrame.")

                self.ablation_scenarios.append(SelectionScenario(
                    parent_directory=self.directory,
                    selector=selector,
                    objective=objective,
                    performance_data=ablated_pd,
                    feature_data=feature_data,
                    solver_cutoff=solver_cutoff,
                    ablate=False,  # If we set to true here, recursion would happen
                    subdir_path=ablate_subdir)
                )

    def create_scenario(self: SelectionScenario) -> None:
        """Prepare the scenario directories."""
        self.directory.mkdir(parents=True, exist_ok=True)
        self.performance_data.to_csv(self.performance_target_path)
        self.feature_data.to_csv(self.feature_target_path)
        self.create_scenario_file()

    def create_scenario_file(self: SelectionScenario) -> None:
        """Create the scenario file.

        Write the scenario to file.
        """
        with self.scenario_file.open("w") as fout:
            fout.write(self.serialise())

    def serialise(self: SelectionScenario) -> dict:
        """Serialize the scenario."""
        return f"selector: {self.selector.name}\n"\
               f"solver_cutoff: {self.solver_cutoff}\n"\
               f"ablate: {self.ablation_scenarios is not None}\n"\
               f"objective: {self.objective}\n"\
               f"performance_data: {self.performance_target_path}\n"\
               f"feature_data: {self.feature_target_path}\n"

    @staticmethod
    def from_file(scenario_file: Path) -> SelectionScenario:
        """Reads scenario file and initalises SelectorScenario."""
        values = {key: value.strip() for key, value in
                  [line.split(": ", maxsplit=1) for line in scenario_file.open()]}
        selector_class, selector_model = values["selector"].split("_", maxsplit=1)
        # Evaluate string to class
        from sklearn import ensemble
        from asf import selectors
        selector_class = getattr(selectors, selector_class)
        selector_model = getattr(ensemble, selector_model)
        selector = Selector(selector_class, selector_model)
        return SelectionScenario(
            parent_directory=scenario_file.parent,
            selector=selector,
            objective=resolve_objective(values["objective"]),
            performance_data=Path(values["performance_data"]),
            feature_data=Path(values["feature_data"]),
            solver_cutoff=float(values["solver_cutoff"]),
            ablate=bool(values["ablate"]))
