"""Test methods for PyRunSolver class."""

import sys
from pathlib import Path
import pytest

from sparkle.tools.runsolver.py_runsolver import run_with_monitoring, PyRunSolver


def parse_value_file(path: Path) -> dict:
    """Helper to parse the key=value output file."""
    stats = {}
    with Path.open(path, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            key, value = line.strip().split("=", 1)
            stats[key] = value
    return stats


def test_successful_run(tmp_path: Path) -> None:
    """Tests a simple, successful command execution."""
    watcher_file, value_file, output_file = (
        tmp_path / "w.log",
        tmp_path / "v.val",
        tmp_path / "o.log",
    )
    command = ["/bin/sh", "-c", "echo 'Test success'; sleep 0.2"]

    run_with_monitoring(command, watcher_file, value_file, output_file)
    assert b"Test success" in output_file.read_bytes()
    stats = parse_value_file(value_file)
    assert stats["TIMEOUT"] == "false"
    assert stats["MEMOUT"] == "false"


def test_wall_clock_timeout(tmp_path: Path) -> None:
    """Tests if the wall-clock limit terminates a process."""
    watcher_file, value_file, output_file = (
        tmp_path / "w.log",
        tmp_path / "v.val",
        tmp_path / "o.log",
    )
    command = ["sleep", "5"]

    run_with_monitoring(
        command, watcher_file, value_file, output_file, wall_clock_limit=1
    )

    stats = parse_value_file(value_file)
    assert stats["TIMEOUT"] == "true"
    assert 1.0 <= float(stats["WCTIME"]) < 1.3


@pytest.mark.integration
def test_cpu_limit_timeout(tmp_path: Path) -> None:
    """Tests if the CPU time limit terminates a CPU-intensive process."""
    watcher_file, value_file, output_file = (
        tmp_path / "w.log",
        tmp_path / "v.val",
        tmp_path / "o.log",
    )
    command = [sys.executable, __file__]

    run_with_monitoring(command, watcher_file, value_file, output_file, cpu_limit=3)

    stats = parse_value_file(value_file)
    assert stats["TIMEOUT"] == "true"
    assert float(stats["CPUTIME"]) >= 3.0


@pytest.mark.integration
def test_memory_limit_exceeded(tmp_path: Path) -> None:
    """Tests if the virtual memory limit terminates a memory-hungry process."""
    watcher_file, value_file, output_file = (
        tmp_path / "w.log",
        tmp_path / "v.val",
        tmp_path / "o.log",
    )
    mem_script = "a = ' ' * (200 * 1024 * 1024); import time; time.sleep(5)"
    command = [sys.executable, "-c", mem_script]

    run_with_monitoring(
        command, watcher_file, value_file, output_file, vm_limit=100 * 1024
    )

    stats = parse_value_file(value_file)
    assert stats["MEMOUT"] == "true"
    assert float(stats["MAXVM"]) > 90 * 1024


def test_wrap_command_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tests if the wrapper command is generated correctly."""
    # Mock the unique string generator for a predictable output
    monkeypatch.setattr(
        "sparkle.tools.runsolver.py_runsolver.get_time_pid_random_string",
        lambda: "test_stamp",
    )

    command = ["my_solver", "--instance", "path/to/instance"]
    wrapped_cmd = PyRunSolver.wrap_command(command, 3600, tmp_path, "my_log")

    assert wrapped_cmd[0] == sys.executable
    assert Path(wrapped_cmd[1]).name == "py_runsolver.py"
    assert (
        wrapped_cmd[2:]
        == [
            "--timestamp",
            "-C",
            "3600",
            "-w",
            str(tmp_path / "my_log_test_stamp.log"),
            "-v",
            str(tmp_path / "my_log_test_stamp.val"),
            "-o",
            str(tmp_path / "my_log_test_stamp.rawres"),
        ]
        + command
    )


if __name__ == "__main__":

    def is_prime(n: int) -> bool:
        """Checks if a number is prime."""
        if n <= 1:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def find_primes_in_range(limit: int) -> list[int]:
        """Finds all prime numbers up to a given limit."""
        primes = []
        for number in range(2, limit + 1):
            if is_prime(number):
                primes.append(number)
        return primes

    upper_limit = 150000000
    print(f"Finding all prime numbers up to {upper_limit}...")
    prime_numbers = find_primes_in_range(upper_limit)
    print(f"Found {len(prime_numbers)} prime numbers.")
