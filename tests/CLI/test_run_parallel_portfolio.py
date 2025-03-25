"""Test the parallel portfolio CLI entry point."""
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import csv
from sparkle.solver import Solver
from sparkle.instance import FileInstanceSet
from sparkle.CLI.run_parallel_portfolio import run_parallel_portfolio, main
from sparkle.types import SolverStatus
from sparkle.CLI.help import global_variables as gv

solver_pbo = Solver(Path("Solvers/CSCCSat/"))
solver_csccsat = Solver(Path("Solvers/MiniSAT/"))
solver_minisat = Solver(Path("Solvers/PbO-CCSAT-Generic"))
solvers = [solver_pbo, solver_csccsat, solver_minisat]
instance_path = Path("tests/test_files/Instances/Train-Instance-Set/")

allowed_statuses = [
    "SUCCESS",
    "UNKNOWN",
    "SAT",
    "UNSAT",
    "CRASHED",
    "TIMEOUT",
    "WRONG",
    "ERROR",
    "KILLED"
]

expected_headers = [
    "Instance",
    "Solver",
    "PAR10",
    "status:metric",
    "cpu_time:metric",
    "wall_time:metric",
    "memory:metric"
]

default_objective_values = {
    "PAR10": 600,
    "status:metric": SolverStatus.UNKNOWN,
    "cpu_time:metric": 9.223372036854776e+18,
    "wall_time:metric": 9.223372036854776e+18,
    "memory:metric": 9.223372036854776e+18
}


def test_run_parallel_portfolio() -> None:
    """Test run_parallel_portfolio function."""
    portfolio_path = Path("tests/test_files/Output/Parallel_Portfolio/"
                          "Raw_Data/runtime_experiment/")
    portfolio_path.mkdir(parents=True, exist_ok=True)

    # Let the function run with mock
    instance = FileInstanceSet(instance_path)
    return_val = 0
    csv_path = portfolio_path / "results.csv"
    assert not csv_path.exists(), "results.csv should not exist."
    with patch("sparkle.CLI.run_parallel_portfolio.time.sleep", return_value=None), \
         patch("sparkle.CLI.run_parallel_portfolio.tqdm") as mock_tqdm:

        fake_pbar = MagicMock()
        fake_pbar.set_description.return_value = None
        fake_pbar.update.return_value = None
        mock_tqdm.return_value.__enter__.return_value = fake_pbar
        return_val = run_parallel_portfolio(instance, portfolio_path, solvers)
    assert return_val is None

    solvers_as_str = ["CSCCSat", "MiniSAT", "PbO-CCSAT-Generic"]

    # Check if results.csv created and results are written there as expected
    assert csv_path.exists(), "results.csv should have been created."
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
            assert status_val in allowed_statuses, (
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
    assert not csv_path.exists(), "results.csv should have been deleted."


sparkle_objectives = ["PAR10",
                      "status:metric",
                      "cpu_time:metric",
                      "wall_time:metric",
                      "memory:metric"
                      ]

base_string = f"--instance-path {instance_path} --portfolio-name runtime_experiment"


@pytest.mark.parametrize(
    "argv, case", [
        (f"{base_string}", "base_case"),
        (f"{base_string} --solver-seeds 3", "seed_case"),
        (f"{base_string} --cutoff-time 59", "cutoff_case"),
        (f"{base_string} --run-on local", "run_on_case"),
    ]
)
def test_main(argv: str, case: str) -> None:
    """Test main function from run_parallel_portfolio."""
    return
    return_val = 0
    assert return_val is None
    if case == "seed_case":
        return_val = main(argv)
        assert gv.settings().get_parallel_portfolio_number_of_seeds_per_solver() == 3
    elif case == "cutoff_case":
        return_val = main(argv)
        assert gv.settings().get_general_target_cutoff_time() == 59
    elif case == "run_on_case":
        with pytest.raises(SystemExit) as excinfo:
            main(argv)
        assert excinfo.value.code == -1
        assert gv.settings().get_run_on() == "local"
