"""Test functionalities related to the sparkle logging module."""

from pathlib import Path, PurePath

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import global_variables as gv


def test__update_caller() -> None:
    """Test caller is correctly updated when _update_caller is called."""
    argv = ["test.py"]
    sl._update_caller(argv)
    assert sl.caller == "test"


def test__update_caller_file_path() -> None:
    """Test _update_caller_file_path uses the right file name and creates it."""
    timestamp = "18-08-2023_12:34:56"
    sl._update_caller_file_path(timestamp)

    assert isinstance(sl.caller_out_dir, Path)
    assert isinstance(sl.caller_log_path, PurePath)
    assert isinstance(sl.caller_log_dir, Path)

    assert str(sl.caller_out_dir) == f"{timestamp}_{sl.caller}"

    assert Path(sl.caller_log_path).is_file()


def test_add_output() -> None:
    """Test add_output correctly extends the log file with given output."""
    argv = ["test.py"]
    sl.log_command(argv)
    sl.add_output("test.txt", "functionality test.")
    with Path(str(sl.caller_log_path)).open(mode="r") as output_file:
        for line in output_file:
            continue
        last_line = line
    assert "test.txt" in last_line
    assert "functionality test." in last_line


def test_log_command() -> None:
    """Test log_command correctly logs the call to a command."""
    argv = ["test.py"]
    sl.log_command(argv)
    log_path = gv.settings().DEFAULT_output / "sparkle.log"
    with Path(str(log_path)).open(mode="r") as log_file:
        for line in log_file:
            continue
        last_line = line
    assert "test.py" in last_line
