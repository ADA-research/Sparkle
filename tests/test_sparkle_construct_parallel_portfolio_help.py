from unittest import TestCase
import subprocess
from pathlib import Path

from Commands.sparkle_help.sparkle_construct_parallel_portfolio_help import construct_sparkle_parallel_portfolio
#TODO gives error, because it cannot import

class Test(TestCase):

    def setUp(self):
        subprocess.run('./Commands/initialise.py > /dev/null', shell=True)
        # Add solvers

    def tearDown(self):
        subprocess.run('./Commands/initialise.py > /dev/null', shell=True)

    def test_add_solvers_to_portfolio(self):
        path = Path("temporary/")
        success = construct_sparkle_parallel_portfolio(path, ["solver", "algorithm", "function"])
        self.assertTrue(success)
    def test_construct_sparkle_parallel_portfolio(self):
        self.fail()
    def test_overwrite_existing_parallel_portfolio(self):
        self.fail()