"""Test files for Extractor class."""
from __future__ import annotations
from pathlib import Path
import pytest
from sparkle.solver import Extractor
from unittest.mock import patch


# Define test directories for 2024 and 2012 versions of the extractor
test_dir_2024 = Path(
    "Examples/Resources/Extractors/SAT-features-competition2024/"
)
test_dir_2012 = Path(
    "Examples/Resources/Extractors/"
    "SAT-features-competition2012_revised_without_SatELite_sparkle"
)

# Instantiate Extractor objects for each directory
extractor_2012 = Extractor(directory=test_dir_2012)
extractor_2024 = Extractor(directory=test_dir_2024)


@pytest.mark.parametrize(
    "extractor, test_dir", [
        (extractor_2012, test_dir_2012),
        (extractor_2024, test_dir_2024)
    ]
)
def test_extractor_constructor(extractor: Extractor, test_dir: Path) -> None:
    """Test for constructor."""
    assert extractor.directory == test_dir
    assert extractor.name == test_dir.name
    assert extractor.raw_output_directory == test_dir / "tmp"
    assert extractor.runsolver_exec == test_dir / "runsolver"
    assert extractor._features is None
    assert extractor._feature_groups is None
    assert extractor._groupwise_computation is None


@pytest.mark.parametrize(
    "extractor",
    [extractor_2012, extractor_2024]
)
def test_features(extractor: Extractor) -> None:
    """Test for property features."""
    # Check if features are none before accessing
    assert extractor._features is None

    # Access the features for the first time
    first_call_features = extractor.features

    # Validate that features are returned as a list
    assert isinstance(first_call_features, list), (
        "Expected features to be a list."
    )

    # Validate internal storage consistency
    assert extractor._features == first_call_features, (
        "Internal _features attribute should match the accessed value."
    )

    # Check that the list is not empty
    assert len(first_call_features) > 0, (
        "Feature list should not be empty for a valid extractor."
    )

    # Ensure each feature is a tuple of two strings
    for pair in first_call_features:
        assert isinstance(pair, tuple), (
            f"Expected a tuple, but got {type(pair).__name__}: {pair}"
        )
        assert len(pair) == 2, (
            f"Expected a tuple of length 2, but got {len(pair)}: {pair}"
        )
        for element in pair:
            assert isinstance(element, str), (
                f"Expected all elements to be strings, but got "
                f"{type(element).__name__}: {element}"
            )

    # Patch subprocess.run after the first call to ensure caching is used
    with patch("subprocess.run") as mock_subprocess_run:
        # Access the property again to verify caching
        second_call_features = extractor.features

        # Validate that caching works (both calls should return the same value)
        assert first_call_features == second_call_features, (
            "Features property should cache the result and "
            "return consistent values."
        )

        # Ensure subprocess.run was not called during the second access
        mock_subprocess_run.assert_not_called(), (
            "subprocess.run should not be called again as the result should "
            "be cached after the first access."
        )


@pytest.mark.parametrize(
    "extractor",
    [extractor_2012, extractor_2024]
)
def test_feature_groups(extractor: Extractor) -> None:
    """Test for property feature_groups."""
    # Check if feature groups is none before accessing
    assert extractor._feature_groups is None

    # Access the feature_groups property for the first time
    feature_groups = extractor.feature_groups

    # Validate internal storage consistency
    assert extractor._feature_groups == feature_groups, (
        "Internal _feature_groups attribute should match the accessed value."
    )

    # Validate the type of the returned feature_groups
    assert isinstance(feature_groups, list), (
        "Expected feature_groups to be a list."
    )

    # Check for uniqueness of feature group names
    assert len(feature_groups) == len(set(feature_groups)), (
        f"Expected unique elements in feature_groups, "
        f"but got duplicates: {feature_groups}"
    )

    # Ensure all feature group names are strings
    for group in feature_groups:
        assert isinstance(group, str), (
            f"Each feature group should be of type str, "
            f"but got {type(group).__name__}: {group}"
        )


def test_empty_feature_groups() -> None:
    """Test for feature_groups when groups are missing."""
    extractor = Extractor(directory=test_dir_2012)

    # Prepare a mock output where the group is None
    mock_features = "[(None, 'feature1'), (None, 'feature2'), (None, 'feature3')]"
    expected_groups = [None]

    # Patch subprocess.run in the correct namespace
    # to control the none group scenario
    with patch("subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.return_value.stdout = mock_features.encode()
        mock_subprocess_run.return_value.returncode = 0

        feature_groups = extractor.feature_groups

        # Validate type and returned groups
        assert isinstance(feature_groups, list), (
            f"Expected a list, got: {type(feature_groups)}"
        )

        assert feature_groups == expected_groups, (
            f"Expected groups: {expected_groups}, "
            f"instead got : {feature_groups}"
        )


@pytest.mark.parametrize(
    "extractor",
    [extractor_2012, extractor_2024]
)
def test_output_dimension(extractor: Extractor) -> None:
    """Test for property output_dimension."""
    # Get dimension of features by function
    output_dim = extractor.output_dimension

    # Get real features to validate the function
    features = extractor.features

    assert output_dim == len(features), (
        f"Expected dimension: {len(features)}, "
        f"but got: {output_dim}"
    )


@pytest.mark.parametrize(
    "extractor, value",
    [
        (extractor_2012, False),
        (extractor_2024, True)
    ]
)
def test_groupwise_computation(extractor: Extractor, value: bool) -> None:
    """Test for property groupwise_computation."""
    # Before init check if the attribute is None
    assert extractor._groupwise_computation is None

    # First call of the property
    fc_groupwise_computation = extractor.groupwise_computation

    # Check the type and caching, compare with the expected value
    assert isinstance(fc_groupwise_computation, bool), (
        f"Groupwise computation should be bool, "
        f"but got: {type(fc_groupwise_computation)}"
    )

    assert fc_groupwise_computation == value, (
        f"Expected : {value}, "
        f"but got: {fc_groupwise_computation}"
    )

    assert fc_groupwise_computation == extractor._groupwise_computation, (
        "Internal _groupwise_computation attribute"
        "should match the accessed value."
    )

    # Patch subprocess.run in the correct namespace
    # after the first call to ensure caching is used
    with patch("subprocess.run") as mock_subprocess_run:
        # Call the property a second time to check behavior
        sc_groupwise_computation = extractor.groupwise_computation

        # Validate that caching works (both calls should return the same value)
        assert sc_groupwise_computation == fc_groupwise_computation, (
            "groupwise_computation property should cache the result and "
            "return consistent values."
        )

        # Ensure subprocess.run was not called during the second access
        mock_subprocess_run.assert_not_called(), (
            "subprocess.run should not be called again as the result should "
            "be cached after the first access."
        )


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
