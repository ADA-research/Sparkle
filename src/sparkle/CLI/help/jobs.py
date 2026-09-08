"""File to help with RunRunner jobs."""

import sys
import inspect
from pathlib import Path

from runrunner.base import Status
from runrunner.slurm import SlurmRun

from sparkle.types import DataFileLock


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
    # Maps job name prefixes to the data file they lock
    job_name_locks: dict[str, DataFileLock] = {
        "Run Solver ": DataFileLock.PERFORMANCE,
        "Run Extractor ": DataFileLock.FEATURE,
    }
    running = []
    waiting = []
    # Collect only the name prefixes that correspond to the requested lock types,
    # so we skip jobs that write to unrelated data files.
    relevant_prefixes = {
        prefix for prefix, lock in job_name_locks.items() if lock in locks
    }
    for run in get_runs_from_file(path, filter=[Status.RUNNING, Status.WAITING]):
        if any(run.name.startswith(prefix) for prefix in relevant_prefixes):
            if run.status == Status.RUNNING:
                running.append(run)
            else:
                waiting.append(run)
    return running, waiting


def check_running_waiting_jobs(
    path: Path, locks: set[DataFileLock] | None = None
) -> None:
    """Check for running/waiting jobs that lock the calling command's data files.

    For standard CLI commands (locks=None): derives the relevant locks by looking
    up the calling command's filename in the internal mapping. Raises KeyError if
    the caller is not registered.

    For cleanup only (locks provided): uses the given lock set directly, since
    cleanup determines its locks from CLI flags at runtime. Any other caller
    passing explicit locks raises ValueError.

    Exits with -1 if running jobs are found.
    Asks the user whether to continue if only waiting jobs are found, and
    exits with -1 if the user declines.

    Args:
        path: Path to search for RunRunner job JSON files.
        locks: Only cleanup.py may pass this. All other callers must omit it.
    """
    # Internal mapping: which data files each CLI command structurally modifies.
    # cleanup is intentionally absent — it determines its locks from CLI flags.
    cli_command_locks: dict[str, set[DataFileLock]] = {
        "add_solver": {DataFileLock.PERFORMANCE},
        "remove_solver": {DataFileLock.PERFORMANCE},
        "add_instances": {DataFileLock.PERFORMANCE, DataFileLock.FEATURE},
        "remove_instances": {DataFileLock.PERFORMANCE, DataFileLock.FEATURE},
        "add_feature_extractor": {DataFileLock.FEATURE},
        "remove_feature_extractor": {DataFileLock.FEATURE},
        "run_portfolio_selector": {DataFileLock.PERFORMANCE, DataFileLock.FEATURE},
    }

    def get_locks() -> set[DataFileLock]:
        """Validate the caller and return the appropriate lock set."""
        # inspect.stack()[2]: 0=get_locks, 1=check_running_waiting_jobs, 2=caller
        caller = Path(inspect.stack()[2].filename).stem
        if locks is not None:
            # Explicit locks are only permitted for cleanup
            if caller != "cleanup":
                raise ValueError(f"'{caller}' cannot pass explicit locks. ")
            return locks
        if caller not in cli_command_locks:
            raise KeyError(f"'{caller}' is not registered in the lock commands. ")
        return cli_command_locks[caller]

    resolved_locks = get_locks()
    # Build a human-readable string of the affected data files for the warning
    # messages, e.g. "PERFORMANCE_DATA or FEATURE_DATA".
    lock_names = " or ".join(lock.value.capitalize() for lock in resolved_locks)
    running, waiting = get_locking_runs(path, resolved_locks)
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
    path: Path, print_error: bool = False, filter: list[Status] | None = None
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
    if not path.exists():
        return []
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
