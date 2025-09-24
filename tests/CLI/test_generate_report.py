"""Test the generate report CLI entry point."""

import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, generate_report

from tests.CLI import tools


def test_parser() -> None:
    """Test argument parser."""
    parser = generate_report.parser_function()
    import argparse

    assert isinstance(parser, argparse.ArgumentParser)


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

        generate_report.main(args) is None
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
            generate_report.main(args) is None
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
