"""Methods regarding feature extractors."""

from __future__ import annotations
from typing import Any
from pathlib import Path
import ast
import subprocess

import runrunner as rrr
from runrunner.base import Status, Runner
from runrunner.local import Run, LocalRun

from sparkle.types import SparkleCallable, SolverStatus
from sparkle.structures import FeatureDataFrame
from sparkle.tools import RunSolver
from sparkle.instance import InstanceSet


class Extractor(SparkleCallable):
    """Extractor base class for extracting features from instances."""

    wrapper = "sparkle_extractor_wrapper.py"
    extractor_cli = Path(__file__).parent / "extractor_cli.py"

    def __init__(self: Extractor, directory: Path) -> None:
        """Initialize solver.

        Args:
            directory: Directory of the solver.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in directory.
        """
        super().__init__(directory)
        self._features = None
        self._feature_groups = None
        self._groupwise_computation = None

    def __str__(self: Extractor) -> str:
        """Return the string representation of the extractor."""
        return self.name

    def __repr__(self: Extractor) -> str:
        """Return detailed representation of the extractor."""
        return (
            f"{self.name}:\n"
            f"\t- Directory: {self.directory}\n"
            f"\t- Wrapper: {self.wrapper}\n"
            f"\t- # Feature Groups: {len(self.feature_groups)}\n"
            f"\t- Output Dimension (# Features): {self.output_dimension}\n"
            f"\t- Groupwise Computation Enabled: {self.groupwise_computation}"
        )

    @property
    def features(self: Extractor) -> list[tuple[str, str]]:
        """Determines the features of the extractor."""
        if self._features is None:
            extractor_process = subprocess.run(
                [self.directory / Extractor.wrapper, "-features"], capture_output=True
            )
            self._features = ast.literal_eval(extractor_process.stdout.decode())
        return self._features

    @property
    def feature_groups(self: Extractor) -> list[str]:
        """Returns the various feature groups the Extractor has."""
        if self._feature_groups is None:
            self._feature_groups = list(set([group for group, _ in self.features]))
        return self._feature_groups

    @property
    def output_dimension(self: Extractor) -> int:
        """The size of the output vector of the extractor."""
        return len(self.features)

    @property
    def groupwise_computation(self: Extractor) -> bool:
        """Determines if you can call the extractor per group for parallelisation."""
        if self._groupwise_computation is None:
            extractor_help = subprocess.run(
                [self.directory / Extractor.wrapper, "-h"], capture_output=True
            )
            # Not the cleanest / most precise way to determine this
            self._groupwise_computation = (
                "-feature_group" in extractor_help.stdout.decode()
            )
        return self._groupwise_computation

    def build_cmd(
        self: Extractor,
        instance: Path | list[Path],
        feature_group: str = None,
        output_file: Path = None,
        cutoff_time: int = None,
        log_dir: Path = None,
    ) -> list[str]:
        """Builds a command line string seperated by space.

        Args:
            instance: The instance to run on
            feature_group: The optional feature group to run the extractor for.
            output_file: Optional file to write the output to.
            runsolver_args: The arguments for runsolver. If not present,
                will run the extractor without runsolver.
            cutoff_time: The maximum runtime.
            log_dir: Directory path for logs.

        Returns:
            The command seperated per item in the list.
        """
        cmd_list_extractor = []
        if not isinstance(instance, list):
            instance = [instance]
        cmd_list_extractor = [
            f"{self.directory / Extractor.wrapper}",
            "-extractor_dir",
            f"{self.directory}/",
            "-instance_file",
        ] + [str(file) for file in instance]
        if feature_group is not None:
            cmd_list_extractor += ["-feature_group", feature_group]
        if output_file is not None:
            cmd_list_extractor += ["-output_file", str(output_file)]
        if cutoff_time is not None:
            # Extractor handles output file itself
            return RunSolver.wrap_command(
                self.runsolver_exec,
                cmd_list_extractor,
                cutoff_time,
                log_dir,
                log_name_base=self.name,
                raw_results_file=False,
            )
        return cmd_list_extractor

    def run(
        self: Extractor,
        instance: Path | list[Path],
        feature_group: str = None,
        output_file: Path = None,
        cutoff_time: int = None,
        log_dir: Path = None,
    ) -> list[list[Any]] | list[Any] | None:
        """Runs an extractor job with Runrunner.

        Args:
            extractor_path: Path to the executable
            instance: Path to the instance to run on
            feature_group: The feature group to compute. Must be supported by the
                extractor to use.
            output_file: Target output. If None, piped to the RunRunner job.
            cutoff_time: CPU cutoff time in seconds
            log_dir: Directory to write logs. Defaults to CWD.

        Returns:
            The features or None if an output file is used, or features can not be found.
        """
        log_dir = Path() if log_dir is None else log_dir
        if feature_group is not None and not self.groupwise_computation:
            # This extractor cannot handle groups, compute all features
            feature_group = None
        cmd_extractor = self.build_cmd(
            instance, feature_group, output_file, cutoff_time, log_dir
        )
        run_on = Runner.LOCAL  # TODO: Let this function also handle Slurm runs
        extractor_run = rrr.add_to_queue(runner=run_on, cmd=" ".join(cmd_extractor))
        if isinstance(extractor_run, LocalRun):
            extractor_run.wait()
            if extractor_run.status == Status.ERROR:
                print(f"{self.name} failed to compute features for {instance}.")
                for i, job in enumerate(extractor_run.jobs):
                    print(
                        f"Job {i} error yielded was:\n"
                        f"\t-stdout: '{job.stdout}'\n"
                        f"\t-stderr: '{job.stderr}'\n"
                    )
                return None
            # RunRunner adds a stamp before the statement
            output = [
                ast.literal_eval(job.stdout.split("\t", maxsplit=1)[-1])
                for job in extractor_run.jobs
            ]
            if len(output) == 1:
                return output[0]
            return output
        return None

    def run_cli(
        self: Extractor,
        instance_set: InstanceSet | list[Path],
        feature_dataframe: FeatureDataFrame,
        cutoff_time: int,
        feature_group: str = None,
        run_on: Runner = Runner.SLURM,
        sbatch_options: list[str] = None,
        srun_options: list[str] = None,
        parallel_jobs: int = None,
        slurm_prepend: str | list[str] | Path = None,
        dependencies: list[Run] = None,
        log_dir: Path = None,
    ) -> None:
        """Run the Extractor CLI and write result to the FeatureDataFrame.

        Args:
            instance_set: The instance set to run the Extractor on.
            feature_dataframe: The feature dataframe to write to.
            cutoff_time: CPU cutoff time in seconds
            feature_group: The feature group to compute. If left empty,
                will run on all feature groups.
            run_on: The runner to use.
            sbatch_options: Additional options to pass to sbatch.
            srun_options: Additional options to pass to srun.
            parallel_jobs: Number of parallel jobs to run.
            slurm_prepend: Slurm script to prepend to the sbatch
            dependencies: List of dependencies to add to the job.
            log_dir: The directory to write logs to.
        """
        instances = (
            instance_set
            if isinstance(instance_set, list)
            else instance_set.instance_paths
        )
        log_dir = Path() if log_dir is None else log_dir
        feature_group = f"--feature-group {feature_group} " if feature_group else ""
        commands = [
            f"python3 {Extractor.extractor_cli} "
            f"--extractor {self.directory} "
            f"--instance {instance_path} "
            f"--feature-csv {feature_dataframe.csv_filepath} "
            f"{feature_group}"
            f"--cutoff {cutoff_time} "
            f"--log-dir {log_dir}"
            for instance_path in instances
        ]

        job_name = f"Run Extractor: {self.name} on {len(instances)} instances"
        import subprocess

        run = rrr.add_to_queue(
            runner=run_on,
            cmd=commands,
            name=job_name,
            stdout=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print
            stderr=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print
            base_dir=log_dir,
            sbatch_options=sbatch_options,
            srun_options=srun_options,
            parallel_jobs=parallel_jobs,
            prepend=slurm_prepend,
            dependencies=dependencies,
        )
        if isinstance(run, LocalRun):
            print("Waiting for the local calculations to finish.")
            run.wait()
            for job in run.jobs:
                jobs_done = sum(j.status == Status.COMPLETED for j in run.jobs)
                print(f"Executing Progress: {jobs_done} out of {len(run.jobs)}")
                if jobs_done == len(run.jobs):
                    break
                job.wait()
            print("Computing features done!")
        else:
            print(f"Running {self.name} through Slurm with Job IDs: {run.run_id}")
        return run

    def get_feature_vector(
        self: Extractor, result: Path, runsolver_values: Path = None
    ) -> list[str]:
        """Extracts feature vector from an output file.

        Args:
            result: The raw output of the extractor
            runsolver_values: The output of runsolver.

        Returns:
            A list of features. Vector of missing values upon failure.
        """
        if (
            result.exists()
            and RunSolver.get_status(runsolver_values, None) != SolverStatus.TIMEOUT
        ):
            feature_values = ast.literal_eval(result.read_text())
            return [str(value) for _, _, value in feature_values]
        return [FeatureDataFrame.missing_value] * self.output_dimension
