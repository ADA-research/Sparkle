"""Test the run ablation CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, run_ablation, add_solver, add_instances

from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_run_ablation_command(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run ablation command."""
    snapshot_path = (
        Path("tests") / "CLI" / "test_files"
        / "snapshot_configured_validated_solver_Pb0-CCSAT-Generic_PTN.zip").absolute()
    solver_pbo_path = (
        Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic").absolute()
    train_set_path = (
        Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    test_set_path = (
        Path("Examples") / "Resources" / "Instances" / "PTN2").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add solver
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_pbo_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add train instances
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(train_set_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add test instances
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(test_set_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_ablation.main(["--solver", solver_pbo_path.name,
                           "--instance-set-train", train_set_path.name,
                           "--instance-set-test", test_set_path.name])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
