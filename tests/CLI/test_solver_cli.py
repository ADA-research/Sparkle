"""Test the solver CLI entry points."""
import pytest
from pathlib import Path
import shutil

from sparkle.CLI import add_solver, remove_solver, run_solvers
from sparkle.CLI import add_instances
from tests.CLI import tools as cli_tools


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


@pytest.mark.integration
def test_run_solvers(tmp_path: Path,
                     monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run solvers command."""
    solver_path = (Path("Examples") / "Resources" / "Solvers" / "CSCCSat").absolute()
    instances_path = (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    settings_path = cli_tools.get_settings_path()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Smoke test
    # First we add solvers and instances to the platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(instances_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Second we test the command twice, once with local and once with slurm
    # NOTE: Expensive local test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--run-on", "local",
                          "--settings-file", str(settings_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Check if testing with Slurm is relevant for system
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--run-on", "slurm",
                          "--settings-file", str(settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
