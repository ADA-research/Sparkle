"""Test the run solvers CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import add_solver, run_solvers, add_instances, load_snapshot
from tests.CLI import tools as cli_tools


@pytest.mark.integration
def test_run_solvers_performance_dataframe(tmp_path: Path,
                                           monkeypatch: pytest.MonkeyPatch) -> None:
    """Run solvers that write to the performance dataframe."""
    solver_path =\
        (Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic").absolute()
    instances_path = (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    settings_path = cli_tools.get_settings_path()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Smoke test
    # First we add solvers and instances to the platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(instances_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Second we test the command twice, once with local and once with slurm
    # NOTE: Expensive local test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--performance-data-jobs",
                          "--run-on", "local",
                          "--settings-file", str(settings_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Check if testing with Slurm is relevant for system
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--performance-data-jobs",
                          "--recompute",
                          "--run-on", "slurm",
                          "--settings-file", str(settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.integration
def test_run_solvers_configured(tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run solvers command with a configuration."""
    configured_snapshot = (
        Path("tests") / "CLI" / "test_files"
        / "snapshot_configured_solver_Pb0-CCSAT-Generic_PTN.zip").absolute()
    test_instance = (Path("Examples") / "Resources" / "Instances"
                     / "PTN2" / "Ptn-7824-b20.cnf").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(configured_snapshot)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test for Solver without configuration (Default)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--instance", str(test_instance),
                          "--run-on", "local"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test for Solver with best configuration over some instances
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--best-configuration", "PTN",
                          "--instance", str(test_instance),
                          "--run-on", "local"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test for Solver with specific configuration (2nd best)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--configuration", "SMAC2_20250523115757_6",
                          "--instance", str(test_instance),
                          "--run-on", "local"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # We don't test all configurations as its too expensive
