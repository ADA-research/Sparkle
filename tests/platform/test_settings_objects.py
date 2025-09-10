"""Test class for the Settings class."""

import pytest
from pathlib import Path
import argparse
import random
from unittest.mock import patch
import re

from sparkle.CLI.help import global_variables as gv
from sparkle.platform.settings_objects import Settings, Option
from sparkle.CLI import add_solver, run_solvers, add_instances


def test_option() -> None:
    """Test the Option (NamedTuple) class."""
    option_a = Option("a", "sec1", int, 1, ("c", "d"))
    _option_a = Option("a", "sec1", int, 1, ("c", "d"))
    # Basic property tests
    assert option_a == _option_a
    assert option_a == "a"
    option_b = Option("b", "sec2", int, 2, ("f", "g"))
    assert option_a != option_b
    # Test fetching from list
    assert "a" in [option_a, option_b]
    # Test getting index
    assert [option_a, option_b].index("a") == 0
    assert [option_b, option_a, _option_a].index("a") == 1
    # Test with arparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(*option_a.args, **option_a.kwargs)
    assert len(parser._actions) == 1
    assert parser._actions[0].dest == option_a.name
    assert parser._actions[0].type == option_a.type


def test_read_from_file() -> None:
    """Test reading settings from file."""
    default_settings = Path("sparkle/Components/sparkle_settings.ini")
    settings = Settings(default_settings)
    assert set([o.name for o in settings.objectives]) == set(
        [
            "PAR10",
            "status:metric",
            "cpu_time:metric",
            "wall_time:metric",
            "memory:metric",
        ]
    )
    assert settings.solver_cutoff_time == 60
    assert settings.extractor_cutoff_time == 60
    assert settings.run_on == "slurm"
    assert settings.verbosity_level.name == "STANDARD"
    assert settings.seed is None

    # Configurator
    assert settings.configurator.name == "SMAC2"
    assert settings.configurator_number_of_runs == 9
    assert settings.configurator_solver_call_budget is None
    assert settings.configurator_max_iterations is None

    # Ablation
    assert settings.ablation_racing_flag
    assert settings.ablation_max_parallel_runs_per_node == 8

    # Selection
    assert settings.selection_model == "RandomForestClassifier"
    assert settings.selection_class == "MultiClassClassifier"

    # SMAC2
    assert settings.smac2_wallclock_time_budget == 600
    assert settings.smac2_cpu_time_budget is None
    assert settings.smac2_target_cutoff_length == "max"
    assert settings.smac2_max_iterations is None
    assert settings.smac2_use_tunertime_in_cpu_time_budget is None
    assert settings.smac2_cli_cores is None

    # SMAC3
    assert settings.smac3_number_of_trials is None
    assert settings.smac3_facade == "HyperparameterOptimizationFacade"
    assert settings.smac3_facade_max_ratio is None
    assert settings.smac3_crash_cost is None
    assert settings.smac3_termination_cost_threshold is None
    assert settings.smac3_wallclock_time_budget is None
    assert settings.smac3_cpu_time_budget == 600.0
    assert settings.smac3_use_default_config is None
    assert settings.smac3_min_budget is None
    assert settings.smac3_min_budget is None

    # IRACE
    assert settings.irace_max_time == 1750
    assert settings.irace_max_experiments == 0
    assert settings.irace_first_test == 2
    assert settings.irace_mu == 2
    assert settings.irace_max_iterations == 1

    # ParamILS
    assert settings.paramils_cpu_time_budget == 600
    assert settings.paramils_max_runs is None
    assert settings.paramils_min_runs is None
    assert settings.paramils_random_restart is None
    assert not settings.paramils_focused_approach
    assert settings.paramils_use_cpu_time_in_tunertime is None
    assert settings.paramils_cli_cores is None
    assert settings.paramils_max_iterations is None
    assert settings.paramils_number_initial_configurations is None


def test_file_with_cli_args() -> None:
    """Test reading settings from file with CLI override args."""
    default_settings = Path("sparkle/Components/sparkle_settings.ini")
    settings = Settings(default_settings)
    assert settings.solver_cutoff_time == 60
    assert settings.extractor_cutoff_time == 60
    assert settings.configurator_solver_call_budget is None
    # Create parser to mimic CLI args
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        *Settings.OPTION_solver_cutoff_time.args,
        **Settings.OPTION_solver_cutoff_time.kwargs,
    )
    parser.add_argument(
        *Settings.OPTION_extractor_cutoff_time.args,
        **Settings.OPTION_extractor_cutoff_time.kwargs,
    )
    parser.add_argument(
        *Settings.OPTION_configurator_solver_call_budget.args,
        **Settings.OPTION_configurator_solver_call_budget.kwargs,
    )
    args = parser.parse_args(
        [
            "--solver-cutoff-time",
            "10",
            "--extractor-cutoff-time",
            "20",
            "--solver-calls",
            "100",
        ]
    )
    settings = Settings(default_settings, args)
    assert settings.solver_cutoff_time == 10
    assert settings.extractor_cutoff_time == 20
    assert settings.configurator_solver_call_budget == 100


def test_read_empty_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading an empty file for standard properties."""
    empty = Path("tests/test_files/Settings/settings-empty.ini").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    settings = Settings(empty)
    assert settings.solver_cutoff_time is None
    assert settings.irace_max_time == 0
    assert settings.irace_max_experiments == 0
    assert settings.smac3_facade == "AlgorithmConfigurationFacade"
    assert settings.verbosity_level.name == "STANDARD"
    assert settings.seed is None

    # Check that writing settings read from an empty file produces an empty file
    tmp = Path("tmp.ini")
    settings.write_settings_ini(tmp)
    assert tmp.read_text() == ""


def test_read_full_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading settings from file where each setting gets a value."""
    default_settings = Path("tests/test_files/Settings/settings-full.ini").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    settings = Settings(default_settings)
    assert set([o.name for o in settings.objectives]) == set(
        [
            "PAR10",
            "status:metric",
            "cpu_time:metric",
            "wall_time:metric",
            "memory:metric",
        ]
    )
    assert settings.solver_cutoff_time == 60
    assert settings.extractor_cutoff_time == 60
    assert settings.run_on == "slurm"
    assert settings.verbosity_level.name == "QUIET"
    assert settings.seed == 1

    # Configurator
    assert settings.configurator.name == "SMAC3"
    assert settings.configurator_number_of_runs == 69
    assert settings.configurator_solver_call_budget == 420
    assert settings.configurator_max_iterations == 42

    # Ablation
    assert settings.ablation_racing_flag
    assert settings.ablation_max_parallel_runs_per_node == 3

    # Selection
    assert settings.selection_model == "RandomForestClassifier"
    assert settings.selection_class == "MultiClassClassifier"

    # SMAC2
    assert settings.smac2_wallclock_time_budget == 600
    assert settings.smac2_cpu_time_budget == 450
    assert settings.smac2_target_cutoff_length == "max"
    assert settings.smac2_use_tunertime_in_cpu_time_budget
    assert settings.smac2_cli_cores == 4
    assert settings.smac2_max_iterations == 200

    # SMAC3
    assert settings.smac3_number_of_trials == 85
    assert settings.smac3_facade == "HyperparameterOptimizationFacade"
    assert settings.smac3_facade_max_ratio == 0.44
    assert settings.smac3_crash_cost == 99.99
    assert settings.smac3_termination_cost_threshold == 49.99
    assert settings.smac3_wallclock_time_budget == 600.0
    assert settings.smac3_cpu_time_budget == 450.0
    assert settings.smac3_use_default_config
    assert settings.smac3_min_budget == 10.0
    assert settings.smac3_max_budget == 55.0

    # IRACE
    assert settings.irace_max_time == 999
    assert settings.irace_max_experiments == 33
    assert settings.irace_first_test == 8
    assert settings.irace_mu == 3
    assert settings.irace_max_iterations == 6

    # ParamILS
    assert settings.paramils_cpu_time_budget == 600
    assert settings.paramils_min_runs == 1
    assert settings.paramils_max_runs == 99
    assert settings.paramils_random_restart == 0.01
    assert settings.paramils_focused_approach
    assert settings.paramils_use_cpu_time_in_tunertime
    assert settings.paramils_cli_cores == 4
    assert settings.paramils_max_iterations == 175
    assert settings.paramils_number_initial_configurations == 29

    # Parallel Portfolio
    assert settings.parallel_portfolio_check_interval == 10
    assert settings.parallel_portfolio_num_seeds_per_solver == 5

    # Slurm
    assert settings.slurm_jobs_in_parallel == 16
    assert settings.slurm_job_prepend == "echo $JOB_ID"
    assert set(settings.sbatch_settings) == set(
        ["--mem-per-cpu=3000", "--time=25:00", "--partition=CPU", "--qos=fast"]
    )
    # Test writing the file
    tmp = Path("tmp.ini")
    settings.write_settings_ini(tmp)
    settings_tmp = Settings(tmp)
    assert Settings.check_settings_changes(settings, settings_tmp) is False


def test_read_with_cli_file() -> None:
    """Test reading settings with CLI file argument."""
    default_settings = Path("tests/test_files/Settings/settings-full.ini")
    settings_arg = Path("sparkle/Components/sparkle_settings.ini")
    args = argparse.Namespace(
        **{"settings_file": settings_arg, "solver_cutoff_time": 900}
    )  # Random setting
    settings = Settings(default_settings, args)
    # Test overridden attributes
    assert set([o.name for o in settings.objectives]) == set(
        [
            "PAR10",
            "status:metric",
            "cpu_time:metric",
            "wall_time:metric",
            "memory:metric",
        ]
    )
    assert settings.solver_cutoff_time == 900  # Override
    assert settings.extractor_cutoff_time == 60
    assert settings.run_on == "slurm"
    assert settings.verbosity_level.name == "QUIET"
    assert settings.seed == 1

    # Configurator
    assert settings.configurator.name == "SMAC2"  # Override
    assert settings.configurator_number_of_runs == 9  # Override
    assert settings.configurator_solver_call_budget == 420
    assert settings.configurator_max_iterations == 42

    # Ablation
    assert settings.ablation_racing_flag
    assert settings.ablation_max_parallel_runs_per_node == 8

    # Selection
    assert settings.selection_model == "RandomForestClassifier"
    assert settings.selection_class == "MultiClassClassifier"

    # SMAC2
    assert settings.smac2_wallclock_time_budget == 600
    assert settings.smac2_cpu_time_budget == 450
    assert settings.smac2_target_cutoff_length == "max"
    assert settings.smac2_use_tunertime_in_cpu_time_budget
    assert settings.smac2_cli_cores == 4
    assert settings.smac2_max_iterations == 200

    # SMAC3
    assert settings.smac3_number_of_trials == 85
    assert settings.smac3_facade == "HyperparameterOptimizationFacade"
    assert settings.smac3_facade_max_ratio == 0.44
    assert settings.smac3_crash_cost == 99.99
    assert settings.smac3_termination_cost_threshold == 49.99
    assert settings.smac3_wallclock_time_budget == 600.0
    assert settings.smac3_cpu_time_budget == 600.0  # Override
    assert settings.smac3_use_default_config
    assert settings.smac3_min_budget == 10.0
    assert settings.smac3_max_budget == 55.0

    # IRACE
    assert settings.irace_max_time == 1750  # Override
    assert settings.irace_max_experiments == 33
    assert settings.irace_first_test == 2  # Override
    assert settings.irace_mu == 2  # Override
    assert settings.irace_max_iterations == 1  # Override

    # ParamILS
    assert settings.paramils_cpu_time_budget == 600
    assert settings.paramils_min_runs == 1
    assert settings.paramils_max_runs == 99
    assert settings.paramils_random_restart == 0.01
    assert settings.paramils_focused_approach
    assert settings.paramils_use_cpu_time_in_tunertime
    assert settings.paramils_cli_cores == 4
    assert settings.paramils_max_iterations == 175
    assert settings.paramils_number_initial_configurations == 29

    # Parallel Portfolio
    assert settings.parallel_portfolio_check_interval == 4  # Override
    assert settings.parallel_portfolio_num_seeds_per_solver == 2  # Override

    # Slurm
    assert settings.slurm_jobs_in_parallel == 25  # Override
    assert settings.slurm_job_prepend == "echo $JOB_ID"
    assert set(settings.sbatch_settings) == set(
        ["--mem-per-cpu=3000", "--time=25:00", "--partition=CPU", "--qos=fast"]
    )

    # Test smaller override for integration tests
    override_path = Path("tests/CLI/test_files/Settings/sparkle_settings_kathleen.ini")
    args = argparse.Namespace(**{"settings_file": override_path})
    settings.apply_arguments(args)

    assert set(settings.sbatch_settings) == set(
        ["--mem-per-cpu=3000", "--time=30:00", "--qos=short", "--partition=CPU"]
    )


def test_set_random_state() -> None:
    """Test the global random state."""
    Settings.DEFAULT_settings_path = Path("tests/test_files/Settings/settings-full.ini")
    Settings.DEFAULT_previous_settings_path = Path(
        "tests/test_files/Settings/latest.ini"
    )
    Settings.DEFAULT_previous_settings_path.unlink(missing_ok=True)
    assert Settings(Settings.DEFAULT_settings_path).seed == 1

    # Case 1: Seed is set by user and latest.ini has no seed
    gv.__settings = None  # Needed because other tests use the settings
    rng = random.Random(1)
    next_seed = rng.randint(0, 2**32 - 1)
    assert gv.settings().seed == next_seed
    gv.settings().write_used_settings()
    latest_ini = Settings(Settings.DEFAULT_previous_settings_path)
    assert latest_ini.seed == next_seed
    assert rng.randint(0, 2**32 - 1) == random.randint(0, 2**32 - 1)

    # Case 2: latest.ini has a seed
    gv.__settings = None
    rng = random.Random(next_seed)
    next_seed = rng.randint(0, 2**32 - 1)
    assert gv.settings().seed == next_seed
    gv.settings().write_used_settings()
    latest_ini = Settings(Settings.DEFAULT_previous_settings_path)
    assert latest_ini.seed == next_seed
    assert rng.randint(0, 2**32 - 1) == random.randint(0, 2**32 - 1)

    # Case 3: User did not set a seed and latest.ini has no seed
    Settings.DEFAULT_settings_path = Path("tests/test_files/Settings/settings-empty.ini")
    Settings.DEFAULT_previous_settings_path.unlink(missing_ok=True)
    assert Settings(Settings.DEFAULT_settings_path).seed is None

    gv.__settings = None
    # Simulate seed behavior of the global random state
    rng = random.Random(0)
    init_seed = rng.randint(0, 2**32 - 1)
    rng = random.Random(init_seed)
    next_seed = rng.randint(0, 2**32 - 1)
    # Set the seed for reproducible test
    rng = random.seed(0)
    assert gv.settings().seed == next_seed

    # Remove latest.ini test file
    Settings.DEFAULT_previous_settings_path.unlink(missing_ok=True)


@pytest.mark.integration
def test_submitted_seeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run solvers example to test submitted seeds."""
    solver_path = (
        Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic"
    ).absolute()
    instances_path = (Path("Examples") / "Resources" / "Instances" / "PTN").absolute()
    settings_path = Path("tests/test_files/Settings/settings-full.ini").absolute()
    Settings.DEFAULT_settings_path = Path(
        "tests/test_files/Settings/settings-full.ini"
    ).absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Smoke test
    # First we add solvers and instances to the platform
    rng = random.Random(1)
    next_seed = rng.randint(0, 2**32 - 1)
    gv.__settings = None

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_solver.main([str(solver_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert gv.settings().seed == next_seed

    rng = random.Random(next_seed)
    next_seed = rng.randint(0, 2**32 - 1)
    gv.__settings = None
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_instances.main([str(instances_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert gv.settings().seed == next_seed

    rng = random.Random(next_seed)
    next_seed = rng.randint(0, 2**32 - 1)
    gv.__settings = None
    with patch("runrunner.add_to_queue") as mock_add_to_queue:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            run_solvers.main(
                [
                    "--performance-data-jobs",
                    "--recompute",
                    "--run-on",
                    "local",
                    "--settings-file",
                    str(settings_path),
                ]
            )
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
        assert gv.settings().seed == next_seed

        mock_add_to_queue.assert_called_once()
        _, kwargs = mock_add_to_queue.call_args

        for cmd in kwargs["cmd"]:
            match = re.search(r"--seed (\d+)", cmd)
            seed_str = match.group(1)
            cur_seed = int(seed_str)
            assert cur_seed == rng.randint(0, 2**32 - 1)
