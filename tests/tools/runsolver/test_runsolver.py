"""Test methods for RunSolver class."""

import pytest
import shutil

from pathlib import Path
from sparkle.platform import Settings
from sparkle.solver import Solver
from sparkle.tools.runsolver.runsolver import RunSolver
from sparkle.types import SolverStatus, resolve_objective


def test_get_measurements(tmp_path: Path) -> None:
    """Tests parsing of the .val file."""
    val_file = tmp_path / "run.val"
    # Test with a full file
    val_file.write_text("WCTIME=10.5\nCPUTIME=9.8\nMAXVM=20480")
    cpu, wall, mem = RunSolver.get_measurements(val_file)
    assert cpu == 9.8
    assert wall == 10.5
    assert mem == 20.0  # 20480 KiB -> 20.0 MB

    # Test with a missing file
    val_file.unlink()
    cpu, wall, mem = RunSolver.get_measurements(val_file)
    assert cpu == -1.0
    assert wall == -1.0
    assert mem == -1.0


def test_get_status(tmp_path: Path) -> None:
    """Tests get status."""
    val_file = tmp_path / "run.val"
    raw_file = tmp_path / "run.rawres"

    # Case 1: No log files exist -> CRASHED
    assert RunSolver.get_status(val_file, raw_file) == SolverStatus.CRASHED

    # Case 2: .val file indicates TIMEOUT -> TIMEOUT
    val_file.write_text("TIMEOUT=true")
    assert RunSolver.get_status(val_file, raw_file) == SolverStatus.TIMEOUT

    # Case 3: .val file exists but .rawres does not -> KILLED
    val_file.write_text("TIMEOUT=false")
    assert RunSolver.get_status(val_file, raw_file) == SolverStatus.KILLED

    # Case 4: Both files exist, parse status from .rawres -> SUCCESS
    raw_file.write_text(
        "... some solver output ...\nFinal result: {'status': 'SUCCESS'}"
    )
    assert RunSolver.get_status(val_file, raw_file) == SolverStatus.SUCCESS


def test_get_solver_output(tmp_path: Path) -> None:
    """Tests get solver output."""
    val_file = tmp_path / "run.val"
    raw_file = tmp_path / "run.rawres"
    watch_file = tmp_path / "run.log"

    val_file.write_text("CPUTIME=15.0\nWCTIME=16.0\nMAXVM=10240")
    raw_file.write_text("Solver output line\n{'status': 'SUCCESS', 'quality': 123}")
    watch_file.write_text(
        "command line: ... sparkle_solver_wrapper {'cutoff_time': '30', "
        "'objectives': 'runtime,quality'}"
    )

    config = [
        "--cpu-limit",
        "30",
        "-v",
        str(val_file),
        "-o",
        str(raw_file),
        "-w",
        str(watch_file),
    ]
    result = RunSolver.get_solver_output(config, "")

    assert result["status"] == SolverStatus.SUCCESS
    assert result["cpu_time"] == 15.0
    assert result["wall_time"] == 16.0
    assert result["memory"] == 10.0  # 10240 KiB -> 10 MB
    assert result["quality"] == 123
    assert result["cutoff_time"] == 30.0


def test_get_solver_output_timeout_override(tmp_path: Path) -> None:
    """Tests if high CPU time overrides status to TIMEOUT."""
    val_file = tmp_path / "run.val"
    raw_file = tmp_path / "run.rawres"

    # CPU time (35s) is greater than cutoff (30s)
    val_file.write_text("CPUTIME=35.0")
    raw_file.write_text("{'status': 'SUCCESS'}")

    config = ["--cpu-limit", "30", "-v", str(val_file), "-o", str(raw_file)]
    result = RunSolver.get_solver_output(config, "")

    assert result["status"] == SolverStatus.TIMEOUT


@pytest.mark.integration
def test_runsolver_versus_pyrunsolver(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that RunSolver and PyRunSolver produce the (near) same results."""
    if (
        not Settings.DEFAULT_runsolver_exec.exists()
    ):  # Check that Runsolver exists, else return
        return

    # command line: /home/snelleman/Sparkle/Solvers/PbO-CCSAT-Generic/runsolver --timestamp --use-pty --cpu-limit 60 -w Output/Log/run_solvers_2025-10-02-14.28.24/Ptn-7824-b13.cnf_PbO-CCSAT-Generic_2025-10-02-14:28:24_1707148_1782621243.log -v Output/Log/run_solvers_2025-10-02-14.28.24/Ptn-7824-b13.cnf_PbO-CCSAT-Generic_2025-10-02-14:28:24_1707148_1782621243.val -o Output/Log/run_solvers_2025-10-02-14.28.24/Ptn-7824-b13.cnf_PbO-CCSAT-Generic_2025-10-02-14:28:24_1707148_1782621243.rawres Solvers/PbO-CCSAT-Generic/sparkle_solver_wrapper.sh '{"solver_dir": "/home/snelleman/Sparkle/Solvers/PbO-CCSAT-Generic", "instance": "Instances/PTN/Ptn-7824-b13.cnf", "seed": "1167250818", "objectives": "PAR10,status:metric,cpu_time:metric,wall_time:metric,memory:metric", "cutoff_time": "60"}'
    # Run PbO-CSCCAT-Generic on Ptn-7824-b13.cnf with default conf and seed 1167250818, should be done in ~23 seconds
    solver_path_source = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    instance_path_source = Path(
        "Examples/Resources/Instances/PTN/Ptn-7824-b13.cnf"
    ).absolute()
    runsolver_path_source = Settings.DEFAULT_runsolver_exec.absolute()
    seed = 1167250818
    objective = resolve_objective("PAR10")
    monkeypatch.chdir(tmp_path)

    solver_path = Path(solver_path_source.name)
    instance_path = Path(instance_path_source.name)

    # Setup solver and instance
    shutil.copytree(solver_path_source, solver_path)
    shutil.copy(instance_path_source, instance_path)
    solver = Solver(solver_path)

    # Run without Runsolver e.g. PyRunSolver
    pysolver_output = solver.run(
        instances=str(instance_path), objectives=[objective], seed=seed, cutoff_time=60
    )

    shutil.copy(runsolver_path_source, solver_path / runsolver_path_source.name)
    runsolver_output = solver.run(
        instances=str(instance_path), objectives=[objective], seed=seed, cutoff_time=60
    )

    # Verify that the discrete results are the same
    assert pysolver_output["status"] == runsolver_output["status"]
    assert pysolver_output["quality"] == runsolver_output["quality"]
    assert pysolver_output["memory"] == runsolver_output["memory"]

    # Assume the results are 'similar'
    # The metrics will diverge a bit but they all should be within 2 points of eachother
    measurement_threshold = 2
    cpu_distance = abs(pysolver_output["cpu_time"] - runsolver_output["cpu_time"])
    assert cpu_distance <= measurement_threshold, (
        f"WARNING: Measured CPU time variance is {cpu_distance} > {measurement_threshold} (Runsolver: {runsolver_output['cpu_time']}, PyRunSolver: {pysolver_output['cpu_time']})"
    )
    wall_distance = abs(pysolver_output["wall_time"] - runsolver_output["wall_time"])
    assert wall_distance <= measurement_threshold, (
        f"WARNING: Measured CPU time variance is {wall_distance} > {measurement_threshold} (Runsolver: {runsolver_output['wall_time']}, PyRunSolver: {pysolver_output['wall_time']})"
    )
