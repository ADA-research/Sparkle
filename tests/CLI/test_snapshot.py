"""Test the snapshot CLI entry points."""
import pytest
from pathlib import Path
import subprocess


@pytest.mark.integration
def test_load_command(tmp_path: Path) -> None:
    """Test load command."""
    # Smoke test
    test_snapshot_file = Path("tests/CLI/test_files/test_snapshot.zip")
    load = subprocess.run(["sparkle", "load", "snapshot", test_snapshot_file.absolute()],
                          cwd=tmp_path)
    assert load.returncode == 0


@pytest.mark.integration
def test_save_command(tmp_path: Path) -> None:
    """Test load command."""
    init = subprocess.run(["sparkle", "initialise"],
                          cwd=tmp_path)
    assert init.returncode == 0
    # Smoke test
    save = subprocess.run(["sparkle", "save", "snapshot"],
                          cwd=tmp_path)
    assert save.returncode == 0
