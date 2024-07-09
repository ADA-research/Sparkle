"""Methods regarding feature extractors."""
from __future__ import annotations
from pathlib import Path
import ast
import subprocess
from sparkle.types import SparkleCallable
from sparkle.structures import FeatureDataFrame
from tools.runsolver_parsing import get_status


class Extractor(SparkleCallable):
    """Extractor base class for extracting features from instances."""
    wrapper = "sparkle_extractor_wrapper.py"

    def __init__(self: Extractor,
                 directory: Path,
                 runsolver_exec: Path = None,
                 raw_output_directory: Path = None,
                 ) -> None:
        """Initialize solver.

        Args:
            directory: Directory of the solver.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in directory.
            raw_output_directory: Directory where solver will write its raw output.
                Defaults to directory / tmp
        """
        super().__init__(directory, runsolver_exec, raw_output_directory)
        self.output_dimension = 1  # TODO: Set to the output dim of the extractor

    def build_cmd(self: Extractor,
                  instance: Path | list[Path],
                  output_file: Path,
                  runsolver_args: list[str | Path] = None,
                  ) -> list[str]:
        """Builds a command line string seperated by space.

        Args:
            instance: The instance to run on
            outputfile: Target output file
            runsolver_args: The arguments for runsolver. If not present,
                will run the extractor without runsolver.

        Returns:
            The command seperated per item in the list.
        """
        cmd_list_extractor = []
        if not isinstance(instance, list):
            instance = [instance]
        if runsolver_args is not None:
            # Ensure stringification of runsolver configuration is done correctly
            cmd_list_extractor += [str(self.runsolver_exec.absolute())]
            cmd_list_extractor += [str(runsolver_config) for runsolver_config
                                   in runsolver_args]
        cmd_list_extractor += [f"{self.directory / Extractor.wrapper}",
                               "-extractor_dir", f"{self.directory}/",
                               "-instance_file"] + [str(file) for file in instance]
        if output_file is not None:
            cmd_list_extractor += ["-output_file", str(output_file)]
        return cmd_list_extractor

    def run(self: Extractor,
            instance: Path | list[Path],
            output_file: Path = None,
            runsolver_args: list[str | Path] = None) -> list | None:
        """Runs an extractor job with Runrunner.

        Args:
            extractor_path: Path to the executable
            instance: Path to the instance to run on
            output_file: Target output. If None, piped to the RunRunner job.
            runsolver_args: List of run solver args, each word a seperate item.

        Returns:
            The features or None if an output file is used, or features can not be found.
        """
        cmd_extractor = self.build_cmd(instance, output_file, runsolver_args)
        extractor = subprocess.run(cmd_extractor, capture_output=True)
        if output_file is None:
            try:
                features = ast.literal_eval(extractor.stdout.decode())
                return features
            except Exception:
                return None
        return None

    def get_feature_vector(self: Extractor,
                           result: Path,
                           runsolver_values: Path = None) -> list[str]:
        """Extracts feature vector from output, vector of missing values upon failure.

        Args:
            result: The raw output of the extractor
            runsolver_values: The output of runsolver.

        Returns:
            A list of features.
        """
        if result.exists() and get_status(runsolver_values, None) != "TIMEOUT":
            feature_values = ast.literal_eval(result.read_text())
            return [str(value) for _, _, value in feature_values]
        return [FeatureDataFrame.missing_value] * self.output_dimension
