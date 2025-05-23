"""Test files for Selector class."""
import pytest
from unittest.mock import patch, Mock

from pathlib import Path
from sparkle.solver import Selector
from sparkle.types.objective import PAR
from runrunner.base import Runner
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from asf.selectors import PairwiseClassifier, MultiClassClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from asf.selectors.abstract_model_based_selector import AbstractModelBasedSelector
from asf.predictors import AbstractPredictor
from sklearn.base import ClassifierMixin, RegressorMixin
import pandas as pd


@pytest.mark.parametrize(
    "selector_class, model_class", [
        (MultiClassClassifier, RandomForestClassifier),
        (PairwiseClassifier, GradientBoostingClassifier),
    ]
)
def test_selector_constructor(
        selector_class: AbstractModelBasedSelector,
        model_class: AbstractPredictor | ClassifierMixin | RegressorMixin) -> None:
    """Test for method constructor."""
    selector = Selector(selector_class, model_class)
    assert selector.selector_class == selector_class
    assert selector.model_class == model_class


@patch("runrunner.add_to_queue")
def test_construct(mock_add_to_queue: Mock) -> None:
    """Test for method construct."""
    selector = Selector(MultiClassClassifier, RandomForestClassifier)

    # Construct Parameters
    target_file = Path("tests/test_files/Output/Portfolio_Selector/portfolio_selector")
    performance_data_path = Path(
        "tests/test_files/Output/Performance_Data/performance_data.csv")
    performance_data = PerformanceDataFrame(performance_data_path)
    feature_data_path = Path("tests/test_files/Output/Feature_Data/feature_data.csv")
    feature_data = FeatureDataFrame(feature_data_path)
    objective = PAR()
    solver_cutoff = 60
    run_on = Runner.SLURM
    sbatch_options = ["--mem-per-cpu=3000", "--qos=short", "--time=30:00"]
    base_dir = Path(".")

    selector.construct(target_file,
                       performance_data,
                       feature_data,
                       objective,
                       solver_cutoff,
                       run_on,
                       "test_job",
                       sbatch_options,
                       base_dir)

    selector_performance_path = target_file.parent / performance_data.csv_filepath.name
    assert selector_performance_path.is_file()
    selector_performance = pd.read_csv(selector_performance_path)
    selector_performance.shape[0] == performance_data.num_instances
    selector_performance.shape[1] == performance_data.num_solvers + 1  # +1 instance col

    selector_feature_path = target_file.parent / feature_data.csv_filepath.name
    assert selector_feature_path.is_file()
    selector_feature_data = pd.read_csv(selector_feature_path, index_col=0)
    # Feature data got transposed
    assert selector_feature_data.shape[0] == feature_data.dataframe.shape[1]
    assert selector_feature_data.shape[1] == feature_data.dataframe.shape[0]

    _, kwargs = mock_add_to_queue.call_args
    assert kwargs["runner"] == run_on
    assert kwargs["base_dir"] == base_dir
    assert kwargs["sbatch_options"] == sbatch_options
    cmd_str = kwargs["cmd"][0]
    assert f"--selector {selector.selector_class.__name__}" in cmd_str
    assert f"--model {selector.model_class.__name__}" in cmd_str
    assert f"--budget {solver_cutoff}" in cmd_str
    assert f"--performance-metric {objective.name}" in cmd_str
    assert f"--feature-data {selector_feature_path}" in cmd_str
    assert f"--performance-data {selector_performance_path}" in cmd_str
    assert f"--model-path {target_file}" in cmd_str


@patch("runrunner.add_to_queue")
def test_construct_all_configurations(mock_add_queue: Mock,
                                      tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with configuration selection."""
    selector = Selector(MultiClassClassifier, RandomForestClassifier)

    # Construct Parameters
    performance_data_path =\
        Path("tests/test_files/performance/actual-data.csv").absolute()
    performance_data =\
        PerformanceDataFrame(performance_data_path)
    feature_data_path =\
        Path("tests/test_files/Output/Feature_Data/feature_data.csv").absolute()
    feature_data = FeatureDataFrame(feature_data_path)
    objective = PAR()
    solver_cutoff = 60
    run_on = Runner.SLURM
    sbatch_options = ["--mem-per-cpu=3000", "--qos=short", "--time=30:00"]
    base_dir = Path(".")
    configurations = performance_data.get_configurations("Solvers/PbO-CCSAT-Generic")

    monkeypatch.chdir(tmp_path)
    target_file = Path("portfolio_selector")

    selector.construct(target_file,
                       performance_data,
                       feature_data,
                       objective,
                       configurations,
                       solver_cutoff,
                       run_on,
                       sbatch_options,
                       base_dir)


@pytest.mark.parametrize(
    "instance",
    ["Instances/PTN/Ptn-7824-b03.cnf",
     "Instances/PTN/Ptn-7824-b15.cnf",
     "Instances/PTN/Ptn-7824-b21.cnf"]
)
def test_run(instance: str) -> None:
    """Test for method run."""
    selector = Selector(MultiClassClassifier, RandomForestClassifier)
    selector_path = Path("tests/test_files/Selector/portfolio_selector_test")
    feature_data_path = Path("tests/test_files/Output/Feature_Data/feature_data.csv")
    feature_data = FeatureDataFrame(feature_data_path)

    solvers = ["Solvers/CSCCSat", "Solvers/PbO-CCSAT-Generic", "Solvers/MiniSAT"]
    schedule = selector.run(selector_path, instance, feature_data)
    print(schedule)
    assert schedule[0][0] in solvers  # Schedule has shape [(solver, config, budget)]
