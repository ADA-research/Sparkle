"""Methods regarding feature extractors."""
from __future__ import annotations
from pathlib import Path
import runrunner as rrr
from runrunner import Runner
from sparkle.types import SparkleCallable
from sparkle.structures.feature_data_csv_help import SparkleFeatureDataCSV
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
        self.output_dimension = 1 #This needs to be set to the output dim of the extractor
        
    def build_cmd(self: Extractor,
                  instance: Path,
                  output_file: Path,
                  runsolver_args: list[str | Path] = None,
                  ) -> list[str]:
        cmd_list_extractor = []
        if runsolver_args is not None:
            # Ensure stringification of runsolver configuration is done correctly
            cmd_list_extractor += [str(self.runsolver_exec.absolute())]
            cmd_list_extractor += [str(runsolver_config) for runsolver_config
                                   in runsolver_args]
        cmd_list_extractor += [f"{self.directory / Extractor.wrapper}",
                                "-extractor_dir", f"{self.directory}/",
                                "-instance_file", str(instance),
                                "-output_file", str(output_file)]
        return cmd_list_extractor

    def run(self: Extractor,
            instance: Path,
            output_file: Path,
            runsolver_args: list[str | Path] = None,
            run_options: list[any] = None,
            run_on: Runner = Runner.SLURM) -> rrr.LocalRun | rrr.SlurmRun:
        """Runs an extractor job with Runrunner.

        Args:
            extractor_path: Path to the executable
            instance: Path to the instance to run on
            output_file: Target output
            runsolver_args: List of run solver args, each word a seperate item.
            run_options: The RunRunner options list of job name, sbatch options list
                and srun options list.
            run_on: Platform to run on

        Returns:
            Local- or SlurmRun."""
        cmd_extractor = self.build_cmd(instance, output_file, runsolver_args)
        return rrr.add_to_queue(
            runner=run_on,
            cmd=" ".join(cmd_extractor),
            name=run_options[0],
            base_dir=self.raw_output_directory,
            sbatch_options=run_options[1],
            srun_options=run_options[2]
        )

    def get_feature_vector(self: Extractor,
                           result: Path,
                           runsolver_values: Path = None) -> list[str]:
        """Extracts feature vector from output, vector of missing values upon failure.

        Args:
            result: The raw output of the extractor
            runsolver_values: The output of runsolver.

        Returns:
            A list of features."""
        features = [SparkleFeatureDataCSV.missing_value] * self.output_dimension
        if result.exists() and get_status(runsolver_values, None) != "TIMEOUT":
            # Last line contains feature vector:
            feature_line = result.open().readlines()[-1]
            # Trim instance name and white space from features
            features = feature_line.strip().split(",")[1:]
        return features