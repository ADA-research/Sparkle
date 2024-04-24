"""Test functionalities related to the sparkle_configure_solver_help module."""
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock

from CLI.support import configure_solver_help as scsh
from CLI.sparkle_help import sparkle_global_help as sgh
from sparkle.platform import settings_help
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.solver.solver import Solver

global settings
sgh.settings = sparkle_settings.Settings()


@patch("pathlib.Path.is_dir")
def test_check_configuration_exists_true(mock_is_dir: Mock) -> None:
    """Test whether True is returned when the configuration directory exists."""
    test_solver_name = "solver_name"
    test_instance_set_name = "instance_set"
    conf = sgh.settings.get_general_sparkle_configurator()
    conf.scenario = ConfigurationScenario(Solver(Path(test_solver_name)),
                                          Path(test_instance_set_name))
    conf.scenario._set_paths(conf.configurator_path)
    mock_is_dir.return_value = True

    result = scsh.check_configuration_exists()

    assert result is True
