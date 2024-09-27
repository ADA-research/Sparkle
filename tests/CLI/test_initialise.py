"""Test the initiliase CLI entry point."""
import pytest
from pathlib import Path
import subprocess


@pytest.mark.integration
def test_initialise_command(tmp_path: Path) -> None:
    """Test initialise command."""
    # Smoke test
    call = subprocess.run(["sparkle", "initialise"],
                          cwd=tmp_path)
    assert call.returncode == 0

    # TODO: Check with/without specific error messages
