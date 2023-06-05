"""Test functionalities related to the sparkle_configure_solver_help module."""

from unittest.mock import patch
from unittest.mock import MagicMock

from Commands.sparkle_help import sparkle_configure_solver_help as scsh

test_solver_name = "solver_name"
test_instance_set_name = "instance_set"


@patch("Commands.sparkle_help.sparkle_configure_solver_help.Path")
def test_check_configuration_exists_true(path_mock: MagicMock) -> None:
    """Test whether True is returned when the configuration directory exists."""
    mock_path = MagicMock()
    path_mock.return_value = mock_path

    # File exists
    mock_path.is_dir.return_value = True

    result = scsh.check_configuration_exists(test_solver_name, test_instance_set_name)

    assert result is True
    mock_path.is_dir.assert_called_once()
