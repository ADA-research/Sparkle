"""Test the initiliase CLI entry point."""
import pytest
from pathlib import Path
import os

from sparkle.CLI import initialise


@pytest.mark.integration
def test_initialise_command(tmp_path: Path) -> None:
    """Test initialise command."""
    # Smoke test
    cwd = Path.cwd()
    os.chdir(tmp_path)  # Execute the command in the PyTest tmp directory
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # Call the command
        initialise.main([])
        # Check the exit status
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
    os.chdir(cwd)
    # TODO: Check with/without specific error messages
