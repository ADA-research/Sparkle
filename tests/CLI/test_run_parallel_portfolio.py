"""Test the parallel portfolio CLI entry point."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import argparse

from sparkle.solver import Solver
from sparkle.instance import FileInstanceSet
from sparkle.CLI import run_parallel_portfolio as rpp
from sparkle.types.status import SolverStatus
from runrunner.base import Runner
from runrunner.slurm import Status
from types import SimpleNamespace


class FakeJob:
    """FakeJob Class to mimick the behavior of run jobs."""

    def __init__(self: FakeJob, status: Status, stdout: str) -> None:
        """Initialize FakeJob.

        Args:
            status: Status of runrunner
            stdout: Output of solver
        """
        self.status: Status = status
        self.stdout: str = stdout

    def kill(self: FakeJob) -> SolverStatus:
        """If called, set status to KILLED."""
        self.status: SolverStatus = SolverStatus.KILLED


solver_paths = [
    Path("Examples/Resources/Solvers/CSCCSat"),
    Path("Examples/Resources/Solvers/PbO-CCSAT-Generic"),
    Path("Examples/Resources/Solvers/MiniSAT")
]
solvers = [Solver(path) for path in solver_paths]

instance_path = Path("tests/test_files/Instances/Train-Instance-Set/")
instance_file = FileInstanceSet(instance_path)
single_instances_str = [str(instance) for instance in instance_file.instance_names]

sparkle_objectives = ["PAR10", "status:metric", "cpu_time:metric", "wall_time:metric",
                      "memory:metric"]
portfolio_path = Path("tests/test_files/Output/Parallel_Portfolio/"
                      "Raw_Data/runtime_experiment/")
stdout = ('{"solver_dir": "/dummy/dir",'
          '"instance": "train_instance_1.cnf",'
          '"seed": "123", "objectives": "dummy",'
          '"cutoff_time": "60", "status": "UNKNOWN"}')
statuses = [Status.COMPLETED, Status.KILLED, Status.COMPLETED,
            Status.UNKNOWN, Status.KILLED, Status.KILLED
            ]
num_jobs = len(solvers) * 2
fake_jobs = [FakeJob(statuses[i], stdout=stdout) for i in range(num_jobs)]


@pytest.mark.integration
def test_run_parallel_portfolio(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test for run_parallel_portfolio function."""
    pdf = rpp.create_performance_dataframe(solvers, instance_file, portfolio_path)
    returned_cmd = rpp.build_command_list(instance_file, solvers, portfolio_path, pdf)
    assert type(returned_cmd) is list
    for element in returned_cmd:
        assert type(element) is str

    [r_default_objective_values,
     r_cpu_time, r_status, r_wall_time] = rpp.init_default_objectives()
    assert type(r_default_objective_values) is dict
    assert r_cpu_time == "cpu_time:metric"
    assert r_status == "status:metric"
    assert r_wall_time == "wall_time:metric"

    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    with patch("sparkle.CLI.run_parallel_portfolio.time.sleep", return_value=None), \
         patch("sparkle.CLI.run_parallel_portfolio.tqdm") as mock_tqdm, \
         patch("sparkle.CLI.run_parallel_portfolio.rrr.add_to_queue") as \
         mock_add_to_queue:

        fake_pbar = MagicMock()
        fake_pbar.set_description.return_value = None
        fake_pbar.update.return_value = None
        mock_tqdm.return_value.__enter__.return_value = fake_pbar
        fake_run = SimpleNamespace(jobs=fake_jobs)
        mock_add_to_queue.return_value = fake_run

        returned_run = rpp.submit_jobs(returned_cmd, solvers,
                                       instance_file, Runner.SLURM
                                       )
        assert type(returned_run) is SimpleNamespace

        job_output_dict = rpp.monitor_jobs(returned_run, instance_file,
                                           solvers, r_default_objective_values)
        assert type(job_output_dict) is dict

        assert rpp.wait_for_logs(returned_cmd) is None

        job_output_dict = rpp.update_results_from_logs(returned_cmd,
                                                       returned_run,
                                                       solvers,
                                                       job_output_dict,
                                                       r_cpu_time
                                                       )
        assert type(job_output_dict) is dict

        job_output_dict = rpp.fix_missing_times(job_output_dict,
                                                r_status, r_cpu_time, r_wall_time)
        assert type(job_output_dict) is dict

        portfolio_path.mkdir(parents=True, exist_ok=True)
        csv_path = portfolio_path / "results.csv"
        csv_path.unlink(missing_ok=True)
        rpp.print_and_write_results(job_output_dict, solvers,
                                    instance_file, portfolio_path,
                                    r_status, r_cpu_time, r_wall_time, pdf) is None

        assert csv_path.exists(), (
            "results.csv should have been created."
        )

        assert pdf.num_instances == len([instance_file.all_paths]), (
            "Expected number of instances in pdf to "
            f"be equal to {len([instance_file.all_paths])} "
            f"in the instance set, but got {pdf.num_instances}."
        )
        for instance_path in pdf.instances:
            assert instance_path in single_instances_str, (
                "Expected instances in pdf to be in the instance set "
                f"{single_instances_str}, but got {instance_path}."
            )

        assert pdf.num_solvers == len(solvers), (
            f"Expected number of solvers in pdf to be equal to {len(solvers)} "
            f"in the solvers list, but got {pdf.num_solvers}."
        )

        assert pdf.num_objectives == len(sparkle_objectives), (
            "Expected number of objectives in pdf to "
            f"be equal to {len(sparkle_objectives)}, "
            f"in the settings, but got {pdf.num_objectives}."
        )
        for objective in pdf.objectives:
            assert objective.name in sparkle_objectives, (
                "Expected objectives in pdf to be in "
                "the objectives in the settings "
                f"{sparkle_objectives}, but got {objective.name}."
            )


def test_parser_function() -> None:
    """Test for parser function."""
    expected_description = "Run a portfolio of solvers on an "\
        "instance set in parallel."
    returned_parser = rpp.parser_function()
    assert returned_parser.description == expected_description
    assert isinstance(returned_parser, argparse.ArgumentParser)
