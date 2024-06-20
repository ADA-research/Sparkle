"""General tools for Sparkle."""
import time
import random
import os


def get_time_pid_random_string() -> str:
    """Return a combination of time, Process ID, and random int as string.

    Returns:
      A random string composed of time, PID and a random positive integer value.
    """
    time_stamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    return f"{time_stamp}_{os.getpid()}_{int(random.getrandbits(32))}"
