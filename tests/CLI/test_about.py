"""Test the about CLI entry point."""
import subprocess

def test_about_command() -> None:
    """Test about command."""
    call = subprocess.run(["sparkle", "about"])

    assert call.returncode == 0
    