"""Test the generate report CLI entry point."""

import pytest
from pathlib import Path

from sparkle.CLI import load_snapshot, generate_report

from tests.CLI import tools


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
