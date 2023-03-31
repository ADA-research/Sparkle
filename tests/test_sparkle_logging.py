from pathlib import Path, PurePath

import sparkle_help.sparkle_logging as sl
import sparkle_help.sparkle_global_help as sgh


def test__update_caller():
    argv = ["test.py"]
    sl._update_caller(argv)
    assert sl.caller == "test"


def test__update_caller_file_path():
    timestamp = "18-08-2023_12:34:56"
    sl._update_caller_file_path(timestamp)

    assert isinstance(sl.caller_out_dir, Path)
    assert isinstance(sl.caller_log_path, PurePath)
    assert isinstance(sl.caller_log_dir, Path)

    assert str(sl.caller_out_dir) == f"{timestamp}_{sl.caller}"

    assert Path(sl.caller_log_path).is_file()


def test_add_output():
    argv = ["test.py"]
    sl.log_command(argv)
    sl.add_output("test.txt", "functionality test.")
    with open(str(sl.caller_log_path), "r") as output_file:
        for line in output_file:
            pass
        last_line = line
    assert "test.txt" in last_line
    assert "functionality test." in last_line


def test_log_command():
    argv = ["test.py"]
    sl.log_command(argv)
    log_path = sgh.sparkle_global_log_path
    with open(str(log_path), "r") as log_file:
        for line in log_file:
            pass
        last_line = line
    print(f"\n{last_line}\n")
    assert "test.py" in last_line
