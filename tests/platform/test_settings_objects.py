"""Test class for the Settings class."""
from pathlib import Path
import argparse

from sparkle.platform.settings_objects import Settings, Option


def test_option() -> None:
    """Test the Option (NamedTuple) class."""
    option_a = Option("a", "sec1", int, 1, ("c", "d"))
    _option_a = Option("a", "sec1", int, 1, ("c", "d"))
    # Basic property tests
    assert option_a == _option_a
    assert option_a == "a"
    option_b = Option("b", "sec2", int, 2, ("f", "g"))
    assert option_a != option_b
    # Test fetching from list
    assert "a" in [option_a, option_b]
    # Test getting index
    assert [option_a, option_b].index("a") == 0
    assert [option_b, option_a, _option_a].index("a") == 1
    # Test with arparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(*option_a.args, **option_a.kwargs)
    assert len(parser._actions) == 1
    assert parser._actions[0].dest == option_a.name
    assert parser._actions[0].type == option_a.type


def test_read_from_file() -> None:
    """Test reading settings from file."""
    settings = Settings()
    default_settings = Path("sparkle/Components/settings_settings.ini")
    settings.read_settings_ini(default_settings)
    # TODO: Check properties
    pass


def test_read_with_cli_args() -> None:
    """Test reading settings with CLI args."""
    pass


def test_write_to_file() -> None:
    """Test writing settings to file."""
    pass
