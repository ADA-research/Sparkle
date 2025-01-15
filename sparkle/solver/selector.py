"""File to handle a Selector for selecting Solvers."""
from __future__ import annotations
from pathlib import Path
import subprocess
import ast

from sklearn.base import ClassifierMixin, RegressorMixin
from asf.predictors import AbstractPredictor
from asf.selectors.abstract_model_based_selector import AbstractModelBasedSelector

# import runrunner as rrr
from runrunner import Runner, Run

from sparkle.types import SparkleCallable, SparkleObjective
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame


class Selector(SparkleCallable):
    """The Selector class for handling Algorithm Selection."""

    def __init__(
            self: SparkleCallable,
            raw_output_directory: Path,
            selector_class: AbstractModelBasedSelector,
            model_class: AbstractPredictor | ClassifierMixin | RegressorMixin) -> None:
        """Initialize the Selector object.

        Args:
            raw_output_directory: Directory where the Selector will write its raw output.
                Defaults to directory / tmp
            selector_class: The Selector class to construct.
            model_class: The model class the selector will use.
        """
        self.selector: AbstractModelBasedSelector =\
            selector_class(model_class, metadata=None)
        self.name = type(selector_class).__name__
        self.raw_output_directory = raw_output_directory

        if not self.raw_output_directory.exists():
            self.raw_output_directory.mkdir(parents=True)

    def build_construction_cmd(
            self: Selector,
            target_file: Path,
            performance_data: Path,
            feature_data: Path,
            objective: SparkleObjective,
            runtime_cutoff: int | float | str = None,
            wallclock_limit: int | float | str = None) -> list[str | Path]:
        """Builds the commandline call string for constructing the Selector.

        Args:
            target_file: Path to the file to save the Selector to.
            performance_data: Path to the performance data csv.
            feature_data: Path to the feature data csv.
            objective: The objective to optimize for selection.
            runtime_cutoff: Cutoff for the runtime in seconds. Defaults to None
            wallclock_limit: Cutoff for total wallclock in seconds. Defaults to None

        Returns:
            The command list for constructing the Selector.
        """
        # This method is to be replaced with a ASF method call
        return

    def construct(self: Selector,
                  target_file: Path | str,
                  performance_data: PerformanceDataFrame,
                  feature_data: FeatureDataFrame,
                  objective: SparkleObjective,
                  runtime_cutoff: int | float | str = None,
                  wallclock_limit: int | float | str = None,
                  run_on: Runner = Runner.SLURM,
                  sbatch_options: list[str] = None,
                  base_dir: Path = Path()) -> Run:
        """Construct the Selector.

        Args:
            target_file: Path to the file to save the Selector to.
            performance_data: Path to the performance data csv.
            feature_data: Path to the feature data csv.
            objective: The objective to optimize for selection.
            runtime_cutoff: Cutoff for the runtime in seconds.
            wallclock_limit: Cutoff for the wallclock time in seconds.
            run_on: Which runner to use. Defaults to slurm.
            sbatch_options: Additional options to pass to sbatch.
            base_dir: The base directory to run the Selector in.

        Returns:
            Path to the constructed Selector.
        """
        if isinstance(target_file, str):
            target_file = self.raw_output_directory / target_file
        # Convert the dataframes to Selector Format
        # performance_csv = performance_data.to_autofolio(objective=objective,
        #                                                target=target_file.parent)
        # feature_csv = feature_data.to_autofolio(target_file.parent)
        """
        self.selector.fit(feature_data, performance_data)
        import pickle
        some_path = Path("test.model")
        with some_path.open("w+") as f:
            pickle.dump(self.selector, f)
        with some_path.open("r") as f:
            selector = pickle.load(f)
        #self.selector.
        self.selector
        cmd = self.build_construction_cmd(target_file,
                                          performance_csv,
                                          feature_csv,
                                          objective,
                                          runtime_cutoff,
                                          wallclock_limit)

        cmd_str = " ".join([str(c) for c in cmd])
        solver_names = ", ".join([Path(s).name for s in performance_data.solvers])
        construct = rrr.add_to_queue(
            runner=run_on,
            cmd=[cmd_str],
            name=f"Selector Construction: {solver_names}",
            base_dir=base_dir,
            stdout=Path("normal.log"),
            stderr=Path("error.log"),
            sbatch_options=sbatch_options)
        if run_on == Runner.LOCAL:
            construct.wait()
            if not target_file.is_file():
                print(f"Selector construction of {self.name} failed!")

        return construct"""
        return

    def build_cmd(self: Selector,
                  selector_path: Path,
                  feature_vector: list | str) -> list[str | Path]:
        """Builds the commandline call string for running the Selector."""
        if isinstance(feature_vector, list):
            feature_vector = " ".join(map(str, feature_vector))

        return ["python3", self.selector_builder_path,
                "--load", selector_path,
                "--feature_vec", feature_vector]

    def run(self: Selector,
            selector_path: Path,
            feature_vector: list | str) -> list:
        """Run the Selector, returning the prediction schedule upon success."""
        cmd = self.build_cmd(selector_path, feature_vector)
        run = subprocess.run(cmd, capture_output=True)
        if run.returncode != 0:
            print(f"Selector run of {self.name} failed! Error:\n"
                  f"{run.stderr.decode()}")
            return None
        # Process the prediction schedule from the output
        schedule = Selector.process_predict_schedule_output(run.stdout.decode())
        if schedule is None:
            print(f"Error getting predict schedule! Selector {self.name} output:\n"
                  f"{run.stderr.decode()}")
        return schedule

    @staticmethod
    def process_predict_schedule_output(output: str) -> list:
        """Return the predicted algorithm schedule as a list."""
        prefix_string = "Selected Schedule [(algorithm, budget)]: "
        predict_schedule = ""
        predict_schedule_lines = output.splitlines()
        for line in predict_schedule_lines:
            if line.strip().startswith(prefix_string):
                predict_schedule = line.strip()
                break
        if predict_schedule == "":
            return None
        predict_schedule_string = predict_schedule[len(prefix_string):]
        return ast.literal_eval(predict_schedule_string)
