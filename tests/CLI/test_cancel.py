"""Test the cancel CLI entry point."""
import pytest
from pathlib import Path
import time

from sparkle.CLI import initialise, cancel, add_solver, add_instances, configure_solver
from sparkle.CLI.help import jobs as jobs_help
from sparkle.CLI.help import global_variables as gv

from runrunner.base import Status


@pytest.mark.integration
def test_cancel_command_no_jobs(tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancel command with no jobs."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # Call the command
        initialise.main([])
        # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test with nothing to cancel
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cancel.main(["--all"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test with an ID that does not exist
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cancel.main(["--job-ids", "1234"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -1


@pytest.mark.integration
def test_cancel_command_configuration(tmp_path: Path,
                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancel command on configuration jobs."""
    # Submit configuration jobs and cancel it by ID
    solver_path =\
        (Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic").absolute()
    instance_set_path =\
        (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    settings_file =\
        (Path("tests") / "CLI" / "test_files" / "Settings"
         / "sparkle_settings.ini").absolute()
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

    # Submit configure solver job and validation job
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        configure_solver.main(["--solver", solver_path.name,
                               "--instance-set-train", instance_set_path.name,
                               "--settings-file", str(settings_file)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Extract job IDs from Sparkle
    time.sleep(1)  # Wait to allow slurmDB to update
    jobs = jobs_help.get_runs_from_file(gv.settings().DEFAULT_log_output)

    # Cancel configuration jobs
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cancel.main(["--job-ids"] + [str(job.run_id) for job in jobs])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Property checks
    assert len(jobs) == 2  # Configuration should submit have 2 jobs

    time.sleep(10)  # Wait to allow slurmDB to update, could be reduced in the future
    for job in jobs:  # All jobs have been cancelled
        assert job.status == Status.KILLED