"""Test ablation scenario class."""
from __future__ import annotations
from unittest import TestCase
from pathlib import Path

from sparkle.configurator.implementations import SMAC2Scenario
from sparkle.configurator.ablation import AblationScenario
from sparkle.solver import Solver
from sparkle.types.objective import PAR
from sparkle.instance import Instance_Set


class TestAblationScenario(TestCase):
    """Test ablation scenario class."""

    def setUp(self: TestAblationScenario) -> None:
        """Setup objects for tests."""
        self.solver = Solver(Path("tests/test_files/Solvers/Test-Solver"))
        self.dataset = Instance_Set(Path(
            "tests/test_files/Instances/Test-Instance-Set"))
        self.objective = PAR(10)
        self.test_dataset = Instance_Set(Path(
            "tests/test_files/Instances/Test-Instance-Set"))
        self.output_directory: Path = Path("Output/ablation_test")
        self.ablation_executable: Path = None
        self.validation_executable: Path = None
        self.override_dirs: bool = False
        self.configuration_scenario = SMAC2Scenario(
            self.solver,
            self.dataset,
            [self.objective],
            Path())
        self.scenario = AblationScenario(
            self.configuration_scenario, self.test_dataset, self.output_directory,
            self.override_dirs)

    def test_ablation_scenario_constructor(self: TestAblationScenario) -> None:
        """Test for ablation scenario constructor."""
        assert self.scenario.solver == self.solver
        assert self.scenario.train_set == self.dataset
        assert self.scenario.test_set == self.test_dataset
        assert self.scenario.output_dir == self.output_directory
        assert self.scenario.scenario_name ==\
            f"{self.solver.name}_{self.dataset.name}_{self.test_dataset.name}"
        assert self.scenario.scenario_dir ==\
            self.output_directory / self.scenario.scenario_name
        assert self.scenario.validation_dir == self.scenario.scenario_dir / "validation"

    def test_create_configuration_file(self: TestAblationScenario) -> None:
        """Test for method create_configuration_file."""
        # TODO: Write test, check that written contents match with expected value
        pass

    def test_create_instance_file(self: TestAblationScenario) -> None:
        """Test for method create_instance_file."""
        # TODO: Write test for with training set
        # TODO: Write test for with test set
        pass

    def test_check_for_ablation(self: TestAblationScenario) -> None:
        """Test for method check_for_ablation."""
        # TODO: Write test for when correct file exists
        # TODO: Write test for when file does not exist
        # TODO: Write test for when file is corrupted
        pass

    def test_read_ablation_table(self: TestAblationScenario) -> None:
        """Test for reading an ablation table from file."""
        # TODO: Write test for correct file

        # TODO: Write test for not existant file

        # TODO: Write test for partially corrupted file
        pass

    def test_submit_ablation(self: TestAblationScenario) -> None:
        """Test for method submit ablation."""
        # NOTE: RunRunner calls must be mocked to avoid slurm job submission
        # TODO: Write test
        pass
