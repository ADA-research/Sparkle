"""Test the generate report CLI entry point."""

from pathlib import Path

import pandas as pd
import pytest

from src.sparkle.CLI import generate_report, load_snapshot
from src.sparkle.CLI.generate_report import (
    MAX_COLS_PER_TABLE,
    NUM_KEYS_FDF,
    NUM_KEYS_PDF,
    WIDE_TABLE_THRESHOLD,
)
from src.sparkle.configurator.configurator import AblationScenario, ConfigurationScenario
from src.sparkle.configurator.implementations import (
    IRACEScenario,
    ParamILSScenario,
    SMAC2Scenario,
    SMAC3Scenario,
)
from src.sparkle.instance import Instance_Set
from src.sparkle.platform.output.configuration_output import ConfigurationOutput
from src.sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from src.sparkle.types import SolverStatus
from tests.CLI import tools

pl = pytest.importorskip("pylatex")


def test_parser() -> None:
    """Test argument parser."""
    parser = generate_report.parser_function()
    import argparse

    assert isinstance(parser, argparse.ArgumentParser)


def test_generate_configuration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate report for configuration."""
    # Not done
    return
    doc_path = tmp_path / "config_report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    report = pl.Document(default_filepath=str(doc_path))
    performance_df_path = Path(
        "tests/test_files/Output/Performance_Data/performance_data.csv"
    )
    performance_df = PerformanceDataFrame(performance_df_path)
    path_to_test_config = Path("tests/test_files/Configuration")
    test_sets = Instance_Set(
        Path("tests/test_files/Instances/Test-Instance-Set").absolute()
    )
    # train_sets = [
    #     Instance_Set(
    #         Path("tests/test_files/Instances/Train-Instance-Set/train_instance_1.cnf")
    #     )
    # ]

    cutoff_length = "3"
    concurrent_clis = 4
    best_configuration = {
        "init_solution": "2",
        "perform_first_div": "1",
        "asd": 5,
        "test_bool": True,
    }
    ablation_racing = False

    config_pairs = []
    for scenario_path in path_to_test_config.iterdir():
        configuration_scenario = None
        if not scenario_path.name.endswith("scenario.txt"):
            continue
        if "smac2" in str(scenario_path):
            configuration_scenario = SMAC2Scenario.from_file(scenario_path)
        elif "smac3" in str(scenario_path):
            continue
            configuration_scenario = SMAC3Scenario.from_file(scenario_path)
        elif "paramils" in str(scenario_path):
            configuration_scenario = ParamILSScenario.from_file(scenario_path)
        elif "irace" in str(scenario_path):
            configuration_scenario = IRACEScenario.from_file(scenario_path)
        if not configuration_scenario:
            continue
        assert isinstance(configuration_scenario, ConfigurationScenario)
        ablation_scenario = AblationScenario(
            configuration_scenario,
            test_sets,
            cutoff_length,
            concurrent_clis,
            best_configuration,
            ablation_racing,
        )
        configuration_scenario._ablation_scenario = ablation_scenario
        configuration_scenario.solver.directory = Path("Solvers/MiniSAT")
        assert configuration_scenario.ablation_scenario is not None
        config_output = ConfigurationOutput(
            configuration_scenario, performance_df, [test_sets]
        )
        config_pairs.append((config_output, configuration_scenario))

    Path(report.default_filepath).parent.mkdir(parents=True, exist_ok=True)

    for config_output, config_scenario in config_pairs:
        assert (
            generate_report.generate_configuration_section(
                report, config_scenario, config_output
            )
            is None
        )
    latex_output = report.dumps()
    assert "Parameter importance via Ablation" in latex_output
    assert "Ablation table" in latex_output


class DummyObjective:
    """A dummy objective for testing."""

    def __init__(self, name: str, time: bool = False) -> None:
        """Initialize dummy objective."""
        self.name = name
        self.time = time
        self.minimise = True

    def __str__(self) -> str:
        """String representation of the objective."""
        return self.name


class StubSettings:
    """Stub settings for testing."""

    def __init__(self, base_dir: Path) -> None:
        """Initialize stub settings."""
        self.DEFAULT_extractor_dir = base_dir / "extractors"
        self.DEFAULT_extractor_dir.mkdir(parents=True, exist_ok=True)
        self.parallel_portfolio_num_seeds_per_solver = 2
        self.solver_cutoff_time = 120


class SolverMapping(dict):
    """A mapping that replaces spaces with underscores in keys."""

    def __getitem__(self, key: str) -> list[str]:
        """Get item from mapping, replacing spaces with underscores."""
        return super().__getitem__(key.replace(" ", "_"))

    def get(self, key: str, default: list[str] | None = None) -> list[str] | None:
        """Get item from mapping, replacing spaces with underscores."""
        return super().get(key.replace(" ", "_"), default)

    def __contains__(self, key: str) -> bool:
        """Check if key is in mapping, replacing spaces with underscores."""
        return super().__contains__(key.replace(" ", "_"))


def test_generate_selection_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report for selection."""
    doc_path = tmp_path / "selection_report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    report = pl.Document(default_filepath=str(doc_path))

    settings = StubSettings(tmp_path)
    monkeypatch.setattr(generate_report.gv, "settings", lambda args=None: settings)

    extractor_stub = type("ExtractorStub", (), {"output_dimension": 5})()
    monkeypatch.setattr(
        generate_report,
        "resolve_object_name",
        lambda name, mapping, default_dir, class_name=None: extractor_stub,
    )

    plot_calls: list[tuple[str | None, Path]] = []

    class FakePlot:
        """A fake plot for testing."""

        def __init__(self, title: str | None) -> None:
            """Initialize fake plot."""
            self.title = title

        def write_image(self, path: Path, width: int, height: int) -> None:
            """Simulate writing an image by recording the call."""
            plot_calls.append((self.title, Path(path)))

    monkeypatch.setattr(
        generate_report.latex, "comparison_plot", lambda df, title: FakePlot(title)
    )
    monkeypatch.setattr(generate_report.latex, "AutoRef", lambda label: f"@{label}")

    class DummySelector:
        model_class = type("ModelClass", (), {"__name__": "DummyModel"})
        selector_class = type("SelectorClass", (), {"__name__": "DummySelector"})

    scenario = type(
        "SelectionScenario",
        (),
        {
            "selector": DummySelector(),
            "objective": DummyObjective("Quality"),
            "feature_extractors": ["Extractor_One"],
            "solver_cutoff": 55,
            "extractor_cutoff": 10,
            "name": "SelectionScenario",
        },
    )()

    scenario_output = type(
        "SelectionOutput",
        (),
        {
            "solvers": SolverMapping({"solver_one": ["conf1", "conf2"]}),
            "training_instance_sets": [("Train_Set", 3)],
            "marginal_contribution_perfect": [
                ("solver_one", "conf1", 0.5, 1.1),
                ("solver_one", "conf2", 0.3, 1.3),
            ],
            "marginal_contribution_actual": [
                ("solver_one", "conf1", 0.6, 1.2),
            ],
            "solver_performance_ranking": [
                ("solver_one", "conf1", 1.234),
                ("solver_one", "conf2", 1.567),
            ],
            "vbs_performance": 0.9,
            "actual_performance": 1.1,
            "sbs_performance": [1.2, 1.3],
            "actual_performance_data": [0.8, 0.9],
            "vbs_performance_data": pd.Series([0.6, 0.7]),
            "test_sets": [("Test_Set", 2)],
            "test_set_performance": {"Test_Set": 1.5},
        },
    )()

    generate_report.generate_selection_section(report, scenario, scenario_output)

    assert len(plot_calls) == 2
    latex_output = report.dumps()
    assert "Marginal Contribution Ranking List" in latex_output
    assert "Test Results" in latex_output


def test_generate_parallel_portfolio_section_reports_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report for parallel portfolio."""
    doc_path = tmp_path / "parallel_report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    report = pl.Document(default_filepath=str(doc_path))

    settings = StubSettings(tmp_path)
    monkeypatch.setattr(generate_report.gv, "settings", lambda args=None: settings)

    plot_calls: list[tuple[str | None, Path]] = []

    class FakePlot:
        """A fake plot for testing."""

        def __init__(self, title: str | None) -> None:
            """Initialize fake plot."""
            self.title = title

        def write_image(self, path: Path, width: int, height: int) -> None:
            """Simulate writing an image by recording the call."""
            plot_calls.append((self.title, Path(path)))

    monkeypatch.setattr(
        generate_report.latex, "comparison_plot", lambda df, title: FakePlot(title)
    )
    monkeypatch.setattr(generate_report.latex, "AutoRef", lambda label: f"@{label}")

    class DummyParallelScenario:
        """A dummy parallel scenario for testing."""

        def __init__(self, base_dir: Path) -> None:
            """Initialize dummy parallel scenario."""
            self.csv_filepath = base_dir / "portfolio_dir" / "data.csv"
            self.csv_filepath.parent.mkdir(parents=True, exist_ok=True)
            self.solvers = ["solver_a", "solver_b"]
            self._configs = {
                "solver_a": {"conf_a": {}},
                "solver_b": {"conf_b": {}},
            }
            self.instances = [
                "set_one/instance1",
                "set_two/instance2",
            ]
            self._objective = DummyObjective("runtime")
            self._performance = {"solver_a": 1.2, "solver_b": 2.4}
            self._status = {
                "solver_a": [SolverStatus.SUCCESS.value, SolverStatus.TIMEOUT.value],
                "solver_b": [SolverStatus.CRASHED.value, SolverStatus.SUCCESS.value],
            }

        @property
        def configurations(self) -> dict[str, dict[str, dict]]:
            """Get configurations."""
            return self._configs

        @property
        def objectives(self) -> list[DummyObjective]:
            """Get objectives."""
            return [self._objective]

        @property
        def objective_names(self) -> list[str]:
            """Get objective names."""
            return ["status_runtime", self._objective.name]

        def get_solver_ranking(
            self, objective: str, instances: list[str] | None = None
        ) -> list[tuple[str, str, float]]:
            """Get solver ranking."""
            if instances:
                if instances[0] == "set_one/instance1":
                    return [
                        ("solver_a", "conf_a", self._performance["solver_a"]),
                        ("solver_b", "conf_b", self._performance["solver_b"]),
                    ]
                return [
                    ("solver_b", "conf_b", self._performance["solver_b"]),
                    ("solver_a", "conf_a", self._performance["solver_a"]),
                ]
            return [
                ("solver_a", "conf_a", self._performance["solver_a"]),
                ("solver_b", "conf_b", self._performance["solver_b"]),
            ]

        def get_value(self, solver: str, objective: str) -> list[float] | list[int]:
            """Get value for solver and objective."""
            if objective == "status_runtime":
                return self._status[solver]
            if objective == self._objective.name:
                base = self._performance[solver]
                return [base, base + 1.0]
            raise KeyError(objective)

        def best_performance(self, objective: str) -> float:
            """Get best performance for objective."""
            return min(self._performance.values())

        def best_instance_performance(self, objective: str) -> pd.Series:
            """Get best instance performance for objective."""
            return pd.Series([0.5, 0.6])

    scenario = DummyParallelScenario(tmp_path)

    generate_report.generate_parallel_portfolio_section(report, scenario)

    assert len(plot_calls) == 1
    latex_output = report.dumps()
    assert "Parallel Portfolio" in latex_output
    assert "Parallel Portfolio Performance" in latex_output


@pytest.mark.parametrize(
    "caption, max_cols, wide_threshold, num_keys",
    [
        (
            "Performance DataFrame",
            MAX_COLS_PER_TABLE,
            WIDE_TABLE_THRESHOLD,
            NUM_KEYS_PDF,
        ),
        (
            "Feature DataFrame",
            MAX_COLS_PER_TABLE,
            WIDE_TABLE_THRESHOLD,
            NUM_KEYS_FDF,
        ),
    ],
)
def test_append_dataframe_longtable(
    tmp_path: Path,
    caption: str,
    max_cols: int,
    wide_threshold: int,
    num_keys: int,
) -> None:
    """Test append dataframe longtable."""
    doc_path = tmp_path / "report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    report = pl.Document(default_filepath=str(doc_path))
    dataframe_path = (
        "tests/test_files/Output/Performance_Data/performance_data.csv"
        if caption == "Performance DataFrame"
        else "tests/test_files/Output/Feature_Data/feature_data.csv"
    )
    current_dataframe = (
        PerformanceDataFrame(Path(dataframe_path))
        if caption == "Performance DataFrame"
        else FeatureDataFrame(Path(dataframe_path))
    )

    assert (
        generate_report.append_dataframe_longtable(
            report,
            current_dataframe,
            caption=caption,
            label=f"tab: {caption}",
            max_cols=max_cols,
            wide_threshold=wide_threshold,
            num_keys=num_keys,
        )
        is None
    )


def test_generate_appendix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate appendix."""
    doc_path = tmp_path / "report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    report = pl.Document(default_filepath=str(doc_path))
    feature_df_path = Path("tests/test_files/Output/Feature_Data/feature_data.csv")
    feature_df = FeatureDataFrame(feature_df_path)
    performance_df_path = Path(
        "tests/test_files/Output/Performance_Data/performance_data.csv"
    )
    performance_df = PerformanceDataFrame(performance_df_path)

    assert generate_report.generate_appendix(report, performance_df, feature_df) is None


@pytest.mark.parametrize(
    "args, case",
    [
        ([], 0),
        (["--only-json", "True"], 1),
        (["--solver", "PbO-CCSAT-Generic", "--instance-set", "PTN", "--appendices"], 2),
    ],
)
def test_main(args: list[str], case: int) -> None:
    """Test main of generate report."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # If report.pdf and/or output.json is generated, delete it first
        if Path("Output/Analysis/report/report.pdf").exists():
            Path("Output/Analysis/report/report.pdf").unlink()
        if Path("Output/Analysis/JSON/output.json").exists():
            Path("Output/Analysis/JSON/output.json").unlink()

        assert generate_report.main(args) is None
        # Check if the report.pdf file and output.json is generated
        assert Path("Output/Analysis/report/report.pdf").exists()
        assert Path("Output/Analysis/JSON/output.json").exists()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    if case == 1:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            # Since report.pdf is generated already in case = 0
            # see if it'll be deleted with --only-json True
            # and not created again
            if Path("Output/Analysis/JSON/output.json").exists():
                Path("Output/Analysis/JSON/output.json").unlink()
            assert generate_report.main(args) is None
            # Check if the report.pdf file is deleted
            assert not Path("Output/Analysis/report/report.pdf").exists()

            # Check if the output.json is generated
            assert Path("Output/Analysis/JSON/output.json").exists()
            assert pytest_wrapped_e.type is SystemExit
            assert pytest_wrapped_e.value.code == 0

    elif case == 2:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            performance_section_name = "Performance DataFrame"
            feature_section_name = "Feature DataFrame"
            assert generate_report.main(args) is None
            # Check if the appendices part is in report.pdf
            # by checking the file size and section presence
            report_path = Path("Output/Analysis/report/report.pdf")
            assert report_path.exists()
            assert report_path.stat().st_size > 10  # Arbitrary size check

            # To check the section presence, get the .tex file
            tex_path = Path("Output/Analysis/report/report.tex")
            assert tex_path.exists()
            with Path.open(tex_path, "r") as f:
                tex_content = f.read()
                assert f"\\section{{{performance_section_name}}}" in tex_content
                assert f"\\section{{{feature_section_name}}}" in tex_content

            assert pytest_wrapped_e.type is SystemExit
            assert pytest_wrapped_e.value.code == 0


@pytest.mark.integration
def test_generate_report_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report for configuration Smoke Test."""
    if tools.get_cluster_name() != "kathleen":
        # Test currently does not work on Github Actions due to PDF compilation error
        return
    snapshot_path = (
        Path("tests")
        / "CLI"
        / "test_files"
        / "snapshot_configured_solver_Pb0-CCSAT-Generic_PTN.zip"
    ).absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Smoke test
    # Generate report without any specifications (should auto detect)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        generate_report.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Generate report with training set only
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        generate_report.main(["--solver", "PbO-CCSAT-Generic", "--instance-set", "PTN"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.integration
def test_generate_report_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report for selection."""
    snapshot_no_testset_path = (
        Path("tests") / "CLI" / "test_files" / "snapshot_selection_"
        "pbo_csccsat_minisat_PTN_satzilla2012_no_test.zip"
    ).absolute()
    snapshot_testset_ptn2_path = (
        Path("tests") / "CLI" / "test_files" / "snapshot_selection_"
        "pbo_csccsat_minisat_PTN_satzilla2012_with_test_PTN2.zip"
    ).absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform for no test set snapshot
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_no_testset_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        generate_report.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Set up platform with test set
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_testset_ptn2_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        generate_report.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Add test with ablation results (Need a snapshot for that)


@pytest.mark.integration
def test_generate_report_parallel_portfolio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report for parallel portfolio."""
    if tools.get_cluster_name() != "kathleen":
        # Test currently does not work on Github Actions due to PDF compilation error
        return
    snapshot_parallel_portfolio = (
        Path("tests") / "CLI" / "test_files" / "snapshot_parallel_portfolio_"
        "pbo_csccsat_minisat_ptn.zip"
    ).absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Set up platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_parallel_portfolio)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    print([p for p in Path("Output/Parallel_Portfolio/").iterdir()])
    print(Path("Output/Parallel_Portfolio/"))

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        generate_report.main([])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.integration
def test_configuration_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate report configuration output (JSON)."""
    # TODO: Write test with actual / value content checking
    pass


@pytest.mark.integration
def test_selection_portfolio_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report selection output (JSON)."""
    # TODO: Write test with actual / value content checking
    pass


@pytest.mark.integration
def test_parallel_portfolio_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report parallel output (JSON)."""
    # TODO: Write Parallel Portfolio data to JSON
    # TODO: Write test with actual / value content checking
    pass
