"""Test functionalities related to the about commmand"""

from sparkle import about


def test_about_str_type():
    # Simple test, mostly for example purpose
    assert(isinstance(about.about_str, str))
