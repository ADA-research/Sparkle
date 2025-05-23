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
                  job_name: str = None,
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
            job_name: Name to give the construction job when submitting.
            sbatch_options: Additional options to pass to sbatch.
            slurm_prepend: Slurm script to prepend to the sbatch
            base_dir: The base directory to run the Selector in.

        Returns:
            The construction Run
        """
        # Convert the dataframes to Selector Format
        # Extract the configurations, reformat columns
        configurations_csv = target_file.parent / "configurations.csv"
        new_column_names = []
        config_csv_lines = []
        for solver, config_id, _ in performance_data.columns:
            if f"{solver}_{config_id}" not in new_column_names:
                new_column_names.append(f"{solver}_{config_id}")
                config_csv_lines.append(
                    f"{solver},{config_id},"
                    f"{performance_data.get_full_configuration(solver, config_id)}"
                )
        configurations_csv.write_text("\n".join(config_csv_lines))
        performance_target = performance_data.drop(
            [PerformanceDataFrame.column_seed],
            axis=1, level=2)
        performance_target = performance_target.droplevel([
            PerformanceDataFrame.column_configuration,
            PerformanceDataFrame.column_meta], axis=1)
        performance_target.columns = new_column_names
        # Requires instances as index for both, columns as features / solvers
        performance_target = performance_target.loc[objective.name]  # Select objective
        # TODO: This should be an aggregation instead?
        performance_target.index = performance_target.index.droplevel("Run")  # Drop runs
        performance_target_path = target_file.parent / "performance_data.csv"
        performance_target.to_csv(performance_target_path)

        # Features requires instances as index, columns as feature names
        feature_target = feature_data.dataframe.copy()
        feature_target.index = feature_target.index.map("_".join)  # Reduce Multi-Index
        feature_target = feature_target.T  # ASF has feature columns and instance rows
        feature_target_path = target_file.parent / "feature_data.csv"
        feature_target.to_csv(feature_target_path)

        selector = self.selector_class(
            self.model_class, ScenarioMetadata(
                algorithms=performance_target.columns.to_list(),
                features=feature_target.columns.to_list(),
                performance_metric=objective.name,
                maximize=not objective.minimise,
                budget=solver_cutoff
            )
        )

        cmd = asf_cli.build_cli_command(selector,
                                        feature_target_path,
                                        performance_target_path,
                                        target_file)

        cmd = [" ".join([str(c) for c in cmd])]
        if not job_name:
            solver_job_names =\
                [f"{Path(s).name} ({len(performance_data.get_configurations(s))})"
                 for s in performance_data.solvers]
            job_name = f"Selector Construction: {', '.join(solver_job_names)}"
        construct = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=job_name,
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
            return None
        # ASF presents result as schedule per instance, we only use one in this setting
        schedule = schedule[instance]
        print(schedule)
        for index, (solver, time) in enumerate(schedule):
            # Split solver name back into solver and config id
            solver_name, conf_index = solver.split("_", maxsplit=1)
            schedule[index] = (solver_name, conf_index, time)
        return schedule
        # Translate possible configurations from file
        if (selector_path.parent / "configurations.csv").exists():
            import ast
            configurations =\
                [ast.literal_eval(line) for line in
                 (selector_path.parent / "configurations.csv").read_text().split("\n")]
            for index, (solver, time, _) in enumerate(schedule):
                solver_name, conf_index = solver.rsplit("_", maxsplit=1)
                schedule[index] = (solver_name, time, configurations[int(conf_index)])
        return schedule
