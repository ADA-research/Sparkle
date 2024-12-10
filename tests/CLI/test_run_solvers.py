"""Test the run solvers CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import add_solver, run_solvers
from sparkle.CLI import add_instances
from tests.CLI import tools as cli_tools


def test_run_solvers_performance_dataframe() -> None:
    """Run solvers that write to the performance dataframe."""
    # TODO: Write test
    pass


@pytest.mark.integration
def test_run_solvers(tmp_path: Path,
                     monkeypatch: pytest.MonkeyPatch) -> None:
    """Test run solvers command without using PerformanceDataFrame."""
    solver_path = (Path("Examples") / "Resources" / "Solvers" / "CSCCSat").absolute()
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
        run_solvers.main(["--run-on", "local",
                          "--settings-file", str(settings_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Check if testing with Slurm is relevant for system
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run_solvers.main(["--run-on", "slurm",
                          "--settings-file", str(settings_path)])
    cli_tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    # TODO: Write a test for Solver without configuration
    # TODO: Write a test for Solver with best configuration over some instances
    # TODO: Write a test for Solver with specific configuration
