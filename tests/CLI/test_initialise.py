"""Test the initiliase CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import initialise


@pytest.mark.integration
def test_initialise_command(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # Call the command
        initialise.main([])
        # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # TODO: Check with/without specific error messages
