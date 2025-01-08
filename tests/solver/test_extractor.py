"""Test files for Extractor class."""
from __future__ import annotations
from pathlib import Path

from sparkle.solver import Extractor

test_dir_2024 = Path("Examples/Resources/Extractors/SAT-features-competition2024/")
test_dir_2012 = Path("Examples/Resources/Extractors/"
                     "SAT-features-competition2012_revised_without_SatELite_sparkle")


def test_extractor_constructor() -> None:
    """Test for constructor."""
    # Test with SAT2024 for Extractor
    extractor_2024 = Extractor(directory=test_dir_2024)
    assert extractor_2024.directory == test_dir_2024
    assert extractor_2024.name == test_dir_2024.name
    assert extractor_2024.raw_output_directory == test_dir_2024 / "tmp"
    assert extractor_2024.runsolver_exec == test_dir_2024 / "runsolver"
    assert extractor_2024._features is None
    assert extractor_2024._feature_groups is None
    assert extractor_2024._output_dimension is None
    assert extractor_2024._groupwise_computation is None

    # Test with SAT2012 for Extractor
    extractor_2012 = Extractor(directory=test_dir_2012)
    assert extractor_2012.directory == test_dir_2012
    assert extractor_2012.name == test_dir_2012.name
    assert extractor_2012.raw_output_directory == test_dir_2012 / "tmp"
    assert extractor_2012.runsolver_exec == test_dir_2012 / "runsolver"
    assert extractor_2012._features is None
    assert extractor_2012._feature_groups is None
    assert extractor_2012._output_dimension is None
    assert extractor_2012._groupwise_computation is None


def test_features() -> None:
    """Test for property features."""
    # TODO: Write test
    pass


def test_feature_groups() -> None:
    """Test for property feature_groups."""
    # TODO: Write test
    pass


def test_output_dimension() -> None:
    """Test for property output_dimension."""
    # TODO: Write test
    pass


def test_groupwise_computation() -> None:
    """Test for property groupwise_computation."""
    # TODO: Write test
    pass


def test_build_cmd() -> None:
    """Test for method build_cmd."""
    # TODO: Write test
    pass


def test_run() -> None:
    """Test for method run."""
    # TODO: Write test
    pass


def test_get_feature_vector() -> None:
    """Test for method get_feature_vector."""
    # TODO: Write test
    pass
