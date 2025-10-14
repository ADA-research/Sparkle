"""Python Runsolver class."""

import argparse
import os
import pty
import select
import shlex
import subprocess
import sys
import time
from typing import Optional
from pathlib import Path
import psutil

from sparkle.tools.general import get_time_pid_random_string
from sparkle.tools.runsolver.runsolver import RunSolver
from sparkle.__about__ import __version__ as sparkle_version


class PyRunSolver(RunSolver):
    """Class representation of Python based RunSolver."""

    @staticmethod
    def wrap_command(
        command: list[str],
        cutoff_time: int,
        log_directory: Path,
        log_name_base: str = None,
        raw_results_file: bool = True,
    ) -> list[str]:
        """Wrap a command with the RunSolver call and arguments.

        Args:
            command: The command to wrap.
            cutoff_time: The cutoff CPU time for the solver.
            log_directory: The directory where to write the solver output.
            log_name_base: A user defined name to easily identify the logs.
                Defaults to "runsolver".
            raw_results_file: Whether to use the raw results file.

        Returns:
            List of commands and arguments to execute the solver.
        """
        log_name_base = "runsolver" if log_name_base is None else log_name_base
        unique_stamp = get_time_pid_random_string()
        raw_result_path = log_directory / Path(f"{log_name_base}_{unique_stamp}.rawres")
        watcher_data_path = raw_result_path.with_suffix(".log")
        var_values_path = raw_result_path.with_suffix(".val")
        runner_exec = Path(__file__)

        return (
            [
                sys.executable,
                str(runner_exec.absolute()),
                "--timestamp",
                "-C",
                str(cutoff_time),
                "-w",
                str(watcher_data_path),
                "-v",
                str(var_values_path),
            ]
            + (["-o", str(raw_result_path)] if raw_results_file else [])
            + command
        )


def run_with_monitoring(
    command: list[str],
    watcher_file: Path,
    value_file: Path,
    output_file: Path,
    timestamp: bool = True,
    cpu_limit: Optional[int] = None,
    wall_clock_limit: Optional[int] = None,
    vm_limit: Optional[int] = None,
) -> None:
    """Runs a command with CPU, wall-clock, and memory monitoring.

    Args:
        command: The command to execute as a list of strings.
        watcher_file: File to log the command line.
        value_file: File to write final resource usage metrics.
        output_file: Optional file to redirect command's output.
        timestamp: Whether to add timestamps to each raw output line as CPU TIME / WC Time.
        cpu_limit: CPU time limit in seconds.
        wall_clock_limit: Wall-clock time limit in seconds.
        vm_limit: Virtual memory limit in KiB.
    """
    start_time = time.time()
    cpu_time = 0.0
    user_time = 0.0
    system_time = 0.0
    max_memory_kib = 0

    with watcher_file.open("w") as f:
        f.write(
            f"PyRunSolver from Sparkle v{sparkle_version}, a Python mirror of RunSolver. Copyright (C) 2025, ADA Research Group\n"
        )
        f.write(f"command line: {shlex.join(sys.argv)}")

    def process_raw_output(fd: int, target_file: Path = None) -> int | None:
        """Reads and writes 'raw' command output to a file."""
        if fd is None:  # Closed file stream, nothing to do
            return None
        while select.select([fd], [], [], 0)[
            0
        ]:  # Check if FD is available for read without blocking/waiting
            try:
                data = os.read(
                    fd,
                    8192,  # Preferably this would be larger, but the stream never gives more than 4095 chars per read. Don't know why.
                ).decode()
                if data:
                    if timestamp:
                        ends_with_newline = data.endswith("\n")
                        stamp = f"{user_time:.2f}/{time.time() - start_time:.2f}"
                        data = "\n".join(
                            [f"{stamp}\t{line}" for line in data.splitlines()]
                        )  # Add stamp at the beginning of each line
                        data += (
                            "\n" if ends_with_newline else ""
                        )  # Splitlines removes last \n
                    if target_file:
                        with target_file.open(
                            "a"
                        ) as f:  # Reopen and close per line to stream output
                            f.write(data)
                    else:  # No output log, print to 'terminal' (Or slurm log etc.)
                        print(data)
                else:
                    os.close(fd)  # No data on stream
                    return None  # Remove FD
            except OSError:  # Streamno longer readable
                return None  # Remove FD
        return fd

    if output_file:  # Create raw output log
        output_file.open("w+").close()

    try:
        master_fd, slave_fd = (
            pty.openpty()
        )  # Open new pseudo-terminal pair for Master (us) and Slave (subprocess)
        process = subprocess.Popen(
            command, stdout=slave_fd, stderr=slave_fd, close_fds=True
        )
        os.close(slave_fd)  # Is this necessary? Are the fds not already closed above?
        ps_process = psutil.Process(process.pid)

        # Main monitoring loop
        while process.poll() is None:
            # Check if process has exceed wall clock limit
            if wall_clock_limit and (time.time() - start_time) > wall_clock_limit:
                process.kill()
                break

            # Read process output and write to out_log
            master_fd = process_raw_output(master_fd, output_file)

            try:  # Try to update statistics
                children = ps_process.children(recursive=True)

                # Sum CPU times and memory for the entire process tree
                current_user_time = (
                    ps_process.cpu_times().user + ps_process.cpu_times().children_user
                )
                current_system_time = (
                    ps_process.cpu_times().system
                    + ps_process.cpu_times().children_system
                )
                current_vms = ps_process.memory_info().vms

                for child in children:
                    try:
                        current_user_time += child.cpu_times().user
                        current_system_time += child.cpu_times().system
                        current_vms += child.memory_info().vms
                    except psutil.NoSuchProcess:
                        continue

                user_time = current_user_time
                system_time = current_system_time
                cpu_time = user_time + system_time
                max_memory_kib = max(max_memory_kib, current_vms / 1024)
                if cpu_limit and cpu_time > cpu_limit:
                    process.kill()
                    break
                if vm_limit and max_memory_kib > vm_limit:
                    process.kill()
                    break

            except psutil.NoSuchProcess:
                break
        process_raw_output(master_fd, output_file)  # Final read from stream
    except (
        KeyboardInterrupt
    ):  # Ensure that we can catch CTRL-C and still wrap up properly
        if process and process.poll() is None:
            process.kill()
        raise
    finally:
        if process:
            process.wait()
        if master_fd:
            os.close(master_fd)  # Close child's output stream

    wall_time = time.time() - start_time
    timeout = (cpu_limit is not None and cpu_time > cpu_limit) or (
        wall_clock_limit is not None and wall_time > wall_clock_limit
    )
    memout = vm_limit is not None and max_memory_kib > vm_limit

    stats = {
        "WCTIME": (f"{wall_time}", "wall clock time in seconds"),
        "CPUTIME": (f"{cpu_time}", "CPU time in seconds (USERTIME+SYSTEMTIME)"),
        "USERTIME": (f"{user_time}", "CPU time spent in user mode in seconds"),
        "SYSTEMTIME": (f"{system_time}", "CPU time spent in system mode in seconds"),
        "CPUUSAGE": (
            f"{((cpu_time / wall_time) * 100 if wall_time > 0 else 0):.2f}",
            "CPUTIME/WCTIME in percent",
        ),
        "MAXVM": (f"{max_memory_kib:.0f}", "maximum virtual memory used in KiB"),
        "TIMEOUT": (str(timeout).lower(), "did the solver exceed a time limit?"),
        "MEMOUT": (str(memout).lower(), "did the solver exceed the memory limit?"),
    }

    with Path.open(value_file, "w") as f:
        for key, (value, comment) in stats.items():
            f.write(f"# {key}: {comment}\n")
            f.write(f"{key}={value}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run and monitor a command.")
    parser.add_argument(
        "--timestamp",
        action="store_true",
        help="Include a timestamp in the output logs.",
    )
    parser.add_argument("-C", "--cpu-limit", type=int, help="CPU time limit in seconds.")
    parser.add_argument(
        "-W", "--wall-clock-limit", type=int, help="Wall clock time limit in seconds."
    )
    parser.add_argument(
        "-V",
        "--vm-limit",
        type=int,
        help="Virtual memory limit in KiB.",
    )
    parser.add_argument(
        "-w",
        "--watcher-data",
        type=Path,
        required=True,
        help="File to write watcher info to.",
    )
    parser.add_argument(
        "-v",
        "--var",
        type=Path,
        required=True,
        help="File to write final resource values to.",
    )
    parser.add_argument(
        "-o",
        "--solver-data",
        required=False,
        type=Path,
        help="File to redirect command stdout and stderr to.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to run.")

    args = parser.parse_args()

    if not args.command:
        parser.error("You must specify a command to run.")

    run_with_monitoring(
        command=args.command,
        watcher_file=args.watcher_data,
        value_file=args.var,
        output_file=args.solver_data,
        timestamp=args.timestamp,
        cpu_limit=args.cpu_limit,
        wall_clock_limit=args.wall_clock_limit,
        vm_limit=args.vm_limit,
    )
