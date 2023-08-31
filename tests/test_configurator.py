"""Test public methods of configurator class."""

import pytest

from pathlib import Path

from Commands.sparkle_help.solver import Solver
from Commands.sparkle_help.configuration_scenario import ConfigurationScenario
from Commands.sparkle_help.configurator import Configurator


class TestConfigurator():
    """Class bundling all tests regarding Configurator."""

    def test_init(self, mocker, scenario_fixture, configurator_path) -> None:
        """Test that Configurator initialization calls create_scenario() correctly."""
        mock_path = mocker.patch.object(Path, "mkdir")

        mock_configurator = mocker.patch.object(ConfigurationScenario, "create_scenario",
                                                return_value=False)

        configurator = Configurator(configurator_path, scenario_fixture)

        assert configurator.configurator_path == configurator_path
        assert configurator.scenario == scenario_fixture

        mock_path.assert_called_once()
        mock_configurator.assert_called_with(parent_directory=configurator_path)

    def test_create_sbatch_script(self, mocker,
                                  scenario_fixture: ConfigurationScenario,
                                  configurator_path: Path) -> None:
        """Test correct sbatch script creation."""
        mocker.patch.object(Path, "mkdir")
        mocker.patch.object(ConfigurationScenario, "create_scenario", return_value=None)
        scenario_fixture.directory = Path("parent_dir", "scenarios",
                                          scenario_fixture.name)
        scenario_fixture.scenario_file_name = f"{scenario_fixture.name}_scenario.txt"

        configurator = Configurator(configurator_path, scenario_fixture)

        reference_file_path = Path("tests", "test_files", "reference_files", "sbatch.sh")
        with reference_file_path.open("r") as file:
            reference_file_content = file.read()

        mocked_file = mocker.patch("pathlib.Path.open", mocker.mock_open())

        configurator.create_sbatch_script()

        mocked_file().write.assert_called_with(reference_file_content)


@pytest.fixture
def solver_fixture() -> Solver:
    """Solver fixture for tests."""
    solver_path = Path("tests", "test_files", "Solvers", "Test-Solver")
    return Solver(solver_path)


@pytest.fixture
def scenario_fixture(solver_fixture) -> ConfigurationScenario:
    """Scenario fixture for tests."""
    instance_set_train = Path("Instances", "Test-Instance-Set")
    number_of_runs = 2
    use_features = False
    return ConfigurationScenario(solver_fixture, instance_set_train, number_of_runs,
                                 use_features)


@pytest.fixture
def configurator_path() -> Path:
    """Configurator path fixture for tests."""
    return Path("tests/test_files/Configurators/smac-v2.10.03-master-778")
