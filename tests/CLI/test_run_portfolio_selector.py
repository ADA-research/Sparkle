"""Test the run portfolio selector CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import (load_snapshot, run_portfolio_selector,
                         add_feature_extractor, add_solver)

from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_run_portfolio_selector_command(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run portfolio command."""
    snapshot_path = (
        Path("tests") / "CLI" / "test_files"
        / "snapshot_constructed_portfolio_selector_csccsat_minisat_ptn.zip").absolute()
    example_file_path = (Path("Examples") / "Resources"
                         / "Instances" / "PTN2" / "Ptn-7824-b20.cnf").absolute()
    extractor_path = (
        Path("Examples") / "Resources" / "Extractors"
        / "SAT-features-competition2012_revised_without_SatELite_sparkle").absolute()
    solver_csccsat_path = (
        Path("Examples") / "Resources" / "Solvers" / "CSCCSat").absolute()
    solver_minisat_path = (
        Path("Examples") / "Resources" / "Solvers" / "MiniSAT").absolute()
    example_test_set_path = (
        Path("Examples") / "Resources" / "Instances" / "PTN2").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Set up platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add feature extractor
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_feature_extractor.main([str(extractor_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add solver
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_csccsat_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_minisat_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Smoke test
    # Run set test slurm
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_portfolio_selector.main([str(example_test_set_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Run single file test local
    # NOTE: These tests only work in this order (First Slurm then Local), not sure why
    # Without this order the test doesn't fail but simply doesn't complete
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_portfolio_selector.main([str(example_file_path),
                                     "--run-on", "local"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
