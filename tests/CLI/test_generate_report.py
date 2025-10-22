"""Test the generate report CLI entry point."""

from pathlib import Path
import pytest
import pylatex as pl

from sparkle.CLI import generate_report, load_snapshot
from sparkle.CLI.generate_report import (
    MAX_COLS_PER_TABLE,
    NUM_KEYS_FDF,
    NUM_KEYS_PDF,
    WIDE_TABLE_THRESHOLD,
)
from sparkle.configurator.configurator import AblationScenario, ConfigurationScenario
from sparkle.configurator.implementations import (
    IRACEScenario,
    ParamILSScenario,
    SMAC2Scenario,
    SMAC3Scenario,
)
from sparkle.instance import Instance_Set
from sparkle.platform.output.configuration_output import ConfigurationOutput
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.selector import SelectionScenario
from sparkle.platform.output.selection_output import SelectionOutput
from tests.CLI import tools


def test_parser() -> None:
    """Test argument parser."""
    parser = generate_report.parser_function()
    import argparse

    assert isinstance(parser, argparse.ArgumentParser)

    invalid_arg = ["TEST_TEST TESTTEST"]
    help_arg = ["--help"]
    only_json_arg = ["--only-json", "True"]
    full_args = [
        "--solver",
        "PbO-CCSAT-Generic",
        "--instance-set",
        "PTN",
        "--appendices",
    ]

    with pytest.raises(SystemExit) as invalid_wrapped:
        # Invalid argument should raise SystemExit with code 2
        parser.parse_args(invalid_arg)
    assert invalid_wrapped.type is SystemExit
    assert invalid_wrapped.value.code == 2

    with pytest.raises(SystemExit) as help_wrapped:
        # --help should exit with code 0
        parser.parse_args(help_arg)
    assert help_wrapped.type is SystemExit
    assert help_wrapped.value.code == 0

    only_json_args = parser.parse_args(only_json_arg)
    assert only_json_args.only_json is True

    full_parsed_args = parser.parse_args(full_args)
    assert full_parsed_args.solvers == ["PbO-CCSAT-Generic"]
    assert full_parsed_args.instance_sets == ["PTN"]
    assert full_parsed_args.appendices is True


def test_generate_selection_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test generate report for selection."""
    doc_path = tmp_path / "selection_report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    report = pl.Document(default_filepath=str(doc_path))
    selection_scenario = SelectionScenario.from_file(
        Path("tests/test_files/Selector/scenario/scenario_with_test.txt")
    )
    selection_output = SelectionOutput(selection_scenario)
    # Manually set marginal contribution actual for testing
    selection_output.marginal_contribution_actual = [
        ("Solvers/MiniSAT", "Default_Config", 1.2345, 6.789)
    ]

    assert (
        generate_report.generate_selection_section(
            report, selection_scenario, selection_output
        )
        is None
    )

    latex_output = report.dumps()
    assert "Marginal Contribution Ranking List" in latex_output
    assert "Test Results" in latex_output
    assert "\\textbf{Solvers/MiniSAT} (Default Config): 1.2345 (6.789)" in latex_output


def test_generate_configuration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate report for configuration."""
    doc_path = tmp_path / "config_report" / "report.tex"
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    report = pl.Document(default_filepath=str(doc_path))
    performance_df_path = Path(
        "tests/test_files/Output/Performance_Data/performance_data.csv"
    )
    performance_df = PerformanceDataFrame(performance_df_path)

    # Align performance data instance identifiers with the scenario expectations.
    instance_level = performance_df.index.get_level_values(
        PerformanceDataFrame.index_instance
    )
    # Get just the names of the instances and not the full path
    rename_map = {
        name: Path(str(name)).stem
        if isinstance(name, str) and "/" in str(name)
        else name
        for name in instance_level.unique()
    }
    performance_df.rename(
        index=rename_map,
        level=PerformanceDataFrame.index_instance,
        inplace=True,
    )
    path_to_test_config = Path("tests/test_files/Configuration")
    test_sets = Instance_Set(
        Path(
            "tests/test_files/Instances/Test-Instance-Set/test_instance_1.cnf"
        ).absolute()
    )

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
    for scenario in path_to_test_config.glob("*scenario.txt"):
        configuration_scenario = None
        if "smac2" in str(scenario):
            configuration_scenario = SMAC2Scenario.from_file(scenario)
        elif "smac3" in str(scenario):
            configuration_scenario = SMAC3Scenario.from_file(scenario)
        elif "paramils" in str(scenario):
            configuration_scenario = ParamILSScenario.from_file(scenario)
        elif "irace" in str(scenario):
            configuration_scenario = IRACEScenario.from_file(scenario)
        assert isinstance(configuration_scenario, ConfigurationScenario)
        ablation_with_config = AblationScenario(
            configuration_scenario,
            test_sets,
            cutoff_length,
            concurrent_clis,
            best_configuration,
            ablation_racing,
        )
        configuration_scenario._ablation_scenario = ablation_with_config

        # Reassign the read_ablation_table to test adding ablation table to report
        ablation_with_config.read_ablation_table = lambda self=ablation_with_config: [
            (1, "param_a", "0", "1", 0.5)
        ]
        assert configuration_scenario.ablation_scenario is not None
        config_output = ConfigurationOutput(
            configuration_scenario, performance_df, [test_sets]
        )

        # To cover the case, when best config is not the default one
        if (
            config_output.best_configuration_key
            == PerformanceDataFrame.default_configuration
        ):
            manual_best_key = "ManualBest"
            config_output.best_configuration_key = manual_best_key
            config_output.best_configuration = best_configuration
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
    assert "Best found configuration values" in latex_output


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
    # Check if caption is in the generated LaTeX
    assert caption in report.dumps()
    # Check for each page after section Performance / Feature DataFrame
    # If they exceed max_cols, there should be landscape environment
    latex_output = report.dumps()
    sections = latex_output.split(f"\\{caption}")
    assert len(sections) == 1  # Ensure section is present
    content_after_section = sections[0]
    # Count occurrences of longtables
    longtable_count = content_after_section.count("\\begin{longtable}")
    if current_dataframe.shape[1] > max_cols:
        # If number of columns exceed max_cols, there should be at least one landscape
        assert "\\begin{landscape}" in content_after_section
        assert longtable_count >= 1
    else:
        # If number of columns do not exceed max_cols, there should be no landscape
        assert "\\begin{landscape}" not in content_after_section
        assert longtable_count == 1  # Only one longtable without landscape


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

    # Unsafecommand appendix should be in the LaTeX output and also both dataframes
    latex_output = report.dumps()
    assert "\\appendix" in latex_output
    assert "Feature DataFrame" in latex_output
    assert "Performance DataFrame" in latex_output


def test_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main of generate report."""
    empty_args = []
    only_json_args = ["--only-json", "True"]
    full_args = [
        "--solver",
        "PbO-CCSAT-Generic",
        "--instance-set",
        "PTN",
        "--appendices",
    ]

    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Create needed files in tmp dir
    output_analysis_path = Path("Output/Analysis")
    output_analysis_path.mkdir(parents=True, exist_ok=True)
    (output_analysis_path / "report").mkdir(parents=True, exist_ok=True)
    (output_analysis_path / "JSON").mkdir(parents=True, exist_ok=True)
    performance_data_path = Path("Output/Performance_Data")
    performance_data_path.mkdir(parents=True, exist_ok=True)
    feature_data_path = Path("Output/Feature_Data")
    feature_data_path.mkdir(parents=True, exist_ok=True)
    instances_path = Path("Instances")
    instances_path.mkdir(parents=True, exist_ok=True)

    with pytest.raises(SystemExit) as empty_wrapped:
        assert generate_report.main(empty_args) is None
    assert empty_wrapped.type is SystemExit
    assert empty_wrapped.value.code == 0
    assert Path("Output/Analysis/report/report.pdf").exists()
    assert Path("Output/Analysis/JSON/output.json").exists()
    # JSON file should be empty
    json_content = Path("Output/Analysis/JSON/output.json").read_text()
    assert json_content.strip() == "{}"
    # Report file should have no appendices for empty args
    tex_content = Path("Output/Analysis/report/report.tex").read_text()
    assert "appendix" not in tex_content
    # Delete .pdf, to check only_json next
    Path("Output/Analysis/report/report.pdf").unlink()

    with pytest.raises(SystemExit) as only_json_wrapped:
        assert generate_report.main(only_json_args) is None
    assert only_json_wrapped.type is SystemExit
    assert only_json_wrapped.value.code == 0
    assert Path("Output/Analysis/JSON/output.json").exists()
    # report.pdf shouldn't be there
    assert not Path("Output/Analysis/report/report.pdf").exists()
    json_content = Path("Output/Analysis/JSON/output.json").read_text()
    assert json_content.strip() == "{}"

    with pytest.raises(SystemExit) as full_wrapped:
        assert generate_report.main(full_args) is None
    assert full_wrapped.type is SystemExit
    assert full_wrapped.value.code == 0
    assert Path("Output/Analysis/JSON/output.json").exists()
    assert Path("Output/Analysis/report/report.pdf").exists()
    json_content = Path("Output/Analysis/JSON/output.json").read_text()
    assert json_content.strip() == "{}"
    # Report file should have appendices for full args
    tex_content = Path("Output/Analysis/report/report.tex").read_text()
    assert "appendix" in tex_content


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
