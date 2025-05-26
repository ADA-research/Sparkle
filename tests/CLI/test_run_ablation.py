"""Test the run ablation CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, run_ablation

from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_run_ablation_command(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run ablation command."""
    settings_path = cli_tools.get_settings_path()
    snapshot_path = (
        Path("tests") / "CLI" / "test_files"
        / "snapshot_configured_solver_Pb0-CCSAT-Generic_PTN").absolute()
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

    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_ablation.main(["--solver", solver_pbo_path.name,
                           "--instance-set-train", train_set_path.name,
                           "--instance-set-test", test_set_path.name,
                           "--settings-file", str(settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
