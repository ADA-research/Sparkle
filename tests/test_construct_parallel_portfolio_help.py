"""Test the sparkle_construct_parallel_portfolio_help module."""

from __future__ import annotations
from unittest import TestCase
import subprocess
from pathlib import Path
import shutil

from CLI.support import construct_parallel_portfolio_help as scpph


class Test(TestCase):
    """Test each function in the module."""

    def setUp(self: TestCase) -> None:
        """Set up for each test case."""
        subprocess.run("./CLI/initialise.py > /dev/null", shell=True)  # noqa

    def tearDown(self: TestCase) -> None:
        """Tear down for each test case."""
        subprocess.run("./CLI/initialise.py > /dev/null", shell=True)  # noqa

    def test_add_solvers_to_portfolio(self: TestCase) -> None:
        """Test whether solvers are added to a parallel portfolio correctly."""
        # TODO: Implement test
        pass

    def test_construct_sparkle_parallel_portfolio(self: TestCase) -> None:
        """Test parallel portfolios are constructed correctly."""
        # TODO: Implement test
        pass

    def test_overwrite_existing_parallel_portfolio(self: TestCase) -> None:
        """Test parallel portfolios are constructed correctly when one already exists."""
        path = Path("tests/temporary/")
        success = scpph.construct_sparkle_parallel_portfolio(
            path, True, ["solver", "algorithm", "function"])
        self.assertTrue(success)
        shutil.rmtree(path)
