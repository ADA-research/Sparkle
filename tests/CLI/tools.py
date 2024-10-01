"""Tools for testing Sparkle CLI."""
import os
from pathlib import Path

from sparkle.CLI.wait import get_runs_from_file


def kill_slurm_jobs(command_log_dir: Path = None) -> None:
    """Kill all slurm jobs in the log directory.

    Args:
        command_log_dir: The directory where to look for jobs to kill.
            If not given, will detect the newest command log and kill all jobs in there.
    """
    # TODO: Cancel slurm jobs with Sparkle command
    if command_log_dir is None:
        command_log_dir = sorted([p for p in (Path("Output") / "Log").iterdir()],
                                 key=lambda p: os.stat(p).st_mtime)[-1]
    jobs = get_runs_from_file(command_log_dir)
    for j in jobs:
        j.kill()
