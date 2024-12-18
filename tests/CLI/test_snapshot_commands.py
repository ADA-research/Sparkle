"""Test the snapshot CLI entry points."""
import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, save_snapshot, initialise


@pytest.mark.integration
def test_load_command(tmp_path: Path,
                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Test load command."""
    test_snapshot_file = Path("tests/CLI/test_files/test_snapshot.zip").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(test_snapshot_file)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # TODO: Check if snapshot is loaded correctly


@pytest.mark.integration
def test_save_command(tmp_path: Path,
                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Test load command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        initialise.main([])  # Initialise the platform
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        save_snapshot.main([])  # Call save command
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # TODO: Check if the saved snapshot exists
    # TODO: Test with name argument
