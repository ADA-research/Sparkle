"""Test functionalities related to the sparkle_instances_help module."""

from unittest.mock import patch
from unittest.mock import MagicMock

from Commands.sparkle_help import sparkle_instances_help as sih

test_instance_set_name = "instance_set"


@patch("Commands.sparkle_help.sparkle_instances_help.Path")
def test_check_existence_of_reference_instance_list(path_mock: MagicMock) -> None:
    mock_path = MagicMock()
    path_mock.return_value = mock_path

    mock_path.is_file.return_value = True
    result = sih.check_existence_of_reference_instance_list(test_instance_set_name)
    assert result is True

    mock_path.is_file.return_value = False
    result = sih.check_existence_of_reference_instance_list(test_instance_set_name)
    assert result is False
