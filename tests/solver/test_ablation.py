"""Test ablation scenario class."""

from __future__ import annotations
from pathlib import Path
import pytest
from unittest.mock import patch, Mock

from sparkle.configurator.implementations import SMAC2Scenario
from sparkle.configurator import AblationScenario
from sparkle.solver import Solver
from sparkle.types.objective import PAR
from sparkle.instance import Instance_Set


solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
dataset = Instance_Set(Path("tests/test_files/Instances/Test-Instance-Set").absolute())
objective = PAR(10)
test_dataset = Instance_Set(
    Path("tests/test_files/Instances/Test-Instance-Set").absolute()
)
ablation_executable: Path = None
validation_executable: Path = None
override_dirs: bool = False
cutoff_time = 2
configuration_scenario = SMAC2Scenario(
    solver, dataset, [objective], 1, Path(), solver_cutoff_time=cutoff_time
)
configuration_scenario._timestamp = "test_date"
cutoff_length = "3"
concurrent_clis = 4
best_configuration = {
    "init_solution": "2",
    "perform_first_div": "1",
    "asd": 5,
    "test_bool": True,
}
ablation_racing = False
scenario = AblationScenario(
    configuration_scenario,
    test_dataset,
    cutoff_length,
    concurrent_clis,
    best_configuration,
    ablation_racing,
)


def test_ablation_scenario_constructor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test for ablation scenario constructor."""
    assert scenario.solver == solver
    assert scenario.train_set == dataset
    assert scenario.test_set == test_dataset
    t = scenario.config_scenario.timestamp
    assert (
        scenario.scenario_name
        == f"ablation_{solver.name}_{dataset.name}_{t}_{test_dataset.name}"
    )
    assert (
        scenario.scenario_dir
        == configuration_scenario.directory / scenario.scenario_name
    )
    assert scenario.validation_dir == scenario.scenario_dir / "validation"


def test_create_configuration_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test for method create_configuration_file."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    scenario.scenario_dir.mkdir(parents=True, exist_ok=True)
    scenario.validation_dir.mkdir(parents=True, exist_ok=True)
    validation_config_file = scenario.validation_dir / "ablation_config.txt"
    returned_val = scenario.create_configuration_file()

    assert validation_config_file.exists() is True, (
        "Validation config file does not exist."
    )

    assert returned_val == validation_config_file

    config_dict = {
        key.strip(): value.strip()
        for line in validation_config_file.open().readlines()
        for key, value in [line.split("=", 1)]
    }
    assert config_dict.get("cutoffTime") == f"{cutoff_time}", "cutoffTime does not match"

    assert config_dict.get("cutoff_length") == f"{cutoff_length}", (
        "cutoff_length does not match"
    )

    assert config_dict.get("cli-cores") == f"{concurrent_clis}", (
        "cli-cores does not match"
    )

    assert config_dict.get("useRacing") == f"{ablation_racing}", (
        "useRacing does not match"
    )

    target_config = config_dict.get("targetConfiguration", "")
    assert "-init_solution 2" in target_config, (
        "Expected 'init_solution' setting not found."
    )

    assert "-perform_first_div 1" in target_config, (
        "Expected 'perform_first_div' setting not found."
    )

    assert "asd" not in target_config, (
        "Extraneous key 'asd' should not be present in targetConfiguration."
    )

    assert "test_bool" not in target_config, (
        "Extraneous key 'test_bool' should not be present in targetConfiguration."
    )


@pytest.mark.parametrize(
    "test, file_name", [(False, "instances_train.txt"), (True, "instances_test.txt")]
)
def test_create_instance_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test: bool, file_name: str
) -> None:
    """Test for method create_instance_file."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    scenario.scenario_dir.mkdir(parents=True, exist_ok=True)
    scenario.validation_dir.mkdir(parents=True, exist_ok=True)
    main_instance_file = scenario.scenario_dir / file_name
    validation_instance_file = scenario.validation_dir / file_name

    assert scenario.create_instance_file(test) == main_instance_file

    assert main_instance_file.exists() is True, f"{main_instance_file} does not exist."

    assert validation_instance_file.exists() is True, (
        f"{validation_instance_file} does not exist."
    )

    main_train_content = main_instance_file.open().readlines()
    validation_content = validation_instance_file.open().readlines()

    assert main_train_content == validation_content, (
        "The instance file and its validation copy do not have the same content."
    )


@pytest.mark.parametrize(
    "output_dir_case, case",
    [
        (Path("tests/test_files/Ablation/Ablation_Correct"), "correct"),
        (Path("tests/test_files/Ablation/No_Ablation"), "no"),
        (Path("tests/test_files/Ablation/Ablation_Corrupted"), "corrupted"),
    ],
)
def test_check_for_ablation(output_dir_case: Path, case: str) -> None:
    """Test for method check_for_ablation."""
    scenario_check = AblationScenario(
        configuration_scenario,
        test_dataset,
        cutoff_length,
        concurrent_clis,
        best_configuration,
        ablation_racing,
    )
    # Override table file to check test file
    scenario_check._table_file = output_dir_case / scenario_check.table_file.name
    return_val = scenario_check.check_for_ablation()
    if case == "correct":
        assert return_val is True
    else:
        assert return_val is False


@pytest.mark.parametrize(
    "output_dir_case, case",
    [
        (Path("tests/test_files/Ablation/Ablation_Correct"), "correct"),
        (Path("tests/test_files/Ablation/No_Ablation"), "no"),
        (Path("tests/test_files/Ablation/Ablation_Corrupted"), "corrupted"),
    ],
)
def test_read_ablation_table(output_dir_case: Path, case: str) -> None:
    """Test for reading an ablation table."""
    scenario_read = AblationScenario(
        configuration_scenario,
        test_dataset,
        cutoff_length,
        concurrent_clis,
        best_configuration,
        ablation_racing,
    )
    # Override table file to check test file
    scenario_read._table_file = output_dir_case / scenario_read.table_file.name
    ablation_table = scenario_read.read_ablation_table()
    if case == "correct":
        for line in ablation_table:
            assert type(line) is list
            assert len(line) == 5  # Always same length
            for value in line:
                assert type(value) is str
    else:
        assert ablation_table == []


@pytest.mark.parametrize(
    "test_set",
    [
        Instance_Set(Path("tests/test_files/Instances/Test-Instance-Set")),
        None,
    ],
)
@patch("sparkle.configurator.configurator.AblationScenario.check_requirements")
def test_submit_ablation(mock_requirements: Mock, test_set: Instance_Set) -> None:
    """Test for method submit ablation."""
    mock_requirements.return_value = True  # Mock requirements to avoid exception
    log_dir = Path("Output/Log")
    scenario_submit = AblationScenario(
        configuration_scenario,
        test_set,
        cutoff_length,
        concurrent_clis,
        best_configuration,
        ablation_racing,
    )
    with patch("runrunner.add_to_queue") as mock_add_to_queue:
        result = scenario_submit.submit_ablation(log_dir)

        if test_set:
            assert mock_add_to_queue.call_count == 2, (
                "Expected add_to_queue to be called twice."
            )
            assert len(result) == 2, (
                "Expected two Run objects in the returned list. "
                f"Instead got: {len(result)}"
            )
        else:
            assert mock_add_to_queue.call_count == 1, (
                "Expected add_to_queue to be called once."
            )
            assert len(result) == 1, (
                "Expected one Run objects in the returned list. "
                f"Instead got: {len(result)}"
            )

        assert isinstance(result, list), (
            f"submit_ablation should return a list. Instead got: {result}"
        )
