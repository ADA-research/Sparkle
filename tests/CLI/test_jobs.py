"""Test the cancel CLI entry point."""

import shutil
import pytest
from pathlib import Path
from unittest.mock import patch

from sparkle.configurator.implementations import SMAC2

from sparkle.CLI import initialise, add_solver, add_instances, configure_solver
from sparkle.CLI import jobs as sparkle_jobs
from sparkle.CLI.help import jobs as jobs_help
from sparkle.CLI.help import global_variables as gv

from tests.CLI import tools
from sparkle.types import DataFileLock

from runrunner.base import Status
from runrunner.slurm import SlurmRun


def copy_fixtures(tmp_path: Path, *names: str) -> None:
    """Copy named fixture files from fixture_jobs_dir into tmp_path."""
    fixture_jobs_dir = Path(__file__).parent.parent / "test_files" / "jobs"
    for name in names:
        shutil.copy(fixture_jobs_dir / name, tmp_path / name)


_SOLVER_FIXTURES = ("run_solver_running.json", "run_solver_waiting.json")
_EXTRACTOR_FIXTURES = ("run_extractor_running.json", "run_extractor_waiting.json")


@pytest.mark.parametrize(
    "fixture_names, locks, expected_running, expected_waiting",
    [
        (_SOLVER_FIXTURES, set(), 0, 0),  # empty set: nothing matches
        (
            _SOLVER_FIXTURES,
            {DataFileLock.PERFORMANCE},
            1,
            1,
        ),  # solver files match PERFORMANCE
        (
            _SOLVER_FIXTURES,
            {DataFileLock.FEATURE},
            0,
            0,
        ),  # solver files don't match FEATURE
        (
            _EXTRACTOR_FIXTURES,
            {DataFileLock.FEATURE},
            1,
            1,
        ),  # extractor files match FEATURE
        (
            _EXTRACTOR_FIXTURES,
            {DataFileLock.PERFORMANCE},
            0,
            0,
        ),  # extractor files don't match PERFORMANCE
    ],
    ids=[
        "empty_locks",
        "performance",
        "no_matching_perf",
        "feature",
        "no_matching_feat",
    ],
)
def test_get_locking_runs(
    tmp_path: Path,
    fixture_names: tuple,
    locks: set,
    expected_running: int,
    expected_waiting: int,
) -> None:
    """get_locking_runs correctly filters runs by lock type."""
    copy_fixtures(tmp_path, *fixture_names)
    with patch.object(SlurmRun, "get_latest_job_details", return_value=None):
        running, waiting = jobs_help.get_locking_runs(tmp_path, locks)
    assert len(running) == expected_running
    assert len(waiting) == expected_waiting
    if expected_running:
        assert running[0].status == Status.RUNNING
    if expected_waiting:
        assert waiting[0].status == Status.WAITING


@pytest.mark.parametrize(
    "filter_arg, expected_count, expected_status",
    [
        (None, 2, None),  # no filter: all runs returned
        ([Status.RUNNING], 1, Status.RUNNING),  # only the running run
        ([Status.WAITING], 1, Status.WAITING),  # only the waiting run
    ],
    ids=["no_filter", "filter_running", "filter_waiting"],
)
def test_get_runs_from_file(
    tmp_path: Path,
    filter_arg: list | None,
    expected_count: int,
    expected_status: Status | None,
) -> None:
    """get_runs_from_file returns the correct runs for a given status filter."""
    copy_fixtures(tmp_path, "run_solver_running.json", "run_solver_waiting.json")
    with patch.object(SlurmRun, "get_latest_job_details", return_value=None):
        runs = jobs_help.get_runs_from_file(tmp_path, filter=filter_arg)
    assert len(runs) == expected_count
    if expected_status is not None:
        assert runs[0].status == expected_status


def test_get_runs_from_file_nonexistent_path(tmp_path: Path) -> None:
    """get_runs_from_file on a non-existent path should return empty list."""
    result = jobs_help.get_runs_from_file(tmp_path / "does_not_exist")
    assert result == []


def test_get_runs_from_file_invalid_json(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """get_runs_from_file should skip unreadable files and print a warning when asked."""
    (tmp_path / "bad_run.json").write_text("not valid json {{{")

    # Without print_error: silently skips the bad file, returns empty list
    runs = jobs_help.get_runs_from_file(tmp_path)
    assert runs == []
    assert capsys.readouterr().out == ""

    # With print_error=True: skips the bad file but prints a WARNING line
    runs = jobs_help.get_runs_from_file(tmp_path, print_error=True)
    assert runs == []
    assert "[WARNING]" in capsys.readouterr().out


@pytest.mark.parametrize(
    "fixture_names, caller, locks, user_input, expect_exit, expect_error",
    [
        # No locking jobs present: should return without exiting
        ((), "add_solver.py", None, None, False, None),
        # Running locking job: should exit -1 immediately
        (("run_solver_running.json",), "add_solver.py", None, None, True, None),
        # Waiting job and user confirms: should continue
        (("run_solver_waiting.json",), "add_solver.py", None, "y", False, None),
        # Waiting job and user declines: should exit -1
        (("run_solver_waiting.json",), "add_solver.py", None, "n", True, None),
        # Caller not in the internal mapping: should raise KeyError
        ((), "unknown_command.py", None, None, False, KeyError),
        # Non-cleanup caller passing explicit locks: should raise ValueError
        ((), "add_solver.py", {DataFileLock.PERFORMANCE}, None, False, ValueError),
        # cleanup.py passing explicit locks: should be allowed (no jobs present)
        ((), "cleanup.py", {DataFileLock.PERFORMANCE}, None, False, None),
    ],
    ids=[
        "no_jobs",
        "running_jobs",
        "waiting_confirm",
        "waiting_decline",
        "unregistered_caller",
        "non_cleanup_explicit",
        "cleanup_explicit",
    ],
)
def test_check_running_waiting_jobs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fixture_names: tuple,
    caller: str,
    locks: set[DataFileLock] | None,
    user_input: str | None,
    expect_exit: bool,
    expect_error: type | None,
) -> None:
    """check_running_waiting_jobs correctly gates CLI commands based on active jobs."""

    def make_stack(caller_filename: str) -> list:
        """Build a mock inspect.stack() return value with the given caller filename."""
        from unittest.mock import MagicMock

        return [
            MagicMock(),  # [0] get_locks frame
            MagicMock(),  # [1] check_running_waiting_jobs frame
            MagicMock(filename=caller_filename),  # [2] actual caller
        ]

    if fixture_names:
        copy_fixtures(tmp_path, *fixture_names)
    if user_input is not None:
        monkeypatch.setattr("builtins.input", lambda: user_input)

    stack_patch = patch(
        "sparkle.CLI.help.jobs.inspect.stack",
        return_value=make_stack(caller),
    )
    scontrol_patch = patch.object(SlurmRun, "get_latest_job_details", return_value=None)

    with stack_patch, scontrol_patch:
        if expect_error is not None:
            with pytest.raises(expect_error):
                jobs_help.check_running_waiting_jobs(tmp_path, locks)
        elif expect_exit:
            with pytest.raises(SystemExit) as exc:
                jobs_help.check_running_waiting_jobs(tmp_path, locks)
            assert exc.value.code == -1
        else:
            jobs_help.check_running_waiting_jobs(tmp_path, locks)  # must not raise


@pytest.mark.integration
def test_cancel_command_no_jobs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cancel command with no jobs."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Fix input calls to test with NO (e.g. no download)
    monkeypatch.setattr("builtins.input", lambda: "N")
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # Call the command
        initialise.main([])
        # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test with nothing to cancel
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        sparkle_jobs.main(["--cancel", "--all"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -1

    # Test with an ID that does not exist
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        sparkle_jobs.main(["--cancel", "--job-ids", "1234"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -1


@pytest.mark.integration
def test_cancel_command_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test cancel command on configuration jobs."""
    if tools.get_cluster_name() != "kathleen":
        # Test currently does not work on Github Actions due to truncating
        return
    if shutil.which("java") is None:
        # Requires Java for SMAC2
        return
    if not SMAC2.check_requirements():
        SMAC2.download_requirements()
    # Submit configuration jobs and cancel it by ID
    solver_path = (
        Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic"
    ).absolute()
    instance_set_path = (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    settings_file = tools.get_settings_path()
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
        configure_solver.main(
            [
                "--solver",
                solver_path.name,
                "--instance-set-train",
                instance_set_path.name,
                "--settings-file",
                str(settings_file),
            ]
        )
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Extract job IDs from Sparkle
    jobs = jobs_help.get_runs_from_file(
        gv.settings().DEFAULT_log_output, print_error=True
    )

    # Cancel configuration jobs
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        sparkle_jobs.main(["--cancel", "--job-ids"] + [str(job.run_id) for job in jobs])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Property checks
    assert len(jobs) == 3  # Configuration should submit 3 jobs

    # NOTE: Here we check for killed and completed because we're not fast enough
    # TODO: Start a different job to cancel that wont be able to finish before we cancel
    for job in jobs:  # All jobs have been cancelled
        job.get_latest_job_details()
        assert job.status in [Status.KILLED, Status.COMPLETED]
