"""Tests for feature dataframe class."""

import math
import pandas as pd
import pytest
from pathlib import Path

from sparkle.structures import FeatureDataFrame

SAMPLE_EXTRACTOR_DATA = {
    "ExtractorA": [("Group1", "Feature1"), ("Group1", "Feature2")],
    "ExtractorB": [("Group2", "Feature3")],
}
SAMPLE_INSTANCES = ["Instance_X", "Instance_Y"]


@pytest.fixture
def feature_df(tmp_path: Path) -> FeatureDataFrame:
    """Pytest fixture to provide an initialized FeatureDataFrame."""
    csv_path = tmp_path / "test.csv"
    feature_df = FeatureDataFrame(
        csv_filepath=csv_path,
        instances=SAMPLE_INSTANCES,
        extractor_data=SAMPLE_EXTRACTOR_DATA,
    )
    return feature_df


def test_feature_dataframe_constructor(tmp_path: Path) -> None:
    """Test feature dataframe constructor for new creation and loading."""
    # Scenario 1: Create a new DataFrame
    csv_path = tmp_path / "new_features.csv"
    feature_df_new = FeatureDataFrame(
        csv_filepath=csv_path,
        instances=SAMPLE_INSTANCES,
        extractor_data=SAMPLE_EXTRACTOR_DATA,
    )
    assert feature_df_new.csv_filepath == csv_path
    assert feature_df_new.columns.names == FeatureDataFrame.multi_dim_column_names
    assert csv_path.exists()
    assert feature_df_new.num_features == 3
    assert sorted(feature_df_new.instances) == sorted(SAMPLE_INSTANCES)
    # Check if every cell of the dataframe is nan
    assert feature_df_new.isnull().all().all()

    # Scenario 2: Load a DataFrame from an existing file
    feature_df_new.set_value("Instance_X", "ExtractorA", "Group1", "Feature1", 123.45)
    feature_df_new.save_csv()

    feature_df_loaded = FeatureDataFrame(csv_filepath=csv_path)
    assert (
        feature_df_loaded.get_value("Instance_X", "ExtractorA", "Group1", "Feature1")
        == 123.45
    )


def test_add_extractor(feature_df: FeatureDataFrame) -> None:
    """Test for method add_extractor."""
    assert "ExtractorC" not in feature_df.extractors
    initial_feature_count = feature_df.num_features

    feature_df.add_extractor("ExtractorC", [("Group3", "Feature4")])

    assert "ExtractorC" in feature_df.extractors
    assert feature_df.num_features == initial_feature_count + 1
    # Verify that the new row is filled with NaNs
    value = feature_df.get_value("Instance_X", "ExtractorC", "Group3", "Feature4")
    assert math.isnan(value)


def test_add_instances(feature_df: FeatureDataFrame) -> None:
    """Test for method add_instances."""
    assert "Instance_Z" not in feature_df.instances

    feature_df.add_instances("Instance_Z")
    assert "Instance_Z" in feature_df.instances
    assert feature_df.loc["Instance_Z"].isnull().all()

    feature_df.add_instances("Instance_W", values=[1.0] * feature_df.num_features)
    assert "Instance_W" in feature_df.instances
    assert (feature_df.loc["Instance_W"] == 1.0).all()


def test_remove_extractor(feature_df: FeatureDataFrame) -> None:
    """Test for method remove_extractor."""
    assert "ExtractorA" in feature_df.extractors
    initial_feature_count = feature_df.num_features

    feature_df.remove_extractor("ExtractorA")

    assert "ExtractorA" not in feature_df.extractors
    # ExtractorA had 2 features
    assert feature_df.num_features == initial_feature_count - 2


def test_remove_instances(feature_df: FeatureDataFrame) -> None:
    """Test for method remove_instances."""
    assert "Instance_X" in feature_df.instances

    feature_df.remove_instances("Instance_X")
    assert "Instance_X" not in feature_df.instances

    feature_df.remove_instances(["Instance_Y"])
    assert "Instance_Y" not in feature_df.instances
    assert len(feature_df.instances) == 0


def test_get_feature_groups(feature_df: FeatureDataFrame) -> None:
    """Test for method get_feature_groups."""
    all_groups = feature_df.get_feature_groups()
    assert sorted(all_groups) == ["Group1", "Group2"]

    groups_a = feature_df.get_feature_groups(extractor="ExtractorA")
    assert groups_a == ["Group1"]

    groups_b = feature_df.get_feature_groups(extractor="ExtractorB")
    assert sorted(groups_b) == ["Group2"]


def test_get_value(feature_df: FeatureDataFrame) -> None:
    """Test for method get_value."""
    # Set a known value to test retrieval
    feature_df.loc["Instance_X", ("ExtractorA", "Group1", "Feature1")] = 42.0
    value = feature_df.get_value("Instance_X", "ExtractorA", "Group1", "Feature1")
    assert value == 42.0


def test_set_value(feature_df: FeatureDataFrame) -> None:
    """Test for method set_value."""
    initial_value = feature_df.get_value(
        "Instance_Y", "ExtractorB", "Group2", "Feature3"
    )
    assert math.isnan(initial_value)

    feature_df.set_value("Instance_Y", "ExtractorB", "Group2", "Feature3", -1.5)

    new_value = feature_df.get_value("Instance_Y", "ExtractorB", "Group2", "Feature3")
    assert new_value == -1.5


def test_has_missing_vectors(feature_df: FeatureDataFrame) -> None:
    """Test for method has_missing_vectors in specific scenarios."""
    # Initially, all vectors are missing
    assert feature_df.has_missing_vectors()

    # SCENARIO 1: Atleast one missing value per instance for all extractors
    feature_df.loc[:, :] = 1.0
    feature_df.set_value(
        "Instance_X", "ExtractorA", "Group1", "Feature1", FeatureDataFrame.missing_value
    )
    feature_df.set_value(
        "Instance_X", "ExtractorB", "Group2", "Feature3", FeatureDataFrame.missing_value
    )
    feature_df.set_value(
        "Instance_Y", "ExtractorA", "Group1", "Feature1", FeatureDataFrame.missing_value
    )
    feature_df.set_value(
        "Instance_Y", "ExtractorB", "Group2", "Feature3", FeatureDataFrame.missing_value
    )
    assert feature_df.has_missing_vectors()

    # SCENARIO 2: One feature group is completely missing
    feature_df.loc[:, :] = 1.0
    group1_mask = (
        feature_df.columns.get_level_values(FeatureDataFrame.feature_group_dim)
        == "Group1"
    )
    feature_df.loc[:, group1_mask] = FeatureDataFrame.missing_value
    assert feature_df.has_missing_vectors()

    # SCENARIO 3: One instance is completely missing
    feature_df.loc[:, :] = 1.0
    feature_df["Instance_Y"] = FeatureDataFrame.missing_value
    assert feature_df.has_missing_vectors()

    # SCENARIO 4: Completly filled feature dataframe
    feature_df.loc[:, :] = 1.0
    assert not feature_df.has_missing_vectors()


def test_get_remaining_jobs(feature_df: FeatureDataFrame) -> None:
    """Test for method get_remaining_jobs."""
    jobs = feature_df.remaining_jobs()
    expected_jobs = {
        ("Instance_X", "ExtractorA", "Group1"),
        ("Instance_Y", "ExtractorA", "Group1"),
        ("Instance_X", "ExtractorB", "Group2"),
        ("Instance_Y", "ExtractorB", "Group2"),
    }
    assert set(jobs) == expected_jobs

    # Complete one job by filling its value
    feature_df.set_value("Instance_X", "ExtractorB", "Group2", "Feature3", 1.0)

    remaining_jobs = feature_df.remaining_jobs()
    assert ("Instance_X", "ExtractorB", "Group2") not in remaining_jobs
    assert len(remaining_jobs) == 3


def test_get_instance(feature_df: FeatureDataFrame) -> None:
    """Test for method get_instance."""
    features = [10.0, 20.0, 30.0]
    feature_df.loc["Instance_Y"] = features

    retrieved_features = feature_df.get_instance("Instance_Y")
    assert retrieved_features == features


def test_impute_missing_values(feature_df: FeatureDataFrame) -> None:
    """Test for method impute_missing_values."""
    # Test with one missing value in a row
    feature_df.set_value("Instance_X", "ExtractorA", "Group1", "Feature1", 10.0)
    # The value for Instance_Y in the same row is NaN and the row mean is 10.0.
    feature_df.impute_missing_values()
    assert feature_df.get_value("Instance_Y", "ExtractorA", "Group1", "Feature1") == 10.0

    # Test for a feature (row) missing in every instance
    feature_df.reset_dataframe()
    feature_df[("ExtractorA", "Group1", "Feature1")] = [2.0, 4.0]
    # Row ("Group1", "Feature2", "ExtractorA") is all NaN.
    feature_df.impute_missing_values()
    # Imputing a row of all NaNs should result in NaNs
    value = feature_df.get_value("Instance_X", "ExtractorA", "Group1", "Feature2")
    assert math.isnan(value)


def test_has_missing_values(feature_df: FeatureDataFrame) -> None:
    """Test for method has_missing_values."""
    assert feature_df.has_missing_value()

    feature_df.loc[:, :] = 1.0
    assert not feature_df.has_missing_value()


def test_reset_dataframe(feature_df: FeatureDataFrame) -> None:
    """Test for method reset_dataframe."""
    feature_df.loc[:, :] = 99.0
    assert not feature_df.has_missing_value()

    feature_df.reset_dataframe()
    assert feature_df.has_missing_value()
    assert feature_df.isnull().all().all()


def test_sort(feature_df: FeatureDataFrame) -> None:
    """Test for method sort."""
    feature_df.add_instances("AAA_INSTANCE_NUMERO1")
    assert not feature_df.index.is_monotonic_increasing

    feature_df.sort()
    assert feature_df.index.is_monotonic_increasing


def test_instances(feature_df: FeatureDataFrame) -> None:
    """Test instances property."""
    assert sorted(feature_df.instances) == sorted(SAMPLE_INSTANCES)
    feature_df.add_instances("New_Instance")
    assert sorted(feature_df.instances) == sorted(SAMPLE_INSTANCES + ["New_Instance"])


def test_extractors(feature_df: FeatureDataFrame) -> None:
    """Test for property extractors."""
    assert sorted(feature_df.extractors) == sorted(["ExtractorA", "ExtractorB"])
    feature_df.add_extractor("New_Extractor", [("Group_New", "Feature_New")])
    assert sorted(feature_df.extractors) == sorted(
        ["ExtractorA", "ExtractorB", "New_Extractor"]
    )


def test_num_features(feature_df: FeatureDataFrame) -> None:
    """Test for property num_features."""
    assert feature_df.num_features == 3
    # Add an extractor with 3 new features
    feature_df.add_extractor(
        "ExtractorC",
        [("Group3", "Feature4"), ("Group3", "Feature5"), ("Group3", "Feature6")],
    )
    assert feature_df.num_features == 6
    # Remove an extractor that has 2 features ("ExtractorA")
    feature_df.remove_extractor("ExtractorA")
    assert feature_df.num_features == 4


def features(feature_df: FeatureDataFrame) -> None:
    """Test for property features."""
    initial_features = ["Feature1", "Feature2", "Feature3"]
    assert sorted(feature_df.features) == sorted(initial_features)
    # Add a new extractor with one new feature and one duplicate feature
    feature_df.add_extractor(
        "ExtractorC", [("Group3", "Feature4"), ("Group1", "Feature1")]
    )
    expected_features = ["Feature1", "Feature2", "Feature3", "Feature4"]
    assert sorted(feature_df.features) == sorted(expected_features)


def test_save_csv(feature_df: FeatureDataFrame, tmp_path: Path) -> None:
    """Test for method save_csv."""
    # Test saving to the default path
    feature_df.set_value("Instance_X", "ExtractorA", "Group1", "Feature1", 1.0)
    feature_df.save_csv()
    fdf_reloaded = FeatureDataFrame(feature_df.csv_filepath)
    pd.testing.assert_frame_equal(feature_df, fdf_reloaded)

    # Test saving to a specified path
    new_csv_path = tmp_path / "new_save_path.csv"
    feature_df.save_csv(new_csv_path)
    assert new_csv_path.exists()
    fdf_new_reloaded = FeatureDataFrame(new_csv_path)
    pd.testing.assert_frame_equal(feature_df, fdf_new_reloaded)
