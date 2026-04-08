"""File to help with RunRunner jobs."""

import sys
from pathlib import Path

from runrunner.base import Status
from runrunner.slurm import SlurmRun

from sparkle.types import DataFileLock


# Maps job name prefixes to the data file they lock
JOB_NAME_LOCKS: dict[str, DataFileLock] = {
    "Run Solver ": DataFileLock.PERFORMANCE,
    "Run Extractor ": DataFileLock.FEATURE,
}


def get_locking_runs(
    path: Path,
    locks: set[DataFileLock],
) -> tuple[list[SlurmRun], list[SlurmRun]]:
    """Return running and waiting jobs that lock the given data files.

    Args:
        path: Path to search for RunRunner job JSON files.
        locks: Set of DataFileLock values to check against.

    Returns:
        A tuple (running, waiting) of SlurmRun lists that overlap with the
        given locks.
    """
    running = []
    waiting = []
    # Collect only the name prefixes that correspond to the requested lock types,
    # so we skip jobs that write to unrelated data files.
    relevant_prefixes = {p for p, lock in JOB_NAME_LOCKS.items() if lock in locks}
    for run in get_runs_from_file(path, filter=[Status.RUNNING, Status.WAITING]):
        if any(run.name.startswith(p) for p in relevant_prefixes):
            if run.status == Status.RUNNING:
                running.append(run)
            else:
                waiting.append(run)
    return running, waiting


def check_running_waiting_jobs(path: Path, locks: set[DataFileLock]) -> None:
    """Check for running/waiting jobs that lock the given data files.

    Exits with -1 if running jobs are found.
    Asks the user whether to continue if only waiting jobs are found, and
    exits with -1 if the user declines.

    Args:
        path: Path to search for RunRunner job JSON files.
        locks: Set of DataFileLock values to check against.
    """
    # Build a human-readable string of the affected data files for the warning
    # messages, e.g. "Performance Data or Feature Data".
    lock_names = " or ".join(lock.value.capitalize() + " Data" for lock in locks)
    running, waiting = get_locking_runs(path, locks)
    if running:
        print(
            f"WARNING: There are {len(running)} running job(s) writing to the "
            f"{lock_names}. Please cancel them before modifying the platform."
        )
        sys.exit(-1)
    if waiting:
        print(
            f"WARNING: There are {len(waiting)} waiting job(s) that will write "
            f"to the {lock_names}. These may conflict with this operation. "
            "Continue? [y/n]"
        )
        if input() != "y":
            sys.exit(-1)


def get_runs_from_file(
    path: Path, print_error: bool = False, filter: list[Status] = None
) -> list[SlurmRun]:
    """Retrieve all run objects from file storage.

    Args:
        path: Path object where to look recursively for the files.
        print_error: Whether to print errors.
        filter: If not None, only runs with the given statuses will be
            returned.

    Returns:
        List of all found SlumRun objects.
    """
    runs = []
    for file in path.rglob("*.json"):
        # TODO: RunRunner should be adapted to have more general methods for runs
        # So this method can work for both local and slurm
        try:
            run_obj = SlurmRun.from_file(file)
            if filter is None or run_obj.status in filter:
                runs.append(run_obj)
        except Exception as ex:
            # Not a (correct) RunRunner JSON file
            if print_error:
                print(f"[WARNING] Could not load file: {file}. Exception: {ex}")
    return runs
