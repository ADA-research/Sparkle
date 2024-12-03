"""Test the run configured solver CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, run_configured_solver

from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_run_configured_solver_command(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run configured solver command."""
    settings_path = cli_tools.get_settings_path()
    snapshot_path = (
        Path("tests") / "CLI" / "test_files"
        / "snapshot_configured_validated_solver_Pb0-CCSAT-Generic_PTN.zip").absolute()

    example_test_set_path = (
        Path("Examples") / "Resources" / "Instances" / "PTN2").absolute()
    example_test_file_path = (
        Path("Examples") / "Resources" / "Instances" / "PTN2"
        / "Ptn-7824-b20.cnf").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Smoke test
    # Run single file test slurm
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_configured_solver.main([str(example_test_file_path),
                                    "--settings-file", str(settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run set test slurm
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_configured_solver.main([example_test_set_path.name,
                                    "--settings-file", str(settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run single file test local
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_configured_solver.main([str(example_test_file_path),
                                    "--run-on", "local"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run test set local
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_configured_solver.main([example_test_set_path.name,
                                    "--run-on", "local"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
