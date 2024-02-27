"""Test public methods of configurator class."""

from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

from pathlib import Path

from Commands.sparkle_help.solver import Solver
from Commands.sparkle_help.configuration_scenario import ConfigurationScenario
from Commands.sparkle_help.configurator import Configurator
from Commands.sparkle_help import sparkle_global_help as sgh


class TestConfigurator():
    """Class bundling all tests regarding Configurator."""

    def test_init(self: TestConfigurator,
                  mocker: MockerFixture,
                  scenario_fixture: MockerFixture,
                  configurator_path: MockerFixture) -> None:
        """Test that Configurator initialization calls create_scenario() correctly."""
        mock_path = mocker.patch.object(Path, "mkdir")

        configurator = Configurator(configurator_path)

        assert configurator.configurator_path == configurator_path

        mock_path.assert_called_once()

    def test_create_sbatch_script(self: TestConfigurator,
                                  mocker: MockerFixture,
                                  scenario_fixture: ConfigurationScenario,
                                  configurator_path: Path) -> None:
        """Test correct sbatch script creation."""
        mocker.patch.object(Path, "mkdir")
        mocker.patch.object(ConfigurationScenario, "create_scenario", return_value=None)
        scenario_fixture.directory = Path("parent_dir", "scenarios",
                                          scenario_fixture.name)
        scenario_fixture.scenario_file_name = f"{scenario_fixture.name}_scenario.txt"

        mock_config_scenario = mocker.patch.object(ConfigurationScenario,
                                                   "create_scenario",
                                                   return_value=False)

        configurator = Configurator(configurator_path)

        reference_file_path = Path("tests", "test_files", "reference_files", "sbatch.sh")
        with reference_file_path.open("r") as file:
            reference_file_content = file.read()

        mocked_file = mocker.patch("pathlib.Path.open", mocker.mock_open())

        configurator.create_sbatch_script(scenario_fixture)

        mocked_file().write.assert_called_with(reference_file_content)
        mock_config_scenario.assert_called_with(parent_directory=configurator_path)


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
    time_budget = sgh.settings.get_config_budget_per_run()
    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    cutoff_length = sgh.settings.get_smac_target_cutoff_length()
    run_objective =\
        sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    use_features = False
    return ConfigurationScenario(solver_fixture, instance_set_train, number_of_runs,
                                 time_budget, cutoff_time, cutoff_length,
                                 run_objective, use_features, sgh.smac_target_algorithm)


@pytest.fixture
def configurator_path() -> Path:
    """Configurator path fixture for tests."""
    return Path("tests/test_files/Configurators/smac-v2.10.03-master-778")
