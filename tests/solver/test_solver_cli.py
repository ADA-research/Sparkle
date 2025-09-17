"""Tests for Solver CLI entry point."""

import os
import time
import math
import stat
import re
import pytest
from pathlib import Path
import shutil
from unittest.mock import patch, PropertyMock

from tests.CLI import tools as cli_tools

from sparkle.solver import Solver, solver_cli
from sparkle.structures import PerformanceDataFrame
from sparkle.platform.settings_objects import Settings

from runrunner.base import Runner, Status
from runrunner.slurm import SlurmRun


def test_solver_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the Solver CLI entry point."""
    if not Settings.DEFAULT_runsolver_exec.exists():
        return  # Currently only works with runsolver
    runsolver_path = Settings.DEFAULT_runsolver_exec.absolute()
    solver_path = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    instance_path = Path("Examples/Resources/Instances/PTN/Ptn-7824-b01.cnf").absolute()
    monkeypatch.chdir(tmp_path)

    pdf = PerformanceDataFrame(
        Path("performance_data.csv"),
        solvers=[str(solver_path)],
        instances=[instance_path.stem],
        objectives=["PAR10"],
    )

    # Patch RunSolver Path
    with patch(
        "sparkle.types.SparkleCallable.runsolver_exec",
        new_callable=PropertyMock,
        return_value=runsolver_path,
    ):
        solver_cli.main(
            [
                "--performance-dataframe",
                str(pdf.csv_filepath),
                "--solver",
                str(solver_path),
                "--instance",
                str(instance_path),
                "--run-index",
                "1",
                "--objectives",
                "PAR10",
                "--seed",
                "0",
                "--cutoff-time",
                "5",  # Short time for testing
                "--log-dir",
                str(tmp_path),
            ]
        )
        pdf = PerformanceDataFrame(pdf.csv_filepath)
        assert (
            pdf.get_value(
                solver=str(solver_path),
                instance=instance_path.stem,
                configuration=PerformanceDataFrame.default_configuration,
                run=1,
                objective="PAR10",
            )
            == 50.0  # Cutoff time should always cause the objective to be 50
        )


@pytest.mark.performance
def test_solver_cli_performance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the Solver CLI entry point with high concurrency.

    Verifies whether the results placed in the PerformanceDataFrame are correct.
    """
    if not Settings.DEFAULT_runsolver_exec.exists():
        return  # Currently only works with runsolver

    if cli_tools.get_cluster_name() != "kathleen":
        return  # Test currently does not work on Github Actions

    cluster_settings = cli_tools.get_cluster_settings()

    pdf_source = Path(
        "tests/test_files/performance/example-high-concurrency.csv"
    ).absolute()
    solver = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    instances = Path("Examples/Resources/Instances/PTN").absolute()
    runsolver_exec = Settings.DEFAULT_runsolver_exec.absolute()
    monkeypatch.chdir(tmp_path)
    pdf_target = Path("performance_data.csv")
    solver_target = Path("Solvers/PbO-CCSAT-Generic")  # Match the structure in PDF
    runsolver_target = solver_target / "runsolver"
    instances_target = Path("Instances/PTN")
    log_dir = Path("Tmp")
    shutil.copyfile(pdf_source, pdf_target)
    shutil.copytree(solver, solver_target)
    shutil.copytree(instances, instances_target)
    shutil.copyfile(runsolver_exec, runsolver_target)
    runsolver_target.chmod(os.stat(runsolver_target).st_mode | stat.S_IEXEC)

    # This DataFrame only has the Default configuration evaluated
    # And 50 new configurations that are not evaluated at all
    original_pdf = PerformanceDataFrame(pdf_target)

    solver = Solver(solver_target)
    config_ids = original_pdf.configuration_ids
    config_ids.remove(PerformanceDataFrame.default_configuration)
    # process remaining jobs into a format accesible by the solver

    # Execute all remaining jobs
    run: SlurmRun = solver.run_performance_dataframe(
        instances=[str(i) for i in instances_target.iterdir()],
        config_ids=config_ids,
        performance_dataframe=original_pdf,
        train_set=None,
        dependencies=None,
        cutoff_time=cluster_settings.solver_cutoff_time,
        sbatch_options=cluster_settings.sbatch_settings,
        slurm_prepend=cluster_settings.slurm_job_prepend,
        log_dir=log_dir,
        base_dir=log_dir,
        job_name="Performance Load Test PerformanceDataFrame",
        run_on=Runner.SLURM,
    )

    # TODO: RunRunner issue, status cannot be resolved directly after submission?
    # TODO: RunRunner issue, run.wait will never finish on Slurm?
    run.get_latest_job_details()

    # Wait for jobs to finish
    while run.status != Status.COMPLETED:
        time.sleep(15)  # Wait for status to be available
        run.get_latest_job_details()
        if run.status in [
            Status.ERROR,
            Status.KILLED,
            Status.UNKNOWN,
        ]:
            raise Exception(f"Run failed: {run.status}")
    assert run.status == Status.COMPLETED

    pdf_changed = PerformanceDataFrame(pdf_target)
    # 1. Check that the original results are left unchanged
    columns = [
        (str(solver_target), PerformanceDataFrame.default_configuration, "Seed"),
        (str(solver_target), PerformanceDataFrame.default_configuration, "Value"),
    ]

    for index in original_pdf.index:
        for column in columns:
            original_value = original_pdf.loc[index, column]
            changed_value = pdf_changed.loc[index, column]
            assert str(original_value) == str(changed_value)
            # assert original_pdf.loc[index, column] == pdf_changed.loc[index, column]

    # 2. Check that all written values are either nan (emtpy) or match with the logs
    pattern = re.compile(
        r"^(?P<objective>\S+)\s*,\s*"
        r"(?P<instance>\S+)\s*,\s*"
        r"(?P<run_id>\S+)\s*\|\s*"
        r"(?P<solver>\S+)\s*,\s*"
        r"(?P<config_id>\S+)\s*:\s*"
        r"(?P<target_value>\S+)$"
    )

    for log in log_dir.iterdir():
        if log.suffix != ".out":
            continue
        with log.open(mode="r") as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    value = pdf_changed.loc[
                        (
                            match.group("objective"),
                            match.group("instance"),
                            int(match.group("run_id")),
                        ),
                        (match.group("solver"), match.group("config_id"), "Value"),
                    ]
                    if (isinstance(value, float) and math.isnan(value)) or (
                        isinstance(value, str) and value.lower() == "nan"
                    ):
                        continue
                    assert str(value) == str(match.group("target_value"))

    # 3. TODO: Check that the values make sense (?)
