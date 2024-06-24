"""Tests for all helper functions in sparkle_generate_report_for_configuration_help."""

import pytest
from pathlib import Path

from pytest_mock import MockFixture

from sparkle.platform import generate_report_for_configuration as sgrch
import global_variables as gv
from sparkle.platform import settings_help
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.types.objective import PerformanceMeasure, SparkleObjective
from sparkle.solver import Solver
import csv

global settings
gv.settings = settings_help.Settings()

configurator = gv.settings.get_general_sparkle_configurator()
configurator_path = configurator.configurator_path
solver_path = Path("tests/test_files/Solvers/Test-Solver")
solver = Solver(solver_path, raw_output_directory=Path(""))
train_instance = "train-instance"
test_instance = "test-instance"
test_objective_runtime = SparkleObjective("RUNTIME:PAR10")
test_objective_quality = SparkleObjective("QUALITY_ABSOLUTE:ACCURACY")
test_objective_err = SparkleObjective("ERR:ERR")
test_objective_err.PerformanceMeasure = PerformanceMeasure.ERR


def setup_conf() -> None:
    """Set up the configurator for the tests."""
    configurator = gv.settings.get_general_sparkle_configurator()
    configurator_path = configurator.configurator_path
    configurator.scenario =\
        ConfigurationScenario(solver, Path(train_instance))
    configurator.scenario._set_paths(configurator_path)


def test_get_par_performance(mocker: MockFixture) -> None:
    """Test get_par_performance returns correct PAR value.

    A performance list should be retrieved from results file.
    The mean of the performance values should be computed and returned.
    """
    cutoff = 42
    mock_get_list = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                 "get_dict_instance_to_performance",
                                 return_value={"one": 10, "two": 5})

    par = sgrch.get_par_performance([], cutoff)

    mock_get_list.assert_called_once_with([], cutoff)
    assert par == 7.5


def test_get_dict_instance_to_performance(mocker: MockFixture) -> None:
    """Test get_dict_instance_to_performance creates dict from performance list."""
    validation_file = Path("tests/test_files/Validator/validation.csv")
    csv_data = [line for line in csv.reader(validation_file.open("r"))][1:]
    cutoff = 10.05
    instance_dict = sgrch.get_dict_instance_to_performance(csv_data, cutoff)
    assert instance_dict == {
        "Ptn-7824-b01.cnf": 100.5,
        "Ptn-7824-b03.cnf": 100.5,
        "Ptn-7824-b05.cnf": 100.5,
        "Ptn-7824-b07.cnf": 100.5,
        "Ptn-7824-b09.cnf": 100.5,
        "Ptn-7824-b11.cnf": 100.5,
        "Ptn-7824-b13.cnf": 100.5,
        "Ptn-7824-b15.cnf": 100.5,
        "Ptn-7824-b17.cnf": 0.993013,
        "Ptn-7824-b19.cnf": 100.5,
        "Ptn-7824-b21.cnf": 100.5,
        "bce7824.cnf": 100.5,
    }


def test_get_performance_measure_par10(mocker: MockFixture) -> None:
    """Test get_performance_measure returns correct measure.

    Return `PAR10` for RUNTIME with default penalty multiplier of 10.
    """
    mock_settings = mocker.patch("sparkle.platform.settings_help.Settings."
                                 "get_general_sparkle_objectives",
                                 return_value=[test_objective_runtime])
    mock_multiplier = mocker.patch("sparkle.platform.settings_help.Settings."
                                   "get_general_penalty_multiplier",
                                   return_value=10)

    measure = sgrch.get_performance_measure()

    mock_settings.assert_called_once_with()
    mock_multiplier.assert_called_once_with()
    assert measure == "PAR10"


def test_get_performance_measure_par5(mocker: MockFixture) -> None:
    """Test get_performance_measure returns correct measure.

    Return `PAR5` for RUNTIME with non-default penalty multiplier of 5.
    """
    mock_settings = mocker.patch("sparkle.platform.settings_help.Settings."
                                 "get_general_sparkle_objectives",
                                 return_value=[test_objective_runtime])
    mock_multiplier = mocker.patch("sparkle.platform.settings_help.Settings."
                                   "get_general_penalty_multiplier",
                                   return_value=5)

    measure = sgrch.get_performance_measure()

    mock_settings.assert_called_once_with()
    mock_multiplier.assert_called_once_with()
    assert measure == "PAR5"


def test_get_performance_measure_quality(mocker: MockFixture) -> None:
    """Test get_performance_measure returns correct measure for QUALITY."""
    mock_settings = mocker.patch("sparkle.platform.settings_help.Settings."
                                 "get_general_sparkle_objectives",
                                 return_value=[test_objective_quality])
    measure = sgrch.get_performance_measure()
    print(measure)
    print(test_objective_quality.PerformanceMeasure)
    mock_settings.assert_called_once_with()
    assert measure == "performance"


def test_get_runtime_bool(mocker: MockFixture) -> None:
    """Test get_runtime_bool returns correct string for objective RUNTIME."""
    mock_settings = mocker.patch("sparkle.platform.settings_help.Settings."
                                 "get_general_sparkle_objectives",
                                 return_value=[test_objective_runtime])
    runtime_bool = sgrch.get_runtime_bool()

    mock_settings.assert_called_once_with()
    assert runtime_bool == r"\runtimetrue"

    # Quality
    mock_settings = mocker.patch("sparkle.platform.settings_help.Settings."
                                 "get_general_sparkle_objectives",
                                 return_value=[test_objective_quality])

    runtime_bool = sgrch.get_runtime_bool()

    mock_settings.assert_called_once_with()
    assert runtime_bool == r"\runtimefalse"

    # Other
    mock_settings = mocker.patch("sparkle.platform.settings_help.Settings."
                                 "get_general_sparkle_objectives",
                                 return_value=[test_objective_err])

    runtime_bool = sgrch.get_runtime_bool()

    mock_settings.assert_called_once_with()
    assert runtime_bool == ""


def test_get_ablation_bool_true(mocker: MockFixture) -> None:
    """Test get_ablation_bool returns correct string if get_ablation_bool is True."""
    mock_check = mocker.patch("CLI.support.ablation_help."
                              "check_for_ablation",
                              return_value=True)

    ablation_bool = sgrch.get_ablation_bool("test-solver",
                                            "train-instance",
                                            "test-instance")

    mock_check.assert_called_once_with("test-solver",
                                       "train-instance",
                                       "test-instance")
    assert ablation_bool == r"\ablationtrue"


def test_get_ablation_bool_false(mocker: MockFixture) -> None:
    """Test get_ablation_bool returns correct string if get_ablation_bool is False."""
    mock_check = mocker.patch("CLI.support.ablation_help."
                              "check_for_ablation",
                              return_value=False)

    ablation_bool = sgrch.get_ablation_bool("test-solver",
                                            "train-instance",
                                            "test-instance")

    mock_check.assert_called_once_with("test-solver",
                                       "train-instance",
                                       "test-instance")
    assert ablation_bool == r"\ablationfalse"


def test_get_data_for_plot_same_instance(mocker: MockFixture) -> None:
    """Test get_data_for_plot returns list of values if dicts are correct."""
    dict_configured = {
        "instance-1.cnf": 1.0
    }
    dict_default = {
        "instance-1.cnf": 0.01
    }
    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_instance_to_performance",
                             side_effect=[dict_configured, dict_default])

    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    cutoff = 0
    points = sgrch.get_data_for_plot(configured_dir, default_dir, cutoff)

    mock_dict.assert_any_call(default_dir, cutoff)
    mock_dict.assert_any_call(configured_dir, cutoff)
    assert points == [[1.0, 0.01]]


def test_get_data_for_plot_instance_error(mocker: MockFixture) -> None:
    """Test get_data_for_plot raises a SystemExit if dicts to not fit.

    If the two dicts do not contain the same instances, an error is raised.
    """
    dict_configured = {
        "instance-2.cnf": 1.0
    }
    dict_default = {
        "instance-1.cnf": 0.01
    }
    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_instance_to_performance",
                             side_effect=[dict_configured, dict_default])

    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    cutoff = 0
    with pytest.raises(SystemExit):
        sgrch.get_data_for_plot(configured_dir, default_dir, cutoff)

    mock_dict.assert_any_call(default_dir, cutoff)
    mock_dict.assert_any_call(configured_dir, cutoff)


def test_get_figure_configure_vs_default(mocker: MockFixture) -> None:
    """Test get_figure_configure_vs_default creates plot and returns correct string.

    The function `generate_comparison_plot()` should be called with the correct
    arguments.
    Also, the correct LaTeX string to include the figure should be returned.
    """
    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    reports_dir = gv.configuration_output_analysis
    filename = "figure.jpg"
    cutoff = 0

    points = [[1.0, 0.1]]
    performance_measure = "PERF_MEASURE"
    plot_params = {"xlabel": f"Default parameters [{performance_measure}]",
                   "ylabel": f"Configured parameters [{performance_measure}]",
                   "output_dir": reports_dir,
                   "scale": "linear",
                   "limit_min": 1.5,
                   "limit_max": 1.5,
                   "limit": "relative",
                   "replace_zeros": False,
                   }
    mock_data = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_data_for_plot",
                             return_value=points)
    mock_performance = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                    "get_performance_measure",
                                    return_value=performance_measure)
    mock_plot = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "generate_comparison_plot")

    figure_string = sgrch.get_figure_configure_vs_default(configured_dir,
                                                          default_dir,
                                                          reports_dir,
                                                          filename,
                                                          cutoff)

    mock_data.assert_called_once_with(configured_dir, default_dir, cutoff)
    mock_performance.assert_called_once_with()
    mock_plot.assert_called_once_with(points, filename, **plot_params)
    assert figure_string == f"\\includegraphics[width=0.6\\textwidth]{{{filename}}}"


def test_get_figure_configure_vs_default_par(mocker: MockFixture) -> None:
    """Test get_figure_configure_vs_default adds params for performance measure PAR.

    If the performance measure starts with PAR, `generate_comparison_plot()` should
    be called with additional parameters.
    """
    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    reports_dir = gv.configuration_output_analysis
    filename = "figure.jpg"
    cutoff = 0

    points = [[1.0, 0.1]]
    performance_measure = "PAR12"
    plot_params = {"xlabel": f"Default parameters [{performance_measure}]",
                   "ylabel": f"Configured parameters [{performance_measure}]",
                   "scale": "log",
                   "limit_min": 0.25,
                   "limit_max": 0.25,
                   "limit": "magnitude",
                   "penalty_time": 10,
                   "replace_zeros": True,
                   "output_dir": reports_dir
                   }
    mock_data = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_data_for_plot",
                             return_value=points)
    mock_performance = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                    "get_performance_measure",
                                    return_value=performance_measure)
    mock_plot = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "generate_comparison_plot")

    mock_penalised = mocker.patch("sparkle.platform.settings_help.Settings."
                                  "get_penalised_time",
                                  return_value=10)

    figure_string = sgrch.get_figure_configure_vs_default(configured_dir,
                                                          default_dir,
                                                          reports_dir,
                                                          filename,
                                                          cutoff)

    mock_data.assert_called_once_with(configured_dir, default_dir, cutoff)
    mock_performance.assert_called_once_with()
    mock_plot.assert_called_once_with(points, filename, **plot_params)
    mock_penalised.assert_called_once_with()
    assert figure_string == f"\\includegraphics[width=0.6\\textwidth]{{{filename}}}"


def test_get_timeouts(mocker: MockFixture) -> None:
    """Test get_timeouts correctly computes timeouts and overlapping values for dicts."""
    conf_dict = {
        "instance-1.cnf": 100.0,
        "instance-2.cnf": 100.0,
        "instance-3.cnf": 0.01,
        "instance-4.cnf": 0.01,
    }
    default_dict = {
        "instance-1.cnf": 0.01,
        "instance-2.cnf": 100.0,
        "instance-3.cnf": 100.0,
        "instance-4.cnf": 100.0,
    }
    cutoff = 10

    mock_multiplier = mocker.patch("sparkle.platform.settings_help."
                                   "Settings.get_general_penalty_multiplier",
                                   return_value=10)

    configured, default, overlap = sgrch.get_timeouts(conf_dict, default_dict, cutoff)

    mock_multiplier.assert_called_once()
    assert configured == 2
    assert default == 3
    assert overlap == 1


def test_get_ablation_table(mocker: MockFixture) -> None:
    """Test get_ablation_table calls sah.get_ablation_table and transforms its string."""
    sah_ablation_table = (
        [["Round", "Flipped parameter", "Source value", "Target value",
          "Validation result"],
         ["0", "-source-", "N/A", "N/A", "76.53275"],
         ["1", "sel_var_div", "3", "6", "68.41392"],
         ["2", "-target-", "N/A", "N/A", "92.06944"]])
    mock_table = mocker.patch("CLI.support.ablation_help."
                              "read_ablation_table",
                              return_value=sah_ablation_table)

    table_string = sgrch.get_ablation_table(solver, train_instance, test_instance)

    mock_table.assert_called_once_with(solver, train_instance, test_instance)
    assert table_string == (r"\begin{tabular}{rp{0.25\linewidth}rrr}"
                            r"\textbf{Round} & \textbf{Flipped parameter} & "
                            r"\textbf{Source value} & \textbf{Target value} & "
                            r"\textbf{Validation result} \\ \hline "
                            r"0 & -source- & N/A & N/A & 76.53275 \\ "
                            r"1 & sel_var_div & 3 & 6 & 68.41392 \\ "
                            r"2 & -target- & N/A & N/A & 92.06944 \\ "
                            r"\end{tabular}")


def test_get_dict_variable_to_value_with_test(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value returns correct dictionary.

    If a test instance is present, the function should add the corresponding entry
    to the dictionary.
    """
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = gv.configuration_output_analysis
    ablation = False
    common_dict = {
        "common-1": "1",
        "common-2": "2",
        "featuresBool": r"\featuresfalse"
    }
    test_dict = {
        "test-1": "3",
        "test-2": "4"
    }
    mock_common = mocker.patch("sparkle.platform.generate_report_for_configuration."
                               "get_dict_variable_to_value_common",
                               return_value=common_dict)
    mock_test = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_variable_to_value_test",
                             return_value=test_dict)

    full_dict = sgrch.configuration_report_variables(
        gv.configuration_output_analysis, solver, train_instance,
        test_instance, ablation)

    mock_common.assert_called_once_with(solver, train_instance,
                                        test_instance, output_dir)
    mock_test.assert_called_once_with(output_dir, solver,
                                      train_instance, test_instance)
    assert full_dict == {
        "testBool": r"\testtrue",
        "ablationBool": r"\ablationfalse"
    } | common_dict | test_dict


def test_configuration_report_variables_without_test(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value returns correct dictionary.

    If no test instance is present, the function should add the corresponding entry
    to the dictionary.
    """
    train_instance = "train-instance"
    test_instance = None
    output_dir = gv.configuration_output_analysis
    ablation = False
    common_dict = {
        "common-1": "1",
        "common-2": "2",
        "featuresBool": r"\featuresfalse"
    }
    mock_common = mocker.patch("sparkle.platform.generate_report_for_configuration."
                               "get_dict_variable_to_value_common",
                               return_value=common_dict)

    full_dict = sgrch.configuration_report_variables(
        output_dir, solver, train_instance, test_instance,
        ablation)

    mock_common.assert_called_once_with(solver, train_instance,
                                        test_instance, output_dir)
    assert full_dict == {
        "testBool": r"\testfalse",
        "ablationBool": r"\ablationfalse"
    } | common_dict


def test_configuration_report_variables_with_ablation(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value returns correct dictionary.

    If `ablation` is set to True, the key `ablationBool` should not be set in the
    dictionary.
    """
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = gv.configuration_output_analysis
    ablation = True
    common_dict = {
        "common-1": "1",
        "common-2": "2",
        "featuresBool": r"\featuresfalse"
    }
    test_dict = {
        "test-1": "3",
        "test-2": "4"
    }
    mock_common = mocker.patch("sparkle.platform.generate_report_for_configuration."
                               "get_dict_variable_to_value_common",
                               return_value=common_dict)
    mock_test = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_variable_to_value_test",
                             return_value=test_dict)

    full_dict = sgrch.configuration_report_variables(
        gv.configuration_output_analysis, solver, train_instance,
        test_instance, ablation)

    mock_common.assert_called_once_with(solver, train_instance,
                                        test_instance, output_dir)
    mock_test.assert_called_once_with(output_dir, solver,
                                      train_instance, test_instance)
    assert full_dict == {
        "testBool": r"\testtrue"
    } | common_dict | test_dict


def test_configuration_report_variables_with_features(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value returns correct dictionary.

    If the key `featuresBool` in the common dictionary is found and set to true,
    the corresponding other keys should be added to the final dictionary.
    """
    setup_conf()
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = gv.configuration_output_analysis
    ablation = True
    common_dict = {
        "common-1": "1",
        "common-2": "2",
        "featuresBool": r"\featurestrue"
    }
    test_dict = {
        "test-1": "3",
        "test-2": "4"
    }
    mock_common = mocker.patch("sparkle.platform.generate_report_for_configuration."
                               "get_dict_variable_to_value_common",
                               return_value=common_dict)
    mock_test = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_variable_to_value_test",
                             return_value=test_dict)
    mock_extractor_list = mocker.patch("sparkle.platform.generate_report_for_selection."
                                       "get_feature_extractor_list",
                                       return_value="43")
    mocker.patch("pathlib.Path.mkdir", return_value=None)

    full_dict = sgrch.configuration_report_variables(
        gv.configuration_output_analysis, solver, train_instance,
        test_instance, ablation)

    mock_common.assert_called_once_with(solver, train_instance,
                                        test_instance, output_dir)
    mock_test.assert_called_once_with(output_dir, solver,
                                      train_instance, test_instance)
    mock_extractor_list.assert_called_once_with()
    assert full_dict == {
        "testBool": r"\testtrue",
        "numFeatureExtractors": "42",
        "featureExtractorList": "43",
        "featureComputationCutoffTime": "44"
    } | common_dict | test_dict


def test_get_dict_variable_to_value_common(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value_common creates the correct dictionary.

    Test that all needed functions are called to retrieve values and that these
    values are added to the common dictionary.
    """
    setup_conf()
    train_instance = Path("train-instance")
    test_instance = Path("test-instance")
    validation_data = [
        ["SolverName", "{}", "InstanceSetName", "InstanceName", "STATUS", "0", "25.323"]]
    report_dir = "reports/directory"
    cutoff = "60"
    mock_perf = mocker.patch("sparkle.platform.generate_"
                             "report_for_configuration."
                             "get_performance_measure",
                             return_value="PERF")
    mocker.patch("sparkle.about.version", "0.8")
    mocker.patch("sparkle.platform.generate_"
                 "report_for_configuration."
                 "get_par_performance",
                 side_effect=[42.1, 42.2])
    mock_figure = mocker.patch("sparkle.platform.generate_"
                               "report_for_configuration."
                               "get_figure_configured_vs_default_on_"
                               "instance_set",
                               return_value="figure-string")
    mock_timeouts = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_timeouts_instanceset",
                                 return_value=(2, 3, 1))
    mock_ablation_bool = mocker.patch("sparkle.platform.generate_"
                                      "report_for_configuration."
                                      "get_ablation_bool",
                                      return_value="ablationtrue")
    mock_ablation_table = mocker.patch("sparkle.platform.generate_"
                                       "report_for_configuration."
                                       "get_ablation_table",
                                       return_value="ablation/path")
    mocker.patch("sparkle.configurator.implementations.smac2."
                 "SMAC2.get_optimal_configuration", return_value=(0, "123"))
    mocker.patch("pathlib.Path.iterdir", return_value=[Path("test1")])
    mocker.patch("sparkle.solver.validator.Validator.get_validation_results",
                 return_value=validation_data)

    common_dict = sgrch.get_dict_variable_to_value_common(solver, train_instance,
                                                          test_instance, report_dir)

    mock_perf.assert_called_once_with()
    mock_figure.assert_called_once_with(solver, train_instance.name,
                                        validation_data, validation_data, report_dir,
                                        float(cutoff))
    mock_timeouts.assert_called_once_with(solver, train_instance, float(cutoff))
    mock_ablation_bool.assert_called_once_with(solver, train_instance.name,
                                               test_instance.name)
    mock_ablation_table.assert_called_once_with(solver, train_instance.name,
                                                test_instance.name)

    assert common_dict == {
        "performanceMeasure": "PERF",
        "runtimeBool": "\\runtimetrue",
        "solver": solver.name,
        "instanceSetTrain": train_instance.name,
        "sparkleVersion": "0.8",
        "numInstanceInTrainingInstanceSet": "1",
        "numSmacRuns": "25",
        "smacObjective": "RUNTIME",
        "smacWholeTimeBudget": "600",
        "smacEachRunCutoffTime": cutoff,
        "optimisedConfiguration": "123",
        "optimisedConfigurationTrainingPerformancePAR": "42.1",
        "defaultConfigurationTrainingPerformancePAR": "42.2",
        "figure-configured-vs-default-train": "figure-string",
        "timeoutsTrainDefault": "3",
        "timeoutsTrainConfigured": "2",
        "timeoutsTrainOverlap": "1",
        "ablationBool": "ablationtrue",
        "ablationPath": "ablation/path",
        "bibliographypath": str(gv.sparkle_report_bibliography_path.absolute()),
        "featuresBool": "\\featuresfalse"
    }


def test_get_dict_variable_to_value_test(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value_test creates the correct dictionary.

    Test that all needed functions are called to retrieve values and that these
    values are added to the common dictionary.
    """
    setup_conf()
    train_instance = Path("train-instance")
    test_instance = Path("test-instance")
    validation_data = [
        ["SolverName", "{}", "InstanceSetName", "InstanceName", "STATUS", "0", "25.323"]]
    cutoff = "60"

    mocker.patch("sparkle.platform.generate_"
                 "report_for_configuration."
                 "get_par_performance",
                 side_effect=[42.1, 42.2])
    mock_figure = mocker.patch("sparkle.platform.generate_"
                               "report_for_configuration."
                               "get_figure_configured_vs_default_on_"
                               "instance_set",
                               return_value="figure-string")
    mock_timeouts = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_timeouts_instanceset",
                                 return_value=(2, 3, 1))
    mock_ablation_bool = mocker.patch("sparkle.platform.generate_"
                                      "report_for_configuration."
                                      "get_ablation_bool",
                                      return_value="ablationtrue")
    mock_ablation_table = mocker.patch("sparkle.platform.generate_"
                                       "report_for_configuration."
                                       "get_ablation_table",
                                       return_value="ablation/path")
    mocker.patch("pathlib.Path.iterdir", return_value=[Path("test1")])
    mocker.patch("sparkle.solver.validator.Validator.get_validation_results",
                 return_value=validation_data)
    mocker.patch("sparkle.configurator.implementations.SMAC2."
                 "get_optimal_configuration", return_value=(0.0, "configurino"))

    test_dict = sgrch.get_dict_variable_to_value_test(gv.configuration_output_analysis,
                                                      solver,
                                                      train_instance,
                                                      test_instance)

    mock_figure.assert_called_once_with(solver, test_instance.name,
                                        validation_data, validation_data,
                                        gv.configuration_output_analysis,
                                        float(cutoff), data_type="test")
    mock_timeouts.assert_called_once_with(solver, test_instance, float(cutoff))
    mock_ablation_bool.assert_called_once_with(solver, train_instance.name,
                                               test_instance.name)
    mock_ablation_table.assert_called_once_with(solver, train_instance.name,
                                                test_instance.name)
    assert test_dict == {
        "instanceSetTest": test_instance.name,
        "numInstanceInTestingInstanceSet": "1",
        "optimisedConfigurationTestingPerformancePAR": "42.1",
        "defaultConfigurationTestingPerformancePAR": "42.2",
        "figure-configured-vs-default-test": "figure-string",
        "timeoutsTestDefault": "3",
        "timeoutsTestConfigured": "2",
        "timeoutsTestOverlap": "1",
        "ablationBool": "ablationtrue",
        "ablationPath": "ablation/path"
    }


def test_generate_report_for_configuration_train(mocker: MockFixture) -> None:
    """Test generate_report_for_configuration_train generates report.

    The function should call functions to prepare report generation and call
    `generate_report_for_configuration_common` with the right parameters.
    """
    train_instance = "train-instance"

    value_dict = {
        "key-1": "value-1",
        "key-2": "value-2",
        "bibliographypath": str(gv.sparkle_report_bibliography_path.absolute())
    }

    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "configuration_report_variables",
                             return_value=value_dict)
    mock_generate_report = mocker.patch("sparkle.platform.generate_report_for_selection."
                                        "generate_report", return_value=None)
    mock_log = mocker.patch("sparkle_logging.add_output",
                            return_value=None)

    sgrch.generate_report_for_configuration(solver,
                                            gv.configuration_output_analysis,
                                            train_instance, ablation=True)
    mock_dict.assert_called_once_with(gv.configuration_output_analysis, solver,
                                      train_instance, None, True)
    mock_generate_report.assert_called_once()
    mock_log.assert_called_once()


def test_generate_report_for_configuration(mocker: MockFixture) -> None:
    """Test generate_report_for_configuration generates report.

    The function should call functions to prepare report generation and call
    `generate_report_for_configuration_common` with the right parameters.
    """
    train_instance = "train-instance"
    test_instance = "test-instance"
    ablation = True

    value_dict = {
        "key-1": "value-1",
        "key-2": "value-2"
    }

    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "configuration_report_variables",
                             return_value=value_dict)
    mock_generate_report = mocker.patch("sparkle.platform.generate_report_for_selection"
                                        ".generate_report", return_value=None)
    mock_log = mocker.patch("sparkle_logging.add_output",
                            return_value=None)

    sgrch.generate_report_for_configuration(solver,
                                            gv.configuration_output_analysis,
                                            train_instance,
                                            test_instance, ablation)

    mock_dict.assert_called_once_with(
        gv.configuration_output_analysis,
        solver, train_instance, test_instance, ablation)
    mock_generate_report.assert_called_once()
    mock_log.assert_called_once()
