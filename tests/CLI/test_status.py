"""Test for the Sparkle CLI status entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import status


@pytest.mark.integration
def test_status_command(tmp_path: Path,
                        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test status command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        status.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
