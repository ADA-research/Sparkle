"""Test the add solver CLI entry point."""
import pytest
from pathlib import Path
import subprocess


@pytest.mark.integration
def test_add_solver_command(tmp_path: Path) -> None:
    """Test initialise command."""
    # Smoke test
    solver_path = Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic"
    call = subprocess.run(["sparkle", "add", "solver", solver_path.absolute()],
                          cwd=tmp_path)
    assert call.returncode == 0
