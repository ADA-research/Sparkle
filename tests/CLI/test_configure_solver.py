"""Test the cancel CLI entry point."""
import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from sparkle.CLI import add_solver, add_instances, configure_solver
from sparkle.configurator.implementations import IRACE

from tests.CLI import tools


@pytest.mark.integration
@patch("shutil.which")
def test_configure_solver(mock_which: Mock,
                          tmp_path: Path,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancel command on configuration jobs."""
    # Smoke test: Submit configuration jobs
    solver_path =\
        (Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic").absolute()
    instance_set_path =\
        (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    test_settings_path = tools.get_settings_path()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Add solver
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Add instances
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(instance_set_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Mock shlex to avoid Sparkle throwing an exception because Java is not loaded
    mock_which.return_value("Java")

    # Submit configure solver job and validation job
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        configure_solver.main(["--solver", solver_path.name,
                               "--instance-set-train", instance_set_path.name,
                               "--objectives", "PAR10",
                               "--settings-file", str(test_settings_path),
                               "--run-on", "slurm"])
    tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Submit with different command line parameters

    # --number-of-runs 5
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        configure_solver.main(["--solver", solver_path.name,
                               "--instance-set-train", instance_set_path.name,
                               "--objectives", "PAR10",
                               "--settings-file", str(test_settings_path),
                               "--number-of-runs", "5",
                               "--run-on", "slurm"])
    tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # with IRACE instead of SMAC2
    if not IRACE.check_requirements():
        import warnings
        warnings.warn("WARNING: IRACE not installed, skipping test.")
        return
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        configure_solver.main(["--configurator", "IRACE",
                               "--solver", solver_path.name,
                               "--instance-set-train", instance_set_path.name,
                               "--objectives", "PAR10",
                               "--settings-file", str(test_settings_path),
                               "--run-on", "slurm"])
    tools.kill_slurm_jobs()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Local Test
    # Doesnt work currently as RunRunner cannot handle output paths for local jobs
    # NOTE: Expensive?
