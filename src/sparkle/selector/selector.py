"""File to handle a Selector for selecting Solvers."""

from __future__ import annotations
import random
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
from sparkle.instance import InstanceSet


class Selector:
    """The Selector class for handling Algorithm Selection."""

    selector_cli = Path(__file__).parent / "selector_cli.py"

    def __init__(
        self: Selector,
        selector_class: AbstractModelBasedSelector,
        model_class: AbstractPredictor | ClassifierMixin | RegressorMixin,
    ) -> None:
        """Initialize the Selector object.

        Args:
            selector_class: The (name of) Selector class to construct.
            model_class: The (name of) model class the selector will use.
        """
        if isinstance(selector_class, str):  # Resolve class name
            from asf import selectors

            selector_class = getattr(selectors, selector_class)
        if isinstance(model_class, str):  # Resolve class name
            from sklearn import ensemble

            model_class = getattr(ensemble, model_class)
        self.selector_class = selector_class
        self.model_class = model_class

    @property
    def name(self: Selector) -> str:
        """Return the name of the selector."""
        return f"{self.selector_class.__name__}_{self.model_class.__name__}"

    def construct(
        self: Selector,
        selection_scenario: SelectionScenario,
        run_on: Runner = Runner.SLURM,
        job_name: str = None,
        sbatch_options: list[str] = None,
        slurm_prepend: str | list[str] | Path = None,
        base_dir: Path = Path(),
    ) -> Run:
        """Construct the Selector.

        Args:
            selection_scenario: The scenario to construct the Selector for.
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
            self.model_class,
            ScenarioMetadata(
                algorithms=selection_scenario.performance_data.columns.to_list(),
                features=selection_scenario.feature_data.columns.to_list(),
                performance_metric=selection_scenario.objective.name,
                maximize=not selection_scenario.objective.minimise,
                budget=selection_scenario.solver_cutoff,
            ),
        )
        cmd = asf_cli.build_cli_command(
            selector,
            selection_scenario.feature_target_path,
            selection_scenario.performance_target_path,
            selection_scenario.selector_file_path,
        )
        cmd = [" ".join([str(c) for c in cmd])]

        job_name = job_name or f"Selector Construction: {selection_scenario.name}"
        construct = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=job_name,
            base_dir=base_dir,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend,
        )

        if run_on == Runner.LOCAL:
            construct.wait()
            if not selection_scenario.selector_file_path.is_file():
                print(f"Selector construction of {self.name} failed!")
        return construct

    def run(
        self: Selector,
        selector_path: Path,
        instance: str,
        feature_data: FeatureDataFrame,
    ) -> list:
        """Run the Selector, returning the prediction schedule upon success."""
        instance_features = feature_data[
            [
                instance,
            ]
        ]
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

    def run_cli(
        self: Selector,
        scenario_path: Path,
        instance_set: InstanceSet | list[Path],
        feature_data: Path,
        run_on: Runner = Runner.LOCAL,
        sbatch_options: list[str] = None,
        slurm_prepend: str | list[str] | Path = None,
        job_name: str = None,
        dependencies: list[Run] = None,
        log_dir: Path = None,
    ) -> Run:
        """Run the Selector CLI and write result to the Scenario PerformanceDataFrame.

        Args:
            scenario_path: The path to the scenario with the Selector to run.
            instance_set: The instance set to run the Selector on.
            feature_data: The instance feature data to use.
            run_on: Which runner to use. Defaults to slurm.
            sbatch_options: Additional options to pass to sbatch.
            slurm_prepend: Slurm script to prepend to the sbatch
            job_name: Name to give the Slurm job when submitting.
            dependencies: List of dependencies to add to the job.
            log_dir: The directory to write logs to.

        Returns:
            The Run object.
        """
        # NOTE: The selector object and the scenario selector could differ which could
        # cause unintended behaviour (e.g. running a different selector than desired)
        instances = (
            instance_set
            if isinstance(instance_set, list)
            else instance_set.instance_paths
        )
        commands = [
            f"python3 {Selector.selector_cli} "
            f"--selector-scenario {scenario_path} "
            f"--instance {instance_path} "
            f"--feature-data {feature_data} "
            f"--log-dir {log_dir} "
            f"--seed {random.randint(0, 2**32 - 1)}"
            for instance_path in instances
        ]

        job_name = (
            f"Run Selector: {self.name} on {len(instances)} instances"
            if not job_name
            else job_name
        )
        import subprocess

        r = rrr.add_to_queue(
            runner=run_on,
            cmd=commands,
            name=job_name,
            stdout=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print
            stderr=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print
            base_dir=log_dir,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend,
            dependencies=dependencies,
        )
        if run_on == Runner.LOCAL:
            r.wait()
        return r


class SelectionScenario:
    """A scenario for a Selector."""

    __selector_solver_name__ = "portfolio_selector"

    def __init__(
        self: SelectionScenario,
        parent_directory: Path,
        selector: Selector,
        objective: SparkleObjective,
        performance_data: PerformanceDataFrame | Path,
        feature_data: FeatureDataFrame | Path,
        feature_extractors: list[str] = None,
        solver_cutoff: int | float = None,
        extractor_cutoff: int | float = None,
        ablate: bool = False,
        subdir_path: Path = None,
    ) -> None:
        """Initialize a scenario for a selector."""
        self.selector: Selector = selector
        self.objective: SparkleObjective = objective
        self.solver_cutoff: float = solver_cutoff
        self.extractor_cutoff: float = extractor_cutoff
        if subdir_path is not None:
            self.directory = parent_directory / subdir_path
        elif isinstance(performance_data, PerformanceDataFrame):
            self.directory: Path = (
                parent_directory
                / selector.name
                / "_".join([Path(s).name for s in performance_data.solvers])
            )
        else:
            self.directory = performance_data.parent
        self.name = f"{selector.name} on {self.directory.name}"
        self.selector_file_path: Path = self.directory / "portfolio_selector"
        self.scenario_file: Path = self.directory / "scenario.txt"
        self.selector_performance_path: Path = (
            self.directory / "selector_performance.csv"
        )
        if self.selector_performance_path.exists():
            self.selector_performance_data = PerformanceDataFrame(
                self.selector_performance_path
            )
        else:  # Create new performance data frame for selector, write to file later
            self.selector_performance_data = performance_data.clone()
            self.selector_performance_data.add_solver(
                SelectionScenario.__selector_solver_name__
            )

        if isinstance(performance_data, PerformanceDataFrame):  # Convert
            # Convert the dataframes to Selector Format
            new_column_names: list[str] = []
            for solver, config_id, _ in performance_data.columns:
                if f"{solver}_{config_id}" not in new_column_names:
                    new_column_names.append(f"{solver}_{config_id}")
            self.performance_data = performance_data.drop(
                [PerformanceDataFrame.column_seed], axis=1, level=2
            )
            self.performance_data = self.performance_data.droplevel(
                [
                    PerformanceDataFrame.column_configuration,
                    PerformanceDataFrame.column_meta,
                ],
                axis=1,
            )
            self.performance_data = self.performance_data.droplevel(
                PerformanceDataFrame.index_objective, axis=0
            )
            self.performance_data.columns = new_column_names
            # Requires instances as index for both, columns as features / solvers
            # TODO: This should be an aggregation instead?
            self.performance_data.index = self.performance_data.index.droplevel("Run")
            # Enforce data type to be numeric
            self.performance_data = self.performance_data.astype(float)
            self.performance_target_path = self.directory / "performance_data.csv"
        else:  # Read from Path
            self.performance_data: pd.DataFrame = pd.read_csv(
                performance_data, index_col=0
            )
            self.performance_target_path: Path = performance_data

        if isinstance(feature_data, FeatureDataFrame):  # Convert
            self.feature_extractors = feature_data.extractors
            # Features requires instances as index, columns as feature names
            feature_target = feature_data.copy()
            feature_target.index = feature_target.index.map("_".join)  # Reduce Index
            # ASF -> feature columns, instance rows
            self.feature_data: pd.DataFrame = feature_target.T.astype(float)
            self.feature_target_path: Path = self.directory / "feature_data.csv"
        else:  # Read from Path
            self.feature_extractors = feature_extractors
            self.feature_data: pd.DataFrame = pd.read_csv(feature_data)
            self.feature_target_path: Path = feature_data

        self.ablation_scenarios: list[SelectionScenario] = []
        if ablate and len(self.performance_data.columns) > 2:
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
                    raise ValueError(
                        "Cannot ablate scenario after loading from file! "
                        "Requires original PerformanceDataFrame."
                    )

                self.ablation_scenarios.append(
                    SelectionScenario(
                        parent_directory=self.directory,
                        selector=selector,
                        objective=objective,
                        performance_data=ablated_pd,
                        feature_data=feature_data,
                        solver_cutoff=solver_cutoff,
                        ablate=False,  # If we set to true here, recursion would happen
                        subdir_path=ablate_subdir,
                    )
                )

    @property
    def training_instances(self: SelectionScenario) -> list[str]:
        """Get the training instances."""
        return self.performance_data.index.to_list()

    @property
    def test_instances(self: SelectionScenario) -> list[str]:
        """Get the test instances."""
        instances = self.selector_performance_data.instances
        return [i for i in instances if i not in self.training_instances]

    @property
    def training_instance_sets(self: SelectionScenario) -> list[str]:
        """Get the training instance sets."""
        # NOTE: This no longer works as instances no longer have their set in the name
        return list(set(Path(i).parent.name for i in self.training_instances))

    @property
    def test_instance_sets(self: SelectionScenario) -> list[str]:
        """Get the test instance sets."""
        # NOTE: This no longer works as instances no longer have their set in the name
        return list(set(Path(i).parent.name for i in self.test_instances))

    @property
    def instance_sets(self: SelectionScenario) -> list[str]:
        """Get all the instance sets used in this scenario."""
        return list(
            set(Path(i).parent.name for i in self.selector_performance_data.instances)
        )

    @property
    def solvers(self: SelectionScenario) -> list[str]:
        """Get the solvers used for the selector."""
        return self.performance_data.columns.to_list()

    def create_scenario(self: SelectionScenario) -> None:
        """Prepare the scenario directories."""
        self.directory.mkdir(parents=True, exist_ok=True)
        self.performance_data.to_csv(self.performance_target_path)
        self.feature_data.to_csv(self.feature_target_path)
        self.selector_performance_data.save_csv(self.selector_performance_path)
        self.create_scenario_file()

    def create_scenario_file(self: SelectionScenario) -> None:
        """Create the scenario file.

        Write the scenario to file.
        """
        with self.scenario_file.open("w") as fout:
            fout.write(self.serialise())

    def serialise(self: SelectionScenario) -> dict:
        """Serialize the scenario."""
        return (
            f"selector: {self.selector.name}\n"
            f"solver_cutoff: {self.solver_cutoff}\n"
            f"extractor_cutoff: {self.extractor_cutoff}\n"
            f"ablate: {len(self.ablation_scenarios) > 0}\n"
            f"objective: {self.objective}\n"
            f"selector_performance_data: {self.selector_performance_path}\n"
            f"performance_data: {self.performance_target_path}\n"
            f"feature_data: {self.feature_target_path}\n"
            f"feature_extractors: {','.join(self.feature_extractors)}\n"
        )

    @staticmethod
    def from_file(scenario_file: Path) -> SelectionScenario:
        """Reads scenario file and initalises SelectorScenario."""
        if not scenario_file.is_file() and (scenario_file / "scenario.txt").is_file():
            scenario_file = scenario_file / "scenario.txt"  # Resolve from directory
        values = {
            key: value.strip()
            for key, value in [
                line.split(": ", maxsplit=1) for line in scenario_file.open()
            ]
        }
        selector_class, selector_model = values["selector"].split("_", maxsplit=1)
        import ast

        selector = Selector(selector_class, selector_model)
        return SelectionScenario(
            parent_directory=scenario_file.parent,
            selector=selector,
            objective=resolve_objective(values["objective"]),
            performance_data=Path(values["performance_data"]),
            feature_data=Path(values["feature_data"]),
            feature_extractors=values["feature_extractors"].split(","),
            solver_cutoff=float(values["solver_cutoff"]),
            ablate=ast.literal_eval(values["ablate"]),
        )
