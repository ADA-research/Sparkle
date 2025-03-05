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

from sparkle.types import SparkleObjective
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
                  target_file: Path,
                  performance_data: PerformanceDataFrame,
                  feature_data: FeatureDataFrame,
                  objective: SparkleObjective,
                  solver_cutoff: int | float | str = None,
                  run_on: Runner = Runner.SLURM,
                  sbatch_options: list[str] = None,
                  slurm_prepend: str | list[str] | Path = None,
                  base_dir: Path = Path()) -> Run:
        """Construct the Selector.

        Args:
            target_file: Path to the file to save the Selector to.
            performance_data: Path to the performance data csv.
            feature_data: Path to the feature data csv.
            objective: The objective to optimize for selection.
            runtime_cutoff: Cutoff for the runtime in seconds.
            run_on: Which runner to use. Defaults to slurm.
            sbatch_options: Additional options to pass to sbatch.
            slurm_prepend: Slurm script to prepend to the sbatch
            base_dir: The base directory to run the Selector in.

        Returns:
            The construction Run
        """
        # Convert the dataframes to Selector Format
        # Requires instances as index for both, columns as features / solvers
        # Remove redundant data
        performance_csv = performance_data.drop(
            [PerformanceDataFrame.column_seed,
             PerformanceDataFrame.column_configuration],
            axis=1, level=1).droplevel(level=1, axis=1)
        performance_csv = performance_csv.loc[objective.name]  # Select objective
        performance_csv.index = performance_csv.index.droplevel("Run")  # Drop runs
        performance_path = target_file.parent / performance_data.csv_filepath.name
        performance_csv.to_csv(target_file.parent / performance_data.csv_filepath.name)

        # Features requires instances as index, columns as feature names
        feature_csv = feature_data.dataframe.copy()
        feature_csv.index = feature_csv.index.map("_".join)  # Reduce Multi-Index
        feature_csv = feature_csv.T  # ASF has feature columns and instance rows
        feature_path = target_file.parent / feature_data.csv_filepath.name
        feature_csv.to_csv(feature_path)

        selector = self.selector_class(
            self.model_class, ScenarioMetadata(
                algorithms=performance_data.solvers,
                features=feature_csv.columns.to_list(),
                performance_metric=objective.name,
                maximize=not objective.minimise,
                budget=solver_cutoff
            )
        )

        cmd = asf_cli.build_cli_command(selector,
                                        feature_path,
                                        performance_path,
                                        target_file)

        cmd = [" ".join([str(c) for c in cmd])]
        construct = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=f"{self.name} Selector Construction: "
                 f"{', '.join([Path(s).name for s in performance_data.solvers])}",
            base_dir=base_dir,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend)
        if run_on == Runner.LOCAL:
            construct.wait()
            if not target_file.is_file():
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
        return schedule[instance]
