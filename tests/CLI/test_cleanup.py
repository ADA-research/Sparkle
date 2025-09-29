"""Test the Sparkle CLI cleanup entry point."""

import pytest
from pathlib import Path

from sparkle.CLI import cleanup


@pytest.mark.integration
def test_cleanup_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cleanup command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cleanup.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # TODO: Check if correct files are removed


# TODO: Add more tests for --all option and --remove command
