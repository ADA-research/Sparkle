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
        cutoff_time = 2
        cutoff_length = "3"
        concurrent_clis = 4
        best_configuration = {"init_solution": "2", "perform_first_div": "1", "asd": 5}
        ablation_racing = False

        return_val = self.scenario.create_configuration_file(cutoff_time,
                                                             cutoff_length,
                                                             concurrent_clis,
                                                             best_configuration,
                                                             ablation_racing)

        validation_config_file = self.scenario.validation_dir / "ablation_config.txt"
        self.assertTrue(validation_config_file.exists(),
                        "Validation config file does not exist.")

        config_dict = {}
        with validation_config_file.open() as f:
            for line in f:
                if "=" in line:
                    key, value = line.split("=", 1)
                    config_dict[key.strip()] = value.strip()

        self.assertEqual(config_dict.get("cutoffTime"),
                         f"{cutoff_time}",
                         "cutoffTime does not match")

        self.assertEqual(config_dict.get("cutoff_length"),
                         f"{cutoff_length}",
                         "cutoff_length does not match")

        self.assertEqual(config_dict.get("cli-cores"),
                         f"{concurrent_clis}",
                         "cli-cores does not match")

        self.assertEqual(config_dict.get("useRacing"),
                         f"{ablation_racing}",
                         "useRacing does not match")

        target_config = config_dict.get("targetConfiguration", "")
        self.assertIn("-init_solution 2", target_config,
                      "Expected 'init_solution' setting not found.")

        self.assertIn("-perform_first_div 1", target_config,
                      "Expected 'perform_first_div' setting not found.")

        self.assertNotIn("asd", target_config,
                         "Extraneous key 'asd' should not be"
                         " present in targetConfiguration.")
        assert return_val is None

    def test_create_instance_file_train_set(self: TestAblationScenario) -> None:
        """Test for method create_instance_file."""
        test = False
        main_instance_file = \
            self.scenario.scenario_dir / "instances_train.txt"
        validation_instance_file = \
            self.scenario.validation_dir / "instances_train.txt"

        return_val = self.scenario.create_instance_file(test)

        self.assertTrue(main_instance_file.exists(),
                        "Main train instance file does not exist.")

        self.assertTrue(validation_instance_file.exists(),
                        "Validation train instance file does not exist.")

        main_train_content = main_instance_file.read_text().splitlines()
        validation_content = validation_instance_file.read_text().splitlines()

        self.assertEqual(main_train_content, validation_content,
                         "The instance file and its validation copy"
                         "do not have the same content.")
        assert return_val is None

    def test_create_instance_file_test_set(self: TestAblationScenario) -> None:
        """Test for method create_instance_file."""
        test = True
        return_val = self.scenario.create_instance_file(test)

        main_instance_file = self.scenario.scenario_dir / "instances_test.txt"

        validation_instance_file = self.scenario.validation_dir / "instances_train.txt"

        self.assertTrue(main_instance_file.exists(),
                        "Main test instance file should not exist.")

        self.assertTrue(validation_instance_file.exists(),
                        "Validation test instance file should not exist.")

        main_content = main_instance_file.read_text().splitlines()
        validation_content = validation_instance_file.read_text().splitlines()

        self.assertEqual(main_content, validation_content,
                         "The instance file and its validation copy"
                         "do not have the same content.")
        assert return_val is None

    def test_check_for_ablation_file(self: TestAblationScenario) -> None:
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
