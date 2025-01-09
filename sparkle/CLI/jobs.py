#!/usr/bin/env python3
"""Command to interact with async jobs."""
import sys
import time
import argparse

import pytermgui as ptg
from tabulate import tabulate

from runrunner.base import Status, Run
from runrunner.slurm import SlurmRun

from sparkle.platform.cli_types import TEXT
from sparkle.CLI.help import logging
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import jobs as jobs_help
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Create parser for the jobs command."""
    parser = argparse.ArgumentParser(description="Command to interact with async jobs. "
                                                 "The command starts an interactive "
                                                 "table when no flags are given. Jobs "
                                                 "can be selected for cancelling in the "
                                                 "table and non activate jobs can be "
                                                 "flushed by pressing the spacebar.")
    parser.add_argument(*ac.CancelJobsArgument.names, **ac.CancelJobsArgument.kwargs)
    parser.add_argument(*ac.JobIDsArgument.names, **ac.JobIDsArgument.kwargs)
    parser.add_argument(*ac.AllJobsArgument.names, **ac.AllJobsArgument.kwargs)
    return parser


def create_jobs_table(jobs: list[SlurmRun],
                      markup: bool = True,
                      format: str = "grid") -> str:
    """Create a table of jobs.

    Args:
        runs: List of SlurmRun objects.
        markup: By default some mark up will be applied to the table.
            If false, a more plain version will be created.
        format: The tabulate format to use.
        per_job: If true, returns a dict with the job ids as keys and
            The lines per job as values.

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
                    if job.status == Status.COMPLETED else job.status.value)
        else:
            status_text = job.status.value
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
        job_table = tabulate(job_table, headers="firstrow", tablefmt=format,
                             maxcolwidths=[12, 32, 14, 12, 16, 16, 16, 10])
    return job_table


def table_gui(jobs: list[Run]) -> None:
    """Display a table of running jobs."""
    jobs = sorted(jobs, key=lambda j: j.run_id)
    ptg.Button.chars = {"delimiter": ["", ""]}  # Disable padding around buttons

    def cancel_jobs(self: ptg.Button) -> None:
        """Cancel jobs based on a button click."""
        job_id = self.label.split("|")[1].strip()
        job = job_id_map[job_id]

        def kill_exit(self: ptg.Button) -> None:
            """Two step protocol of killing the job and removing the popup."""
            job.kill()
            manager.remove(popup)

        button_yes = ptg.Button("Yes", kill_exit)
        button_no = ptg.Button("No", lambda *_: manager.remove(popup))

        popup = manager.alert(ptg.Label(f"Cancel job {job_id}?"),
                              button_no, button_yes)

        refresh_data(self.parent)

    def refresh_data(self: ptg.Window | ptg.WindowManager, key: str = None) -> None:
        """Refresh the table."""
        # Resolve window
        window = self._windows[-1] if isinstance(self, ptg.WindowManager) else self
        # Fetch latest data
        for job in jobs:
            if job.status in [Status.WAITING, Status.RUNNING]:
                job.get_latest_job_details()
        job_table = create_jobs_table(jobs,
                                      markup=True).splitlines()

        if window.width != len(job_table[0]):  # Resize window
            window.width = len(job_table[0])

        for index, row in enumerate(job_table):
            if row.startswith("|"):
                row_id = row.split("|")[1].strip()
                if (row_id in job_id_map.keys()
                        and job_id_map[row_id].status in [Status.WAITING,
                                                          Status.RUNNING]):
                    window._widgets[index + 1] = ptg.Button(row, cancel_jobs)
                else:
                    window._widgets[index + 1] = ptg.Label(row)
            else:
                window._widgets[index + 1] = ptg.Label(row)
            window._widgets[index + 1].parent = window

    table = create_jobs_table(jobs, markup=True).splitlines()
    with ptg.WindowManager() as manager:
        def macro_reload(fmt: str) -> str:
            """Updates jobs in the table with an interval."""
            if "last_reload" not in globals():
                global last_reload
                last_reload = time.time()
            diff = time.time() - last_reload
            interval = 10.0
            if diff > interval:  # Check every 10 seconds
                last_reload = 0
                any_running = False
                for job in jobs:
                    if job.status in [Status.RUNNING, Status.WAITING]:
                        any_running = True
                        job.get_latest_job_details()
                if not any_running:
                    manager.stop()
                refresh_data(manager)
                last_reload = time.time()
            n_bars = int(diff / 2)
            return "|" + "█" * n_bars + " " * (4 - n_bars) + "|"

        def flush_popup(self: ptg.WindowManager, key: str) -> None:
            """Pop up for flushing completed jobs."""
            if len(jobs) <= 1:  # Cannot flush the last job
                return
            flushable_jobs = []
            flushable_job_ids = []
            for job in jobs:
                if job.status not in [Status.WAITING, Status.RUNNING]:
                    flushable_jobs.append(job)
                    flushable_job_ids.append(job.run_id)
            if len(flushable_jobs) == 0:  # Nothing to flush
                return

            def flush(self: ptg.Button) -> None:
                """Flush completed jobs."""
                for job in flushable_jobs:
                    jobs.remove(job)
                    del job_id_map[job.run_id]
                flushable_widgets = []
                table_window = manager._windows[-1]
                for iw, widget in enumerate(table_window._widgets):
                    if isinstance(widget, ptg.Label):
                        if ("|" in widget.value
                                and widget.value.split("|")[1].strip().isnumeric()):
                            job_id = widget.value.split("|")[1].strip()
                            if job_id in flushable_job_ids:
                                flushable_widgets.append(widget)
                                # Jobs can be multiple rows (labels) in the table window,
                                # are underlined with a vertical line to seperate jobs
                                offset = 1
                                while (len(table_window._widgets) - (iw + offset)) > 0:
                                    current_widget = table_window._widgets[iw + offset]
                                    if not isinstance(current_widget, ptg.Label):
                                        break  # This method only cleans labels
                                    flushable_widgets.append(current_widget)
                                    if current_widget.value.startswith("+"):
                                        break  # Seperation line, stop
                                    offset += 1
                for widget in flushable_widgets:
                    table_window.remove(widget)
                manager.remove(popup)

            popup = manager.alert(ptg.Label("Flush non-active jobs?"),
                                  ptg.Button("Yes", flush),
                                  ptg.Button("No", lambda *_: manager.remove(popup)))

        ptg.tim.define("!reload", macro_reload)
        window = (
            ptg.Window(
                "[bold]Sparkle Jobs [!reload]%c",
                width=len(table[0]),
                box="EMPTY",
            )
        )
        job_id_map = {job.run_id: job for job in jobs}
        for row in table:
            if "|" not in row or not row.split("|")[1].strip().isnumeric():
                window._add_widget(ptg.Label(row))
            else:
                window._add_widget(ptg.Button(label=row, onclick=cancel_jobs))

        manager.add(window)
        manager.bind(" ", flush_popup, description="Flush finished jobs")

    # If all jobs were finished, print final table.
    if all([j.status not in [Status.WAITING, Status.RUNNING] for j in jobs]):
        table = create_jobs_table(jobs, format="fancy_grid")
        print(table)


def main(argv: list[str]) -> None:
    """Main function of the jobs command."""
    # Log command call
    logging.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    # Filter jobs on relevant status
    path = gv.settings().DEFAULT_log_output
    jobs = [run for run in jobs_help.get_runs_from_file(path)
            if run.status == Status.WAITING or run.status == Status.RUNNING]
    if args.job_ids:  # Filter
        jobs = [job for job in jobs if job.run_id in args.job_ids]
        job_ids = [job.run_id for job in jobs]
        for id in args.job_ids:
            if id not in job_ids:
                print(f"WARNING: Job ID {id} was not found ")

    if len(jobs) == 0:
        if args.job_ids:
            print(f"None of the specified jobs are running: {args.job_ids}")
            sys.exit(-1)
        print("No jobs running.")
        if args.cancel:
            sys.exit(-1)
        sys.exit(0)

    if args.cancel:
        if args.all or args.job_ids:
            killed_jobs = []
            for j in jobs:
                if args.all or j.run_id in args.job_ids:
                    j.kill()
                    killed_jobs.append(j)
            if len(killed_jobs) == 0:
                if args.all:
                    print("No jobs to cancel.")
                    sys.exit(0)
                else:
                    print(f"ERROR: No jobs with ids {args.job_ids} to cancel.")
                    sys.exit(-1)
            print(f"Canceled {len(killed_jobs)} jobs with IDs: "
                  f"{', '.join([j.run_id for j in killed_jobs])}.")
        sys.exit(0)
    else:
        table_gui(jobs)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
