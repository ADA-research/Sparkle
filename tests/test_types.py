"""Test public methods of sparkle types."""

from __future__ import annotations
import unittest
import itertools

from sparkle.types import resolve_objective
from sparkle.types.objective import SparkleObjective, PAR


class TestResolveObjective(unittest.TestCase):
    """Test resolve_objective function."""

    def setUp(self: TestResolveObjective) -> None:
        """List for good and bad objective names."""
        self.test_names_good = ["quality", "quality10", "f1", "F1", "PAR10special",
                                "very_special-indicator"]
        self.test_names_bad = ["", "10", ".test", ":min", "quality:minimum",
                               "quality:min:max", "_test", "-accuracy"]

    def test_resolving_basic(self: TestResolveObjective) -> None:
        """Test successful strings that should result in a normal SparkleObjective."""
        for name in self.test_names_good:
            objective = resolve_objective(name)
            self.assertIsInstance(objective, SparkleObjective)
            self.assertEqual(objective.name, name)
            self.assertTrue(objective.minimise)

    def test_min_max_suffix(self: TestResolveObjective) -> None:
        """Test the min/max suffix."""
        for name, minimise in itertools.product(self.test_names_good, [True, False]):
            input_name = name
            input_name += ":min" if minimise else ":max"
            objective = resolve_objective(input_name)
            self.assertIsInstance(objective, SparkleObjective)
            self.assertEqual(objective.name, input_name)
            self.assertEqual(objective.minimise, minimise)

    def test_failing_strings(self: TestResolveObjective) -> None:
        """Test object names that should fail and return None."""
        for name in self.test_names_bad:
            self.assertIsNone(resolve_objective(name))

    def test_par(self: TestResolveObjective) -> None:
        """Test PAR objects that should successfully initialize."""
        for name, k, oname in [("PAR", 10, "PAR10"),
                               ("PAR10", 10, "PAR10"),
                               ("PAR2", 2, "PAR2"),
                               ("PAR100", 100, "PAR100"),
                               ("PAR10:max", 10, "PAR10"),
                               ("PAR10:min", 10, "PAR10"), ]:
            objective = resolve_objective(name)
            self.assertIsInstance(objective, SparkleObjective)
            self.assertIsInstance(objective, PAR)
            self.assertEqual(objective.name, oname)
            self.assertEqual(objective.k, k)
            self.assertTrue(objective.minimise)

    def test_failing_par(self: TestResolveObjective) -> None:
        """Test PAR objects names with k<0."""
        for name in ["PAR0", "PAR-1"]:
            print(f"{name=}")
            with self.assertRaises(ValueError):
                resolve_objective(name)
