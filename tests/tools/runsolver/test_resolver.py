"""Test methods for RunSolverResolver class."""

from pathlib import Path
from unittest.mock import patch, MagicMock

from sparkle.tools.runsolver.resolver import RunSolverResolver


@patch("sparkle.tools.runsolver.resolver.PyRunSolver")
@patch("sparkle.tools.runsolver.resolver.RunSolver")
def test_resolver_uses_runsolver_if_exists(
    mock_runsolver: MagicMock, mock_pyrunsolver: MagicMock, tmp_path: Path
) -> None:
    """Verify that the C++-based RunSolver is used when its executable exists."""
    mock_executable = MagicMock(spec=Path)
    mock_executable.exists.return_value = True

    RunSolverResolver.wrap_command(
        runsolver_executable=mock_executable,
        command=["solver"],
        cutoff_time=100,
        log_directory=tmp_path,
    )

    mock_runsolver.wrap_command.assert_called_once()
    mock_pyrunsolver.wrap_command.assert_not_called()


@patch("sparkle.tools.runsolver.resolver.PyRunSolver")
@patch("sparkle.tools.runsolver.resolver.RunSolver")
def test_resolver_uses_pyrunsolver_if_not_exists(
    mock_runsolver: MagicMock, mock_pyrunsolver: MagicMock, tmp_path: Path
) -> None:
    """Verify that the Python-based PyRunSolver is used when the C++ executable is missing."""
    mock_executable = MagicMock(spec=Path)
    mock_executable.exists.return_value = False

    RunSolverResolver.wrap_command(
        runsolver_executable=mock_executable,
        command=["solver"],
        cutoff_time=100,
        log_directory=tmp_path,
    )

    mock_runsolver.wrap_command.assert_not_called()
    mock_pyrunsolver.wrap_command.assert_called_once()
