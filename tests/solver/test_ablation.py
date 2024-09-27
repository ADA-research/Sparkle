"""Test ablation scenario class."""
from __future__ import annotations
from unittest import TestCase
from pathlib import Path

from sparkle.solver.ablation import AblationScenario
from sparkle.solver import Solver
from sparkle.instance import InstanceSet


class TestAblationScenario(TestCase):
    """Test ablation scenario class."""

    def setUp(self: TestAblationScenario) -> None:
        """Setup objects for tests."""
        self.solver = Solver(Path("tests/test_files/Solvers/Test-Solver"))
        self.dataset: InstanceSet = InstanceSet(Path("Instances/Train-Instance-Set"))
        self.test_dataset: InstanceSet = InstanceSet(Path("Instances/Test-Instance-Set"))
        self.output_directory: Path = Path("Output/ablation_test")
        self.ablation_executable: Path = None
        self.validation_executable: Path = None
        self.override_dirs: bool = False
        self.scenario = AblationScenario(
            self.solver, self.dataset, self.test_dataset, self.output_directory,
            self.ablation_executable, self.validation_executable, self.override_dirs)

    def test_ablation_scenario_constructor(self: TestAblationScenario) -> None:
        """Test for ablation scenario constructor."""
        assert self.scenario.ablation_exec == self.ablation_executable
        assert self.scenario.ablation_validation_exec == self.validation_executable
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
