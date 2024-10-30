#!/usr/bin/env python3
"""Command to cancel async jobs."""
import sys
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
        print("No jobs available to cancel.")
    else:
        jobs = sorted(jobs, key=lambda j: j.run_id)
        ptg.Button.chars = {"delimiter": ["", ""]}  # Disable padding around buttons

        def cancel_jobs(self: ptg.Button) -> None:
            """Cancel jobs based on a button click."""
            job_id = self.label.split("|")[1].strip()
            for job in jobs:
                if job.run_id == job_id:
                    job.kill()
                    # Replace button with label
                    for iw, widget in enumerate(self.parent._widgets):
                        if isinstance(widget, ptg.Button) and \
                                widget.label == self.label:
                            self.parent._widgets[iw] = ptg.Label(self.label)
                    break
            refresh_data(self.parent)

        def refresh_data(self: ptg.Window) -> None:
            """Refresh the table."""
            data_table = jobs_help.create_jobs_table(jobs, markup=True).splitlines()
            for iw, widget in enumerate(self._widgets):
                self._widgets[iw] = type(widget)(data_table[iw], onclick=cancel_jobs)
                self._widgets[iw].parent = self

        table = jobs_help.create_jobs_table(jobs, markup=True).splitlines()
        with ptg.WindowManager() as manager:
            window = (
                ptg.Window(
                    width=len(table[0]),
                    box="EMPTY",
                )
                .set_title("Running Sparkle Jobs")
            )
            for row in table:
                if "|" not in row or not row.split("|")[1].strip().isnumeric():
                    window._add_widget(ptg.Label(row))
                else:
                    window._add_widget(ptg.Button(label=row, onclick=cancel_jobs))

            manager.add(window)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
