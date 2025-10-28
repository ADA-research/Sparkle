"""Test the CLI wrap command."""
import sys

from sparkle.CLI.wrap import main


@pytest.mark.integration
def test_main() -> None:
    """Test the main entry point."""
    return