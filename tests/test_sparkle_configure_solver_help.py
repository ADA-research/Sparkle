"""Test functionalities related to the sparkle_configure_solver_help module."""

from unittest.mock import patch
from unittest.mock import Mock

from Commands.sparkle_help import sparkle_configure_solver_help as scsh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_settings

global settings
sgh.settings = sparkle_settings.Settings()

test_solver_name = "solver_name"
test_instance_set_name = "instance_set"

@patch("pathlib.Path.is_dir")
def test_check_configuration_exists_true(mock_is_dir: Mock) -> None:
    """Test whether True is returned when the configuration directory exists."""
    mock_is_dir.return_value = True

    result = scsh.check_configuration_exists(test_solver_name, test_instance_set_name)

    assert result is True
