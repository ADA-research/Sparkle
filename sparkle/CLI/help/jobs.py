"""File to help with RunRunner jobs."""
from pathlib import Path

from runrunner.base import Status
from runrunner.slurm import SlurmRun


def get_runs_from_file(path: Path,
                       print_error: bool = False,
                       filter: list[Status] = None) -> list[SlurmRun]:
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
