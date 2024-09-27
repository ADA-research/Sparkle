"""Test the solver CLI entry points."""
import pytest
from pathlib import Path

from sparkle.CLI import add_solver, remove_solver


@pytest.mark.integration
def test_add_remove_solver_command(tmp_path: Path,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        solver_path = Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic"
        add_solver.main([str(solver_path.absolute())])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
        remove_solver.main([solver_path.name])
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0

# TODO: Test removing with solver directory path
# TODO: Test adding / removing with nicknames
# TODO: Test removing with non solver name/paths for failure
