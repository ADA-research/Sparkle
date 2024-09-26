"""Test the about CLI entry point."""
import pytest
import subprocess


@pytest.mark.integration
def test_about_command() -> None:
    """Test about command."""
    # Smoke test
    call = subprocess.run(["sparkle", "about"])
    assert call.returncode == 0
