#!/usr/bin/env python3
"""Command to cancel async jobs."""
import sys
import time
import argparse
import pytermgui as ptg

from runrunner.base import Status

from sparkle.CLI.help import logging
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help import jobs as jobs_help
from sparkle.CLI.help import global_variables as gv


def parser_function() -> argparse.ArgumentParser:
    """Create parser for the cancel command."""
    parser = argparse.ArgumentParser(description="Command to cancel running jobs.")
    parser.add_argument(*ac.JobIDsArgument.names, **ac.JobIDsArgument.kwargs)
    parser.add_argument(*ac.AllJobsArgument.names, **ac.AllJobsArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the cancel command."""
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
                # NOTE: Should we raise an error here instead?
                sys.exit(-1)
        print(f"Canceled {len(killed_jobs)} jobs with IDs: "
              f"{', '.join([j.run_id for j in killed_jobs])}.")
    elif len(jobs) == 0:
        print("No jobs running.")
    else:
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
            window = self._windows[0] if isinstance(self, ptg.WindowManager) else self
            # Fetch latest data
            for job in jobs:
                if job.status in [Status.WAITING, Status.RUNNING]:
                    job.get_latest_job_details()
            data_table = jobs_help.create_jobs_table(jobs, markup=True).splitlines()
            # Rebuild the widgets
            for iw, row in enumerate(data_table):
                if "|" not in row or not row.split("|")[1].strip().isnumeric():  # Label
                    continue
                else:
                    job = job_id_map[row.split("|")[1].strip()]
                    if job.status in [Status.WAITING, Status.RUNNING]:
                        window._widgets[iw + 1] = ptg.Button(label=row,
                                                             onclick=cancel_jobs)
                    elif isinstance(window._widgets[iw + 1], ptg.Button):
                        # Finished job, replace button with label
                        window._widgets[iw + 1] = ptg.Label(row)
                window._widgets[iw + 1].parent = window

        table = jobs_help.create_jobs_table(jobs, markup=True).splitlines()
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

            ptg.tim.define("!reload", macro_reload)
            window = (
                ptg.Window(
                    "[bold]Sparkle Jobs [!reload]%c",
                    width=len(table[0]),
                    box="EMPTY",
                )
                .set_title("Running Sparkle Jobs")
            )
            job_id_map = {job.run_id: job for job in jobs}
            for row in table:
                if "|" not in row or not row.split("|")[1].strip().isnumeric():
                    window._add_widget(ptg.Label(row))
                else:
                    window._add_widget(ptg.Button(label=row, onclick=cancel_jobs))

            manager.add(window)
            manager.bind(" ", action=refresh_data, description="Refresh")

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
