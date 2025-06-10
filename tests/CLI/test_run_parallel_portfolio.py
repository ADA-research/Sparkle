"""Test the parallel portfolio CLI entry point."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import argparse

from sparkle.solver import Solver
from sparkle.instance import FileInstanceSet
from sparkle.types.objective import SparkleObjective
from sparkle.CLI import run_parallel_portfolio as rpp
from sparkle.types.status import SolverStatus
from sparkle.CLI.help import global_variables as gv
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


solver_pbo = Solver(Path("Examples/Resources/Solvers/CSCCSat/"))
solver_csccsat = Solver(Path("Examples/Resources/Solvers/MiniSAT/"))
solver_minisat = Solver(Path("Examples/Resources/Solvers/PbO-CCSAT-Generic"))
solvers = [solver_pbo, solver_csccsat, solver_minisat]
instance_path = Path("tests/test_files/Instances/Train-Instance-Set/")
instance = FileInstanceSet(instance_path)
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
    """Test for run_parallel_portfolio function."""
    returned_cmd = rpp.build_command_list(instance, solvers, portfolio_path)
    assert type(returned_cmd) is list
    for element in returned_cmd:
        assert type(element) is str

    [r_default_objective_values,
     r_cpu_time, r_status, r_wall_time] = rpp.init_default_objectives()
    assert type(r_default_objective_values) is dict
    assert r_cpu_time == "cpu_time:metric"
    assert r_status == "status:metric"
    assert r_wall_time == "wall_time:metric"

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

        returned_run = rpp.submit_jobs(returned_cmd, solvers, instance, Runner.SLURM)
        assert type(returned_run) is SimpleNamespace

        job_output_dict = rpp.monitor_jobs(returned_run, instance,
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
        rpp.print_and_write_results(job_output_dict, solvers, instance, portfolio_path,
                                    r_status, r_cpu_time, r_wall_time) is None

        # solvers_as_str = ["CSCCSat", "MiniSAT", "PbO-CCSAT-Generic"]
        assert csv_path.exists(), (
            "results.csv should have been created."
        )


def test_parser_function() -> None:
    """Test for parser function."""
    expected_description = "Run a portfolio of solvers on an "\
        "instance set in parallel."
    returned_parser = rpp.parser_function()
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
    args = []
    if case == "solver_none":
        solvers_list_with_none = solvers_list + [f"{None}"]
        args += instance_path_list + portfolio_name_list + solvers_list_with_none +\
            objectives_list + cutoff_time_list + solver_seeds_list +\
            run_on_slurm_list + settings_list
        with pytest.raises(SystemExit) as excinfo:
            rpp.main(args)
        assert excinfo.value.code == -1, (
            "Expected exit code -1, "
            f"got {excinfo.value.code}"
        )
    elif case == "run_on_local":
        args += instance_path_list + portfolio_name_list + solvers_list +\
            objectives_list + cutoff_time_list + solver_seeds_list +\
            run_on_local_list + settings_list
        with pytest.raises(SystemExit) as excinfo:
            rpp.main(args)
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
            rpp.main(args)
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
                rpp.main(args)
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
            rpp.main([])
        str_exception = excinfo.exconly()
        assert str_exception == "TypeError: 'NoneType' object is not iterable", (
            "Expected: `TypeError: 'NoneType' object is not iterable`, but got "
            f"{str_exception}"
        )
