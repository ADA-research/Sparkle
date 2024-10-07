"""Test the initiliase CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import (load_snapshot, add_instances, add_solver,
                         validate_configured_vs_default)
from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_validate_configured_vs_default_command(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    configured_snapshot = (
        Path("tests") / "CLI" / "test_files"
        / "snapshot_configured_solver_Pb0-CCSAT-Generic_PTN.zip").absolute()
    # The Solver and data sets are not in the snapshot to reduce snapshot size
    solver_path = Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute()
    train_set_path = Path("Examples/Resources/Instances/PTN").absolute()
    test_set_path = Path("Examples/Resources/Instances/PTN2").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform for test
    # Load snapshot
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(configured_snapshot)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # Re-add train data set
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(train_set_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # Re-add test data set
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(test_set_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # Re-add solver
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Smoke test for configured vs default LOCAL
    # TODO: Fix bug in Sparkle / RunRunner so this command works ony local

    # Smoke test for configured vs default SLURM
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        validate_configured_vs_default.main(["--solver", solver_path.name,
                                             "--instance-set-train", train_set_path.name,
                                             "--instance-set-test", test_set_path.name,
                                             "--run-on", "slurm"])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Smoke test for configured vs default SLURM with only a train set argument
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        validate_configured_vs_default.main(["--solver", solver_path.name,
                                             "--instance-set-train", train_set_path.name,
                                             "--run-on", "slurm"])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
