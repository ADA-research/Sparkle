#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to communicate run statuses of various commands."""

from Commands.sparkle_help import sparkle_job_help as sjh


def get_jobs_for_command(jobs: list[dict[str, str, str]], command: str) \
        -> list[dict[str, str, str]]:
    """Filter jobs by a command.

    Args:
      jobs: List of jobs
      command: The command to filter for

    Returns:
      Jobs that belong to the given command.
    """
    return [x for x in jobs if x["command"] == command]


def print_running_jobs():
    """Print all the running jobs."""
    sjh.cleanup_active_jobs()
    jobs = sjh.read_active_jobs()
    commands = list(set([x["command"] for x in jobs]))
    for command in commands:
        command_jobs = get_jobs_for_command(jobs, command)
        command_jobs_ids = " ".join([x["job_id"] for x in command_jobs])

        if len(command_jobs) > 1:
            print(f"The command {command} is running "
                  f"with job IDs {command_jobs_ids}")
        else:
            print(f"The command {command} is running "
                  f"with job ID {command_jobs_ids}")
