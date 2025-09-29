"""Test functionalities related to the about file."""

from __future__ import annotations
from sparkle import about


def test_about_str_type() -> None:
    """Tests about_str() returns the correct type."""
    # Simple test, mostly for example purpose
    assert isinstance(about.about_str, str)
    assert isinstance(about.name, str)
    assert isinstance(about.version, str)
