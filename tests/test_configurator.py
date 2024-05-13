"""Test public methods of configurator class."""

from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

from pathlib import Path

from sparkle.solver.solver import Solver
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.configurator.configurator import Configurator
from sparkle.configurator.implementations import SMAC2
from sparkle.platform import settings_help
from sparkle.types.objective import SparkleObjective
import global_variables as gv

global settings
gv.settings = settings_help.Settings()


class TestConfigurator():
    """Class bundling all tests regarding Configurator."""

    def test_init(self: TestConfigurator,
                  mocker: MockerFixture,
                  scenario_fixture: MockerFixture,
                  configurator_path: MockerFixture) -> None:
        """Test that Configurator initialization calls create_scenario() correctly."""
        exec_path = Path("dir/exec.exe")
        configurator = Configurator(
            output_path=Path(),
            validator=None,
            executable_path=exec_path,
            settings_path=None,
            configurator_target=None,
            objectives=[SparkleObjective("RUNTIME:PAR10")])

        assert configurator.executable_path == exec_path


@pytest.fixture
def solver_fixture() -> Solver:
    """Solver fixture for tests."""
    solver_path = Path("tests", "test_files", "Solvers", "Test-Solver")
    return Solver(solver_path)


@pytest.fixture
def scenario_fixture(solver_fixture: MockerFixture) -> ConfigurationScenario:
    """Scenario fixture for tests."""
    instance_set_train = Path("Instances", "Test-Instance-Set")
    number_of_runs = 2
    time_budget = gv.settings.get_config_budget_per_run()
    cutoff_time = gv.settings.get_general_target_cutoff_time()
    cutoff_length = gv.settings.get_smac_target_cutoff_length()
    sparkle_objective =\
        gv.settings.get_general_sparkle_objectives()[0]
    use_features = False
    return ConfigurationScenario(solver_fixture, instance_set_train, number_of_runs,
                                 time_budget, cutoff_time, cutoff_length,
                                 sparkle_objective, use_features,
                                 SMAC2.target_algorithm)


@pytest.fixture
def configurator_path() -> Path:
    """Configurator path fixture for tests."""
    return Path("tests/test_files/Configurators/smac-v2.10.03-master-778")
