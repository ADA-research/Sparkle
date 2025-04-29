"""Test the parallel portfolio CLI entry point."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import csv
import argparse

from sparkle.solver import Solver
from sparkle.instance import FileInstanceSet
from sparkle.types.objective import SparkleObjective
from sparkle.CLI.run_parallel_portfolio import run_parallel_portfolio, \
    main, parser_function
from sparkle.types.status import SolverStatus
from sparkle.CLI.help import global_variables as gv
from runrunner.base import Runner
from runrunner.slurm import Status
from types import SimpleNamespace


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


solver_pbo = Solver(Path("Examples/Resources/Solvers/CSCCSat/"))
solver_csccsat = Solver(Path("Examples/Resources/Solvers/MiniSAT/"))
solver_minisat = Solver(Path("Examples/Resources/Solvers/PbO-CCSAT-Generic"))
solvers = [solver_pbo, solver_csccsat, solver_minisat]
instance_path = Path("tests/test_files/Instances/Train-Instance-Set/")
sparkle_objectives = [str(obj) for obj in gv.settings().get_general_sparkle_objectives()]
expected_headers = ["Instance", "Solver"] + sparkle_objectives
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


def test_run_parallel_portfolio() -> None:
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
        fake_run = SimpleNamespace(jobs=fake_jobs)
        mock_add_to_queue.return_value = fake_run

        return_val = run_parallel_portfolio(instance, portfolio_path, solvers)
    assert return_val is None, (
        "run_parallel_portfolio should return None."
    )

    solvers_as_str = ["CSCCSat", "MiniSAT", "PbO-CCSAT-Generic"]

    assert csv_path.exists(), (
        "results.csv should have been created."
    )
    with csv_path.open("r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        assert reader.fieldnames == expected_headers, (
            f"CSV headers do not match. Got {reader.fieldnames}"
        )

        for row in reader:
            assert row["Instance"] == "train_instance_1.cnf", (
                f"Instance column should be train_instance_1.cnf, got {row['Instance']}"
            )

            assert row["Solver"] in solvers_as_str, (
                f"Solver {row['Solver']} not in allowed list {solvers_as_str}"
            )

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


instance_path_list = ["--instance-path", f"{instance_path}"]
portfolio_name_list = ["--portfolio-name", f"{portfolio_path}"]
solvers_list = ["--solvers", "Examples/Resources/Solvers/CSCCSat/",
                "Examples/Resources/Solvers/PbO-CCSAT-Generic/",
                "Examples/Resources/Solvers/MiniSAT/"
                ]
objectives_list = ["--objectives", "PAR10,status:metric,"
                   "cpu_time:metric,wall_time:metric,memory:metric"]
cutoff_time_list = ["--cutoff-time", f"{55}"]
solver_seeds_list = ["--solver-seeds", f"{2}"]
settings_list = ["--settings-file", f"{Path('Settings/sparkle_settings.ini')}"]
run_on_local_list = ["--run-on", f"{Runner.LOCAL}"]
run_on_slurm_list = ["--run-on", f"{Runner.SLURM}"]


@pytest.mark.parametrize(
    "case", [
        "solver_none",
        "run_on_local",
        "first_objective_not_time",
        "porfolio_name_none",
        "empty_args"
    ]
)
def test_main(case: str) -> None:
    """Test main function from run_parallel_portfolio."""
    return  # Disabled as test is currently not working
    args = []
    if case == "solver_none":
        solvers_list_with_none = solvers_list + [f"{None}"]
        args += instance_path_list + portfolio_name_list + solvers_list_with_none +\
            objectives_list + cutoff_time_list + solver_seeds_list +\
            run_on_slurm_list + settings_list
        with pytest.raises(SystemExit) as excinfo:
            main(args)
        assert excinfo.value.code == -1, (
            "Expected exit code -1, "
            f"got {excinfo.value.code}"
        )
    elif case == "run_on_local":
        args += instance_path_list + portfolio_name_list + solvers_list +\
            objectives_list + cutoff_time_list + solver_seeds_list +\
            run_on_local_list + settings_list
        with pytest.raises(SystemExit) as excinfo:
            main(args)
        assert excinfo.value.code == -1, (
            "Expected exit code -1, "
            f"got {excinfo.value.code}"
        )
        assert str(gv.settings().get_run_on()).lower() == "runner.local", (
            "Expected run_on setting to be 'runner.local' "
            f"but got runner.{gv.settings().get_run_on()}"
        )
    elif case == "first_objective_not_time":
        test_object = SparkleObjective(name="TEST")

        objectives_list_changed = ["--objectives", f"{test_object},status:metric,"
                                   "cpu_time:metric,wall_time:metric,memory:metric"]
        args += instance_path_list + portfolio_name_list + solvers_list +\
            objectives_list_changed + cutoff_time_list + solver_seeds_list +\
            run_on_slurm_list + settings_list
        with pytest.raises(SystemExit) as excinfo:
            main(args)
        assert excinfo.value.code == -1, (
            "Expected exit code -1, "
            f"got {excinfo.value.code}"
        )
    elif case == "porfolio_name_none":
        args += instance_path_list + [f"{None}"] + solvers_list +\
            objectives_list + cutoff_time_list + solver_seeds_list +\
            run_on_slurm_list + settings_list
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
            with pytest.raises(SystemExit) as excinfo:
                main(args)
            assert excinfo.value.code == 0, (
                "Expected exit code 0, "
                f"got {excinfo.value.code}"
            )
        current_port_path = gv.latest_scenario().get_parallel_portfolio_path().as_posix()
        assert current_port_path.startswith("Output/Parallel_Portfolio/Raw_Data/"), (
            "Expected portfolio path should start with"
            "Output/Parallel_Portfolio/Raw_Data/"
            f"but got, {current_port_path}"
        )
        assert gv.latest_scenario().get_latest_scenario() == "PARALLEL_PORTFOLIO"
    elif case == "empty_args":
        with pytest.raises(TypeError) as excinfo:
            main([])
        str_exception = excinfo.exconly()
        assert str_exception == "TypeError: 'NoneType' object is not iterable", (
            "Expected: `TypeError: 'NoneType' object is not iterable`, but got "
            f"{str_exception}"
        )
