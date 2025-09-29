"""Test the construct portfolio selector CLI entry point."""

import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, construct_portfolio_selector

from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_construct_portfolio_selector_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test construct portfolio command."""
    snapshot_path = (
        Path("tests")
        / "CLI"
        / "test_files"
        / "snapshot_computed_features_run_solvers_csccsat_minisat_ptn.zip"
    ).absolute()
    test_settings_path = cli_tools.get_settings_path()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        construct_portfolio_selector.main(["--settings-file", str(test_settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
