#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to communicate run statuses of various commands."""

from Commands.sparkle_help import sparkle_job_help as sjh


def print_running_jobs():
    """Print all the running jobs."""
    sjh.cleanup_active_jobs()
    jobs = sjh.read_active_jobs()
    for job in jobs:
        print(job)
