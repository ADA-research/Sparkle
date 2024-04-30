"""Test functionalities related to the about command."""

from __future__ import annotations
from unittest import TestCase
from sparkle import about


class TestAbout(TestCase):
    """Tests function of sparkle.about."""
    def test_about_str_type(self: TestCase) -> None:
        """Tests about_str() returns the correct type."""
        # Simple test, mostly for example purpose
        self.assertIsInstance(about.about_str, str)
        self.assertIsInstance(about.name, str)
        self.assertIsInstance(about.version, str)
