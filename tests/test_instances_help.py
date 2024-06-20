"""Test functionalities related to the sparkle_instances_help module."""

from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import mock_open
from pathlib import Path

from sparkle.instance import instances_help as sih

test_instance_set_name = "instance_set"
test_file = Path("file.txt")


@patch("sparkle.instance.instances_help.Path")
def test_check_existence_of_reference_instance_list(path_mock: MagicMock) -> None:
    """Test whether return value is correct when the file does (not) exist."""
    mock_path = MagicMock()
    path_mock.return_value = mock_path

    # File exists
    mock_path.is_file.return_value = True

    result = sih.check_existence_of_reference_instance_list(test_instance_set_name)

    assert result is True
    mock_path.is_file.assert_called_once()

    # File does not exist
    mock_path.reset_mock()
    mock_path.is_file.return_value = False

    result = sih.check_existence_of_reference_instance_list(test_instance_set_name)

    assert result is False
    mock_path.is_file.assert_called_once()


@patch("sparkle.instance.instances_help.Path.open")
def test_count_instances_in_reference_list(path_open_mock: mock_open) -> None:
    """Test whether the number of instances is counted correctly."""
    # Empty lines should not be counted
    opener = mock_open(read_data="instance_a.txt\n \t\ninstance_b.txt")
    path_open_mock.return_value = opener.return_value

    result = sih.count_instances_in_reference_list(test_instance_set_name)

    assert result == 2
    path_open_mock.assert_called_once_with("r")
