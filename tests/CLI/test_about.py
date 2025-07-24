"""Test the about CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import about


@pytest.mark.integration
def test_about_command(tmp_path: Path,
                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test about command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        about.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code is None
