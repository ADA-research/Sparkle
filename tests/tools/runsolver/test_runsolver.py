"""Test methods for RunSolver class."""

from pathlib import Path
from sparkle.tools.runsolver.runsolver import RunSolver
from sparkle.types import SolverStatus


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
