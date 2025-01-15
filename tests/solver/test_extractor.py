"""Test files for Extractor class."""
from __future__ import annotations
from pathlib import Path
import pytest
from sparkle.solver import Extractor


# Define test directories for 2024 and 2012 versions of the extractor
test_dir_2024 = Path("Examples/Resources/Extractors/"
                     "SAT-features-competition2024/")
test_dir_2012 = Path("Examples/Resources/Extractors/"
                     "SAT-features-competition2012"
                     "_revised_without_SatELite_sparkle")

# Instantiate Extractor objects for each directory
extractor_2012 = Extractor(directory=test_dir_2012)
extractor_2024 = Extractor(directory=test_dir_2024)


@pytest.mark.parametrize(
    "extractor, test_dir", [
        (extractor_2012, test_dir_2012),
        (extractor_2024, test_dir_2024)
    ]
)
def test_extractor_constructor(extractor, test_dir) -> None:
    """Test for constructor."""
    assert extractor.directory == test_dir
    assert extractor.name == test_dir.name
    assert extractor.raw_output_directory == test_dir / "tmp"
    assert extractor.runsolver_exec == test_dir / "runsolver"
    assert extractor._features is None
    assert extractor._feature_groups is None
    assert extractor._output_dimension is None
    assert extractor._groupwise_computation is None


@pytest.mark.parametrize(
    "extractor",
    [extractor_2012, extractor_2024]
)
def test_features(extractor) -> None:
    """Test for property features."""
    first_call = extractor.features

    # Validate the features are returned as a list
    assert isinstance(first_call, list), \
        "Expected features to be a list."

    # Validate internal caching of features
    assert extractor._features == first_call, \
        "Internal _features attribute should match the accessed value."

    # Check that the list is not empty
    assert len(first_call) > 0, \
        "Feature list should not be empty for a valid extractor."

    # Access the property again to verify caching
    second_call = extractor.features
    assert first_call == second_call, \
        "Features property should cache the result."

    # They should be equal after the second call
    assert extractor._features == first_call, \
        "Internal _features attribute should match the accessed value."

    # Check the length again that is not empty
    assert len(first_call) > 0, \
        "Feature list should not be empty for a valid extractor."

    # Ensure each feature is a tuple of two strings
    assert all(
        isinstance(pair, tuple) and len(pair) == 2 and all(
            isinstance(element, str) for element in pair
        ) for pair in first_call
    ), (
        f"Expected each feature to be a tuple of 2 strings, "
        f"but got {first_call}"
    )


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
