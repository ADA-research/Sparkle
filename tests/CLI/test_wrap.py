"""Test the CLI wrap command."""

import os
import shutil
from pathlib import Path
import pytest

from sparkle.CLI.wrap import main
from sparkle.solver import Solver


@pytest.mark.integration
def test_wrap_exceptions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test wrap command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # No arguments
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 2

    # Wrap type does not exist
    with pytest.raises(Exception) as pytest_wrapped_e:
        main(["FalseType", "solver", "executable"])
    assert pytest_wrapped_e.type is ValueError

    # Path does not exist
    with pytest.raises(Exception) as pytest_wrapped_e:
        main(["Solver", "false_path/solver", "executable"])
    assert pytest_wrapped_e.type is ValueError

    # Executable does not exist
    with pytest.raises(Exception) as pytest_wrapped_e:
        main(
            [
                "Solver",
                "Examples/Resources/Solvers/PbO-CCSAT-Generic",
                "false_executable",
            ]
        )
    assert pytest_wrapped_e.type is ValueError


@pytest.mark.integration
def test_solver_wrap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the main entry point."""
    solver_path_source = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Copy Solver
    solver_path = Path(solver_path_source.name)
    shutil.copytree(solver_path_source, solver_path)

    # Remove current wrapper from copy
    solver_wrapper_path: Path = solver_path / f"{Solver._wrapper_file}.sh"
    solver_wrapper_path.unlink()

    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main(["Solver", str(solver_path), "PbO-CCSAT"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert solver_wrapper_path.exists()
    assert solver_wrapper_path.stat().st_mode & os.X_OK
    return
