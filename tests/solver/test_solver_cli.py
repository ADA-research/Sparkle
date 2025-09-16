"""Tests for Solver CLI entry point."""

import pytest
from pathlib import Path
import shutil

from tests.CLI import tools as cli_tools

from sparkle.solver import Solver, solver_cli
from sparkle.structures import PerformanceDataFrame

from runrunner.base import Runner, Status
from runrunner.slurm import SlurmRun


def test_solver_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the Solver CLI entry point."""
    solver_path = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    instance_path = Path("Examples/Resources/Instances/PTN/Ptn-7824-b01.cnf").absolute()
    monkeypatch.chdir(tmp_path)

    pdf = PerformanceDataFrame(
        Path("performance_data.csv"),
        solvers=[solver_path.name],
        instances=[instance_path.name],
        objectives=["PAR10"],
    )

    solver_cli.main(
        [
            "--performance-dataframe",
            str(pdf.csv_filepath),
            "--solver",
            str(solver_path),
            "--instance",
            str(instance_path),
            "--seed",
            "0",
            # "--objective",
            # "PAR10",
            "--cutoff-time",
            "60",
            "--run-index",
            "0",
            "--log-dir",
            str(tmp_path),
        ]
    )


@pytest.mark.performance
def test_solver_cli_performance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the Solver CLI entry point with high concurrency.

    Verifies whether the results placed in the PerformanceDataFrame are correct.
    """
    cluster_name = cli_tools.get_cluster_name()
    if cluster_name != "kathleen":
        raise Exception("Performance test only available on Kathleen")
    cluster_settings = cli_tools.get_cluster_settings()

    pdf_source = Path(
        "tests/test_files/performance/example-high-concurrency.csv"
    ).absolute()
    solver = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    instances = Path("Examples/Resources/Instances/PTN").absolute()
    monkeypatch.chdir(tmp_path)
    pdf_target = Path("performance_data.csv")
    solver_target = Path("PbO-CCSAT-Generic")
    instances_target = Path("Instances/PTN")
    shutil.copyfile(pdf_source, pdf_target)
    shutil.copytree(solver, solver_target)
    shutil.copytree(instances, instances_target)

    # This DataFrame only has the Default configuration evaluated
    # And 50 new configurations that are not evaluated at all
    original_pdf = PerformanceDataFrame(pdf_target)

    solver = Solver(solver_target)
    config_ids = original_pdf.configuration_ids
    config_ids.remove(PerformanceDataFrame.default_configuration)
    # process remaining jobs into a format accesible by the solver

    # Execute all remaining jobs
    run: SlurmRun = solver.run_performance_dataframe(
        instances=original_pdf.instances,
        config_ids=config_ids,
        performance_dataframe=original_pdf,
        train_set=None,
        dependencies=None,
        cutoff_time=cluster_settings.solver_cutoff_time,
        sbatch_options=cluster_settings.sbatch_settings,
        slurm_prepend=cluster_settings.slurm_job_prepend,
        log_dir=tmp_path,
        base_dir=tmp_path,
        job_name="Performance Load Test PerformanceDataFrame",
        run_on=Runner.SLURM,
    )
    run.wait()  # await the job

    assert run.status == Status.COMPLETED
    # 1. Check that the original results are left unchanged

    # 2. Check that all values are now filled in

    # 3. Check that the values make sense (?)
