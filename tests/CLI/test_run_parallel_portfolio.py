"""Test the parallel portfolio CLI entry point."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import csv
import argparse

from sparkle.solver import Solver
from sparkle.instance import FileInstanceSet
from sparkle.CLI.run_parallel_portfolio import run_parallel_portfolio, \
    main, parser_function
from sparkle.types import SolverStatus
from sparkle.CLI.help import global_variables as gv
from runrunner.base import Runner
from runrunner.slurm import Status
from types import SimpleNamespace

solver_pbo = Solver(Path("Solvers/CSCCSat/"))
solver_csccsat = Solver(Path("Solvers/MiniSAT/"))
solver_minisat = Solver(Path("Solvers/PbO-CCSAT-Generic"))
solvers = [solver_pbo, solver_csccsat, solver_minisat]
instance_path = Path("tests/test_files/Instances/Train-Instance-Set/")
sparkle_objectives = [str(obj) for obj in gv.settings().get_general_sparkle_objectives()]
expected_headers = ["Instance", "Solver"] + sparkle_objectives
portfolio_path = Path("tests/test_files/Output/Parallel_Portfolio/"
                      "Raw_Data/runtime_experiment/")


class FakeJob:
    """FakeJob Class to mimick the behavior of run jobs."""

    def __init__(self: FakeJob, status: Status, stdout: str = "dummy output") -> None:
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


@pytest.mark.parametrize(
    "stdout, statuses", [
        ('{"solver_dir": "/dummy/dir",'
         '"instance": "train_instance_1.cnf",'
         '"seed": "123", "objectives": "dummy",'
         '"cutoff_time": "60", "status": "UNKNOWN"}',
         [Status.COMPLETED,
          Status.KILLED,
          Status.COMPLETED,
          Status.UNKNOWN,
          Status.KILLED,
          Status.KILLED])
    ]
)
def test_run_parallel_portfolio(stdout: str, statuses: list[Status]) -> None:
    """Test run_parallel_portfolio function."""
    portfolio_path.mkdir(parents=True, exist_ok=True)

    instance = FileInstanceSet(instance_path)
    return_val = 0
    csv_path = portfolio_path / "results.csv"
    assert not csv_path.exists(), (
        "results.csv should not exist."
    )
    with patch("sparkle.CLI.run_parallel_portfolio.time.sleep", return_value=None), \
         patch("sparkle.CLI.run_parallel_portfolio.tqdm") as mock_tqdm, \
         patch("sparkle.CLI.run_parallel_portfolio.rrr.add_to_queue") as \
         mock_add_to_queue:

        fake_pbar = MagicMock()
        fake_pbar.set_description.return_value = None
        fake_pbar.update.return_value = None
        mock_tqdm.return_value.__enter__.return_value = fake_pbar
        num_jobs = len(solvers) * 2
        fake_jobs = [
            FakeJob(statuses[i], stdout=stdout)
            for i in range(num_jobs)
        ]
        fake_run = SimpleNamespace(jobs=fake_jobs)
        mock_add_to_queue.return_value = fake_run

        return_val = run_parallel_portfolio(instance, portfolio_path, solvers)
    assert return_val is None, (
        "run_parallel_portfolio should return None."
    )

    solvers_as_str = ["CSCCSat", "MiniSAT", "PbO-CCSAT-Generic"]

    # Check if results.csv created and results are written there as expected
    assert csv_path.exists(), (
        "results.csv should have been created."
    )
    with csv_path.open("r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        assert reader.fieldnames == expected_headers, (
            f"CSV headers do not match. Got {reader.fieldnames}"
        )

        for row in reader:
            # We have just 1 instance, check if all instances are that instance
            assert row["Instance"] == "train_instance_1.cnf", (
                f"Instance column should be train_instance_1.cnf, got {row['Instance']}"
            )

            # Check if current solver in used solvers list
            assert row["Solver"] in solvers_as_str, (
                f"Solver {row['Solver']} not in allowed list {solvers_as_str}"
            )

            # PAR10, cpu_time:metric, wall_time:metric, memory:metric should be numbers
            try:
                float(row["PAR10"])
            except ValueError:
                pytest.fail(f"PAR10 value '{row['PAR10']}' is not valid.")

            status_val = row["status:metric"].strip().upper()
            assert SolverStatus[status_val], (
                f"Status '{status_val}' not recognized in row {row}"
            )

            for col in ["cpu_time:metric", "wall_time:metric", "memory:metric"]:
                try:
                    float(row[col])
                except ValueError:
                    pytest.fail(
                        f"Column '{col}' has non-numeric value '{row[col]}' in row {row}"
                    )

    # Delete the results.csv file and check if deleted
    csv_path.unlink()
    assert not csv_path.exists(), (
        "results.csv should have been deleted."
    )


def test_parser_function() -> None:
    """Test function for parser function of run_parallel_portfilio."""
    expected_description = "Run a portfolio of solvers on an" \
        " instance set in parallel."
    returned_parser = parser_function()
    assert returned_parser.description == expected_description
    assert isinstance(returned_parser, argparse.ArgumentParser)


instance_path_list = [f"--instance-path {instance_path}"]
portfolio_name_list = [f"--portfolio-name {portfolio_path}"]
solvers_list = ["--solvers Solvers/CSCCSat/,\
                Solvers/PbO-CCSAT-Generic,Solvers/MiniSAT/"]
objectives_list = ["--objectives PAR10,status:metric,\
                   cpu_time:metric,wall_time:metric,memory:metric"]
cutoff_time_list = [f"--cutoff-time {55}"]
solver_seeds_list = [f"--solver-seeds {2}"]
settings_list = [f"--settings-file {Path('Settings/latest.ini')}"]
run_on_local_list = [f"--run-on {Runner.LOCAL}"]
run_on_slurm_list = [f"--run-on {Runner.SLURM}"]


@pytest.mark.parametrize(
    "case", [
        "solver_none",
        "run_on_local",
        "first_objective_not_time",
        "porfolio_name_none"
    ]
)
def test_main(case: str) -> None:
    """Test main function from run_parallel_portfolio."""
    args = []
    args += instance_path_list + cutoff_time_list + solver_seeds_list + settings_list
    if case == "solver_none":
        solvers_list_with_none = ["--solvers Solvers/CSCCSat/,\
                                  Solvers/PbO-CCSAT-Generic,Solvers/MiniSAT/,None"]
        args += portfolio_name_list + run_on_slurm_list +\
            solvers_list_with_none + objectives_list
        with pytest.raises(SystemExit) as excinfo:
            main(args)
        assert excinfo.value.code == -1, ("Expected exit code -1,"
                                          f"got {excinfo.value.code}")
    elif case == "run_on_local":
        args += portfolio_name_list + run_on_local_list + solvers_list + objectives_list
        with pytest.raises(SystemExit) as excinfo:
            main(args)
        assert excinfo.value.code == -1, ("Expected exit code -1,"
                                          f"got {excinfo.value.code}")
        assert str(gv.settings().get_run_on()).lower() == "local", (
            f"Expected run_on setting to be 'local', got {gv.settings().get_run_on()}"
        )
    elif case == "first_objective_not_time":
        sparkle_objectives[0] = "TEST"
        objectives_list_changed = [f"--objectives {sparkle_objectives}"]
        args += portfolio_name_list + run_on_slurm_list +\
            solvers_list + objectives_list_changed
        with pytest.raises(SystemExit) as excinfo:
            main(args)
        assert excinfo.value.code == -1, ("Expected exit code -1,"
                                          f"got {excinfo.value.code}")
    else:
        # portfolio name is none
        args = args + run_on_slurm_list +\
            solvers_list + objectives_list
        return_val = main(args)
        assert return_val is None, ("Expected return val was None.")
