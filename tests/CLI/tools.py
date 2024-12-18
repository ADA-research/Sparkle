"""Tools for testing Sparkle CLI."""
import os
import json
import subprocess
from pathlib import Path

from sparkle.CLI.help import jobs as jobs_help


__cluster_name = None


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


def get_cluster_name() -> str:
    """Get the cluster name."""
    global __cluster_name
    if __cluster_name is None:
        output = subprocess.run(["sacctmgr", "show", "Cluster", "--json"],
                                capture_output=True).stdout.decode()
        try:
            cluster_info = json.loads(output)
            __cluster_name = cluster_info["clusters"][0]["name"].lower()
        except Exception:
            __cluster_name = "default"
    return __cluster_name


def get_settings_path() -> Path:
    """Get the absolute settings path corresponding to the compute cluster."""
    settings_dir = Path("tests") / "CLI" / "test_files" / "Settings"
    cluster_name = get_cluster_name()
    if cluster_name == "kathleen":  # AIM
        return (settings_dir / "sparkle_settings_kathleen.ini").absolute()
    # TODO: Add Grace (LIACS)
    return (settings_dir / "sparkle_settings_default.ini").absolute()
