"""Test functionalities related to the about commmand."""
from unittest import TestCase
from sparkle import about


class TestAbout(TestCase):
    def test_about_str_type(self):
        """Tests about_str() returns the correct type."""
        # Simple test, mostly for example purpose
        self.assertIsInstance(about.about_str, str)
