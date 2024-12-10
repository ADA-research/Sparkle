"""Test the solver CLI entry points."""
import pytest
from pathlib import Path
import shutil

from sparkle.CLI import add_solver, remove_solver


@pytest.mark.integration
def test_add_remove_solver_command(tmp_path: Path,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    source_path = (Path("Examples") / "Resources" / "Solvers"
                   / "PbO-CCSAT-Generic").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Copy solver to tmp dir for no-copy test
    solver_path = Path("test") / "PbO-CCSAT-Generic"
    shutil.copytree(source_path, solver_path)

    expected_target = Path("Solvers") / solver_path.name
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert expected_target.exists()
    assert expected_target.is_dir()

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        remove_solver.main([solver_path.name])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert not expected_target.exists()

    # Symlink test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path.absolute()),
                         "--no-copy"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert expected_target.is_symlink()
    assert expected_target.is_dir()

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        remove_solver.main([solver_path.name])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert not expected_target.exists()
    # TODO: Test removing with solver directory path
    # TODO: Test adding / removing with nicknames
    # TODO: Test removing with non solver name/paths for failure
