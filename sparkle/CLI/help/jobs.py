"""File to help with RunRunner jobs."""
from pathlib import Path

from tabulate import tabulate

from runrunner.base import Status
from runrunner.slurm import SlurmRun

from sparkle.platform.cli_types import TEXT


def get_runs_from_file(path: Path, print_error: bool = False) -> list[SlurmRun]:
    """Retrieve all run objects from file storage.

    Args:
        path: Path object where to look recursively for the files.

    Returns:
        List of all found SlumRun objects.
    """
    runs = []
    for file in path.rglob("*.json"):
        # TODO: RunRunner should be adapted to have more general methods for runs
        # So this method can work for both local and slurm
        try:
            run_obj = SlurmRun.from_file(file)
            runs.append(run_obj)
        except Exception as ex:
            # Not a (correct) RunRunner JSON file
            if print_error:
                print(f"[WARNING] Could not load file: {file}. Exception: {ex}")
    return runs


def create_jobs_table(jobs: list[SlurmRun], markup: bool = True) -> str:
    """Create a table of jobs.

    Args:
        runs: List of SlurmRun objects.
        markup: By default some mark up will be applied to the table.
            If false, a more plain version will be created.

    Returns:
        A table of jobs as a string.
    """
    job_table = [["RunId", "Name", "Quality of Service", "Partition", "Status",
                  "Dependencies", "Finished Jobs", "Run Time"]]
    for job in jobs:
        # Count number of jobs that have finished
        finished_jobs_count = sum(1 for status in job.all_status
                                  if status == Status.COMPLETED)
        if markup:  # Format job.status
            status_text = \
                TEXT.format_text([TEXT.BOLD], job.status) \
                if job.status == Status.RUNNING else \
                (TEXT.format_text([TEXT.ITALIC], job.status)
                    if job.status == Status.COMPLETED else job.status)
        else:
            status_text = job.status
        job_table.append(
            [job.run_id,
             job.name,
             job.qos,
             job.partition,
             status_text,
             "None" if len(job.dependencies) == 0 else ", ".join(job.dependencies),
             f"{finished_jobs_count}/{len(job.all_status)}",
             job.runtime])
    if markup:
        return tabulate(job_table, headers="firstrow", tablefmt="grid")
    return job_table
