"""Test files for Extractor class."""

from __future__ import annotations
from pathlib import Path
import pytest
from sparkle.selector import Extractor
from unittest.mock import patch


test_dir_2024 = Path("Examples/Resources/Extractors/SAT-features-competition2024/")
test_dir_2012 = Path(
    "Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite"
)

extractor_2012 = Extractor(directory=test_dir_2012)
extractor_2024 = Extractor(directory=test_dir_2024)


@pytest.mark.parametrize(
    "extractor, test_dir",
    [(extractor_2012, test_dir_2012), (extractor_2024, test_dir_2024)],
)
def test_extractor_constructor(extractor: Extractor, test_dir: Path) -> None:
    """Test for constructor."""
    assert extractor.directory == test_dir
    assert extractor.name == test_dir.name
    assert extractor.runsolver_exec == test_dir / "runsolver"
    assert extractor._features is None
    assert extractor._feature_groups is None
    assert extractor._groupwise_computation is None


@pytest.mark.parametrize("extractor", [extractor_2012, extractor_2024])
def test_features(extractor: Extractor) -> None:
    """Test for property features."""
    assert extractor._features is None

    first_call_features = extractor.features

    assert isinstance(first_call_features, list), "Expected features to be a list."

    assert extractor._features == first_call_features, (
        "Internal _features attribute should match the accessed value."
    )

    assert len(first_call_features) > 0, (
        "Feature list should not be empty for a valid extractor."
    )

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

    with patch("subprocess.run") as mock_subprocess_run:
        second_call_features = extractor.features

        assert first_call_features == second_call_features, (
            "Features property should cache the result and return consistent values."
        )

        (
            mock_subprocess_run.assert_not_called(),
            (
                "subprocess.run should not be called again as the result should "
                "be cached after the first access."
            ),
        )


@pytest.mark.parametrize("extractor", [extractor_2012, extractor_2024])
def test_feature_groups(extractor: Extractor) -> None:
    """Test for property feature_groups."""
    assert extractor._feature_groups is None

    feature_groups = extractor.feature_groups

    assert extractor._feature_groups == feature_groups, (
        "Internal _feature_groups attribute should match the accessed value."
    )

    assert isinstance(feature_groups, list), "Expected feature_groups to be a list."

    assert len(feature_groups) == len(set(feature_groups)), (
        f"Expected unique elements in feature_groups, "
        f"but got duplicates: {feature_groups}"
    )

    for group in feature_groups:
        assert isinstance(group, str), (
            f"Each feature group should be of type str, "
            f"but got {type(group).__name__}: {group}"
        )


def test_empty_feature_groups() -> None:
    """Test for feature_groups when groups are missing."""
    extractor = Extractor(directory=test_dir_2012)

    mock_features = "[(None, 'feature1'), (None, 'feature2'), (None, 'feature3')]"
    expected_groups = [None]

    with patch("subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.return_value.stdout = mock_features.encode()
        mock_subprocess_run.return_value.returncode = 0

        feature_groups = extractor.feature_groups

        assert isinstance(feature_groups, list), (
            f"Expected a list, got: {type(feature_groups)}"
        )

        assert feature_groups == expected_groups, (
            f"Expected groups: {expected_groups}, instead got : {feature_groups}"
        )


@pytest.mark.parametrize("extractor", [extractor_2012, extractor_2024])
def test_output_dimension(extractor: Extractor) -> None:
    """Test for property output_dimension."""
    output_dim = extractor.output_dimension

    features = extractor.features

    assert output_dim == len(features), (
        f"Expected dimension: {len(features)}, but got: {output_dim}"
    )


@pytest.mark.parametrize(
    "extractor, value", [(extractor_2012, False), (extractor_2024, True)]
)
def test_groupwise_computation(extractor: Extractor, value: bool) -> None:
    """Test for property groupwise_computation."""
    assert extractor._groupwise_computation is None

    fc_groupwise_computation = extractor.groupwise_computation

    assert isinstance(fc_groupwise_computation, bool), (
        f"Groupwise computation should be bool, but got: {type(fc_groupwise_computation)}"
    )

    assert fc_groupwise_computation == value, (
        f"Expected : {value}, but got: {fc_groupwise_computation}"
    )

    assert fc_groupwise_computation == extractor._groupwise_computation, (
        "Internal _groupwise_computation attributeshould match the accessed value."
    )

    with patch("subprocess.run") as mock_subprocess_run:
        sc_groupwise_computation = extractor.groupwise_computation

        assert sc_groupwise_computation == fc_groupwise_computation, (
            "groupwise_computation property should cache the result and "
            "return consistent values."
        )

        (
            mock_subprocess_run.assert_not_called(),
            (
                "subprocess.run should not be called again as the result should "
                "be cached after the first access."
            ),
        )


def test_build_cmd() -> None:
    """Test for method build_cmd."""
    # TODO: Write test
    pass


def test_run() -> None:
    """Test for method run."""
    # TODO: Write test
    pass


def test_output_regex() -> None:
    """Test for the regex matching the log output."""
    example = b"128.48/126.01\t[('base', 'n_vars_original', '238290.000000000'), ('base', 'n_clauses_original', '936006.000000000'), ('base', 'n_vars', '152765.000000000'), ('base', 'n_clauses', '490809.000000000'), ('base', 'reduced_vars', '0.559846824'), ('base', 'reduced_clauses', '0.907067719'), ('base', 'pre_featuretime', '7.420000000'), ('base', 'vars_clauses_ratio', '0.311251424'), ('base', 'Postive-Negative-Literals_clause_ratio_mean', '0.264139411'), ('base', 'Postive-Negative-Literals_clause_coefficient_of_variation', '1.055339007'), ('base', 'Postive-Negative-Literals_clause_ratio_minimum', '0.000000000'), ('base', 'Postive-Negative-Literals_clause_ratio_maximum', '1.000000000'), ('base', 'Postive-Negative-Literals_clause_ratio_entropy', '0.921241405'), ('base', 'Variable-Clause-Graph_clause_mean', '0.000016969'), ('base', 'Variable-Clause-Graph_clause_coefficient_of_variation', '0.189575956'), ('base', 'Variable-Clause-Graph_clause_min', '0.000013092'), ('base', 'Variable-Clause-Graph_clause_max', '0.000019638'), ('base', 'Variable-Clause-Graph_clause_entropy', '0.676041040'), ('base', 'unary', '0.000000000'), ('base', 'binary', '0.407781846'), ('base', 'trinary', '1.000000000'), ('base', 'feature_time', '0.030000000'), ('base', 'Variable-Clause-Graph_variable_mean', '0.000016989'), ('base', 'Variable-Clause-Graph_variable_coefficient_of_variation', '2.060640058'), ('base', 'Variable-Clause-Graph_variable_min', '0.000004075'), ('base', 'Variable-Clause-Graph_variable_max', '0.001558651'), ('base', 'Variable-Clause-Graph_variable_entropy', '2.045314316'), ('base', 'Postive-Negative-Literals_variable_mean', '0.058496362'), ('base', 'Postive-Negative-Literals_variable_standard_deviation', '0.090059060'), ('base', 'Postive-Negative-Literals_variable_min', '0.000000000'), ('base', 'Postive-Negative-Literals_variable_max', '0.866666667'), ('base', 'Postive-Negative-Literals_variable_entropy', '1.062020368'), ('base', 'Horn-Formula_variable_mean', '0.000010448'), ('base', 'Horn-Formula_variable_coefficient_of_variation', '2.251917377'), ('base', 'Horn-Formula_variable_min', '0.000002037'), ('base', 'Horn-Formula_variable_max', '0.000817018'), ('base', 'Horn-Formula_variable_entropy', '1.709661624'), ('base', 'Horn-Formula_clauses_fraction', '0.665303611'), ('base', 'Variable-Graph_variable_mean', '0.000010813'), ('base', 'Variable-Graph_variable_coefficient_of_variation', '2.579094033'), ('base', 'Variable-Graph_variable_min', '0.000002037'), ('base', 'Variable-Graph_variable_max', '0.001175610'), ('base', 'Kevin-Leyton-Brown_feature_time', '21.040000000'), ('base', 'Clause-Graph_clause_mean', '0.000115884'), ('base', 'Clause-Graph_clause_coefficient_of_variation', '1.703620171'), ('base', 'Clause-Graph_clause_min', '0.000002037'), ('base', 'Clause-Graph_clause_max', '0.000882217'), ('base', 'Clause-Graph_clause_entropy', '3.687603682'), ('base', 'Clause-Graph_cluster_coefficient_mean', '0.255763369'), ('base', 'Clause-Graph_cluster_coefficient_of_variation', '0.699031298'), ('base', 'Clause-Graph_cluster_coefficient_min', '0.006896478'), ('base', 'Clause-Graph_cluster_coefficient_max', '1.000000000'), ('base', 'Clause-Graph_cluster_coefficient_entropy', '3.324503014'), ('base', 'Clause-Graph_feature_time', '90.520000000')]\r\n".decode()
    assert Extractor.output_pattern.match(example) is not None


def test_get_feature_vector() -> None:
    """Test for method get_feature_vector."""
    # TODO: Write test
    pass
