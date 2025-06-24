"""Test public methods of IRACE configurator."""
import pytest
import shutil
import warnings
from pathlib import Path
from unittest.mock import Mock, patch, ANY

import runrunner as rrr

from sparkle.CLI import initialise

from sparkle.configurator.implementations import IRACE, IRACEScenario
from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame
from sparkle.types import resolve_objective
from sparkle.types.objective import PAR

from tests.CLI import tools as cli_tools


@patch("runrunner.add_to_queue")
def test_irace_configure(mock_add_to_queue: Mock) -> None:
    """Test IRACE configure method."""
    if shutil.which("Rscript") is None:
        warnings.warn("R is not installed, which is required for the IRACE")
        return
    if not IRACE.configurator_executable.exists():
        returncode = initialise.initialise_irace()  # Ensure IRACE is compiled
        if returncode != 0:
            warnings.warn("Failed to install IRACE, skipping test")
            return
    sparkle_objective = PAR(10)
    test_files = Path("tests", "test_files")
    base_dir = test_files / "tmp"
    output = Path("Output")
    irace_conf = IRACE(output, base_dir)
    train_set = Instance_Set(test_files / "Instances/Train-Instance-Set")
    solver = Solver(test_files / "Solvers/Test-Solver")
    conf_scenario = IRACEScenario(
        solver, train_set, [sparkle_objective], 2, base_dir,
        solver_calls=25,
        solver_cutoff_time=60,
        max_time=200,
    )
    assert irace_conf.output_path == output / IRACE.__name__
    assert irace_conf.base_dir == base_dir
    assert irace_conf.tmp_path == output / IRACE.__name__ / "tmp"
    assert irace_conf.multiobjective is False

    if cli_tools.get_cluster_name() != "kathleen":
        # Test currently does not work on Github Actions due missing packages
        return

    # Testing without validation afterwards
    mock_add_to_queue.return_value = None

    # We currently cannot test these strings as they are using absolute paths
    cmds = ANY
    outputs = ANY
    data_target = PerformanceDataFrame(
        Path("tests/test_files/performance/example_empty_runs.csv"))
    # Make a copy to avoid writing
    data_target = data_target.clone(Path("tmp-pdf.csv"))

    runs = irace_conf.configure(conf_scenario,
                                data_target=data_target,
                                validate_after=False,
                                base_dir=base_dir)
    mock_add_to_queue.assert_called_once_with(
        runner=rrr.Runner.SLURM,
        base_dir=base_dir,
        cmd=cmds,
        output_path=outputs,
        parallel_jobs=None,
        name=f"{IRACE.__name__}: {conf_scenario.solver.name} on "
             f"{conf_scenario.instance_set.name}",
        sbatch_options=[],
        prepend=None,
    )
    assert runs == [None]
    data_target.csv_filepath.unlink()


def test_irace_organise_output(tmp_path: Path,
                               monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE organise output method."""
    if shutil.which("Rscript") is None:
        warnings.warn("Rscript is not installed, which is required for the IRACE")
        return
    if cli_tools.get_cluster_name() != "kathleen":
        return  # Test does not work on Github because it can't find IRACE package
    source_path = Path("tests/test_files/Configuration/"
                       "test_output_irace.Rdata").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    if not IRACE.configurator_executable.exists():
        returncode = initialise.initialise_irace()  # Ensure IRACE is compiled
        if returncode != 0:
            warnings.warn("Failed to install IRACE, skipping test")
            return
    assert IRACE.organise_output(source_path, None, None, 1) == {
        "init_solution": "1", "perform_pac": "0", "perform_first_div": "1",
        "perform_double_cc": "1", "perform_aspiration": "1",
        "sel_var_break_tie_greedy": "4", "perform_clause_weight": "0",
        "sel_clause_div": "2", "sel_var_div": "6", "prob_first_div": "0.9918",
        "gamma_hscore2": "495644", "prob_novelty": "0.4843"}


def test_irace_scenario_file(tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE scenario file creation."""
    if cli_tools.get_cluster_name() != "kathleen":
        # Test currently does not work on Github Actions due missing packages
        return
    solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    set = Instance_Set(Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    if not IRACE.configurator_executable.exists():
        returncode = initialise.initialise_irace()  # Ensure IRACE is compiled
        if returncode != 0:
            warnings.warn("Failed to install IRACE, skipping test")
            return
    obj_par, obj_acc = resolve_objective("PAR10"), resolve_objective("accuray:max")
    scenario = IRACEScenario(solver, set, [obj_par, obj_acc], 2, Path("irace_scenario"),
                             solver_calls=2, solver_cutoff_time=2)
    scenario.create_scenario()
    # TODO: Add file comparison, requires variables/regex to match


def test_irace_scenario_from_file() -> None:
    """Test IRACE scenario file creation."""
    solver = Solver(Path("Examples/Resources/Solvers/PbO-CCSAT-Generic"))
    set = Instance_Set(Path("Examples/Resources/Instances/PTN"))
    scenario_file = Path("tests/test_files/Configuration/"
                         "PbO-CCSAT-Generic_PTN_scenario_irace.txt")
    scenario = IRACEScenario.from_file(scenario_file)
    assert scenario.solver.name == solver.name
    assert scenario.instance_set.name == set.name
    assert scenario.solver_calls is None
    assert scenario.solver_cutoff_time == 60
    assert scenario.max_time == 1750
    assert scenario.sparkle_objective.name == "PAR10"
