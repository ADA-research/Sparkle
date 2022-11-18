#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Basic helper functions."""

import os
import time
import random
import sys


def get_time_pid_random_string() -> str:
    """Return a combination of time, PID, and random str."""
    my_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    my_pid = os.getpid()
    my_pid_str = str(my_pid)
    my_random = random.randint(1, sys.maxsize)
    my_random_str = str(my_random)
    my_time_pid_random_str = my_time_str + '_' + my_pid_str + '_' + my_random_str

    return my_time_pid_random_str
