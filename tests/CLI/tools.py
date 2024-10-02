"""Tools for testing Sparkle CLI."""
import os
from pathlib import Path

from sparkle.CLI.help import jobs as jobs_help


def kill_slurm_jobs(command_log_dir: Path = None) -> None:
    """Kill all slurm jobs in the log directory.

    Args:
        command_log_dir: The directory where to look for jobs to kill.
            If not given, will detect the latest command and kill all its jobs.
    """
    if command_log_dir is None:
        command_log_dir = sorted([p for p in (Path("Output") / "Log").iterdir()],
                                 key=lambda p: os.stat(p).st_mtime)[-1]
    jobs = jobs_help.get_runs_from_file(command_log_dir)
    for j in jobs:
        j.kill()
