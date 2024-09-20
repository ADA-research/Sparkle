"""Tests for all helper functions in sparkle_generate_report_for_configuration_help."""

import pytest
from pathlib import Path

from pytest_mock import MockFixture

from sparkle.solver.ablation import AblationScenario
from sparkle.platform import generate_report_for_configuration as sgrch
from sparkle.platform.settings_objects import Settings
from sparkle.solver.validator import Validator
from sparkle.types.objective import SparkleObjective, PAR
from sparkle.solver import Solver
from sparkle.instance import instance_set
import csv

global settings
settings = Settings()

configurator = settings.get_general_sparkle_configurator()
solver_path = Path("tests/test_files/Solvers/Test-Solver")
solver = Solver(solver_path, raw_output_directory=Path(""))
train_instance = "train-instance"
test_instance = "test-instance"
configurator_path = configurator.configurator_path
configurator.scenario =\
    configurator.scenario_class(solver, Path(train_instance))
configurator.scenario._set_paths(configurator_path)
ablation_scenario = AblationScenario(
    solver, Path(train_instance), Path(test_instance), Path(""))
validator = Validator()
test_objective_runtime = PAR(10)
test_objective_quality = SparkleObjective("ACCURACY")


def test_get_average_performance(mocker: MockFixture) -> None:
    """Test get_average_performance returns correct value.

    A performance list should be retrieved from results file.
    The mean of the performance values should be computed and returned.
    """
    mock_get_list = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                 "get_dict_instance_to_performance",
                                 return_value={"one": 10, "two": 5})

    avg = sgrch.get_average_performance([], test_objective_runtime)
    mock_get_list.assert_called_once_with([], test_objective_runtime)
    assert avg == 7.5


def test_get_dict_instance_to_performance(mocker: MockFixture) -> None:
    """Test get_dict_instance_to_performance creates dict from performance list."""
    validation_file = Path("tests/test_files/Validator/validation.csv")
    csv_data = [line for line in csv.reader(validation_file.open("r"))]
    instance_dict = sgrch.get_dict_instance_to_performance(
        csv_data, test_objective_runtime)
    assert instance_dict == {
        "bce7824.cnf": 10.1316,
        "Ptn-7824-b09.cnf": 10.0667,
        "Ptn-7824-b13.cnf": 10.0786,
        "Ptn-7824-b21.cnf": 10.1152,
        "Ptn-7824-b15.cnf": 10.1177,
        "Ptn-7824-b01.cnf": 10.0812,
        "Ptn-7824-b19.cnf": 10.0642,
        "Ptn-7824-b05.cnf": 10.1184,
        "Ptn-7824-b03.cnf": 10.1368,
        "Ptn-7824-b11.cnf": 10.1921,
        "Ptn-7824-b07.cnf": 10.1672,
        "Ptn-7824-b17.cnf": 0.993013
    }


def test_get_ablation_bool_true(mocker: MockFixture) -> None:
    """Test get_ablation_bool returns correct string if get_ablation_bool is True."""
    mock_check = mocker.patch("sparkle.solver.ablation.AblationScenario."
                              "check_for_ablation",
                              return_value=True)
    ablation_bool = sgrch.get_ablation_bool(ablation_scenario)
    mock_check.assert_called_once()
    assert ablation_bool == r"\ablationtrue"


def test_get_ablation_bool_false(mocker: MockFixture) -> None:
    """Test get_ablation_bool returns correct string if get_ablation_bool is False."""
    mock_check = mocker.patch("sparkle.solver.ablation.AblationScenario."
                              "check_for_ablation",
                              return_value=False)
    ablation_bool = sgrch.get_ablation_bool(ablation_scenario)
    mock_check.assert_called_once()
    assert ablation_bool == r"\ablationfalse"


def test_get_data_for_plot_same_instance(mocker: MockFixture) -> None:
    """Test get_data_for_plot returns list of values if dicts are correct."""
    dict_configured = {"instance-1.cnf": 1.0}
    dict_default = {"instance-1.cnf": 0.01}
    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_instance_to_performance",
                             side_effect=[dict_configured, dict_default])

    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    points = sgrch.get_data_for_plot(
        configured_dir, default_dir, test_objective_runtime)

    mock_dict.assert_any_call(default_dir, test_objective_runtime)
    mock_dict.assert_any_call(configured_dir, test_objective_runtime)
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
    with pytest.raises(SystemExit):
        sgrch.get_data_for_plot(
            configured_dir, default_dir, test_objective_runtime)

    mock_dict.assert_any_call(default_dir, test_objective_runtime)
    mock_dict.assert_any_call(default_dir, test_objective_runtime)


def test_get_figure_configure_vs_default(mocker: MockFixture) -> None:
    """Test get_figure_configure_vs_default creates plot and returns correct string.

    The function `generate_comparison_plot()` should be called with the correct
    arguments.
    Also, the correct LaTeX string to include the figure should be returned.
    """
    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    reports_dir = Path("configuration/report")
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
    mock_plot = mocker.patch("sparkle.platform.latex.generate_comparison_plot")

    figure_string = sgrch.get_figure_configure_vs_default(configured_dir,
                                                          default_dir,
                                                          reports_dir,
                                                          filename,
                                                          performance_measure,
                                                          cutoff,
                                                          test_objective_runtime)

    mock_data.assert_called_once_with(configured_dir, default_dir,
                                      test_objective_runtime)
    mock_plot.assert_called_once_with(points, filename, **plot_params)
    assert figure_string == f"\\includegraphics[width=0.6\\textwidth]{{{filename}}}"


def test_get_figure_configure_vs_default_par(mocker: MockFixture) -> None:
    """Test get_figure_configure_vs_default adds params for performance measure PAR.

    If the performance measure starts with PAR, `generate_comparison_plot()` should
    be called with additional parameters.
    """
    configured_dir = "configured/directory/"
    default_dir = "default/directory/"
    reports_dir = Path("configuration/report")
    filename = "figure.jpg"
    cutoff = 1

    points = [[1.0, 0.1]]
    performance_measure = "PAR12"
    plot_params = {"xlabel": f"Default parameters [{performance_measure}]",
                   "ylabel": f"Configured parameters [{performance_measure}]",
                   "scale": "log",
                   "limit_min": 0.25,
                   "limit_max": 0.25,
                   "limit": "magnitude",
                   "replace_zeros": True,
                   "output_dir": reports_dir
                   }
    mock_data = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_data_for_plot",
                             return_value=points)
    mock_plot = mocker.patch("sparkle.platform.latex.generate_comparison_plot")

    figure_string = sgrch.get_figure_configure_vs_default(configured_dir,
                                                          default_dir,
                                                          reports_dir,
                                                          filename,
                                                          performance_measure,
                                                          cutoff,
                                                          test_objective_runtime)

    mock_data.assert_called_once_with(configured_dir, default_dir,
                                      test_objective_runtime)
    mock_plot.assert_called_once_with(points, filename, **plot_params)
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

    configured, default, overlap = sgrch.get_timeouts(
        conf_dict, default_dict, cutoff)

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
    mock_table = mocker.patch("sparkle.solver.ablation.AblationScenario."
                              "read_ablation_table",
                              return_value=sah_ablation_table)

    table_string = sgrch.get_ablation_table(ablation_scenario)

    mock_table.assert_called_once()
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
    output_dir = Path("configuration/report")
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
        Path("configuration/report"), solver, configurator, validator, Path(),
        Path(), train_instance, 1, test_instance, None)

    mock_common.assert_called_once_with(solver, configurator, validator,
                                        None, Path(), train_instance,
                                        output_dir)
    mock_test.assert_called_once_with(output_dir, solver, configurator, validator,
                                      None, train_instance, test_instance)
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
    output_dir = Path("configuration/report")
    common_dict = {
        "common-1": "1",
        "common-2": "2",
        "featuresBool": r"\featuresfalse"
    }
    mock_common = mocker.patch("sparkle.platform.generate_report_for_configuration."
                               "get_dict_variable_to_value_common",
                               return_value=common_dict)

    full_dict = sgrch.configuration_report_variables(
        output_dir, solver, configurator, validator, Path(),
        Path(), train_instance, 1, test_instance, None)

    mock_common.assert_called_once_with(solver, configurator, validator, None, Path(),
                                        train_instance, output_dir)
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
    output_dir = Path("configuration/report")
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
        output_dir, solver, configurator, validator, Path(),
        Path(), train_instance, 1, test_instance, ablation_scenario)

    mock_common.assert_called_once_with(
        solver, configurator, validator, ablation_scenario,
        Path(), train_instance, output_dir)
    mock_test.assert_called_once_with(
        output_dir, solver, configurator, validator,
        ablation_scenario, train_instance, test_instance)
    assert full_dict == {
        "testBool": r"\testtrue"
    } | common_dict | test_dict


def test_configuration_report_variables_with_features(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value returns correct dictionary.

    If the key `featuresBool` in the common dictionary is found and set to true,
    the corresponding other keys should be added to the final dictionary.
    """
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = Path("configuration/report")
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
    mocker.patch("pathlib.Path.iterdir",
                 return_value=[Path("extract1"), Path("extract2")])
    mocker.patch("sparkle.platform.latex.list_to_latex", return_value="43")
    mocker.patch("pathlib.Path.mkdir", return_value=None)
    extractor_dir = Path("extract/dir")
    full_dict = sgrch.configuration_report_variables(
        output_dir, solver, configurator, validator, extractor_dir,
        Path(), train_instance, 1, test_instance, ablation_scenario)

    mock_common.assert_called_once_with(
        solver, configurator, validator, ablation_scenario, Path(), train_instance,
        output_dir)
    mock_test.assert_called_once_with(
        output_dir, solver, configurator, validator, ablation_scenario, train_instance,
        test_instance)
    assert full_dict == {
        "testBool": r"\testtrue",
        "numFeatureExtractors": "2",
        "featureExtractorList": "43",
        "featureComputationCutoffTime": "44"
    } | common_dict | test_dict


def test_get_dict_variable_to_value_common(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value_common creates the correct dictionary.

    Test that all needed functions are called to retrieve values and that these
    values are added to the common dictionary.
    """
    train_instance = Path("train-instance")
    validation_data = [
        ["SolverName", "{}", "InstanceSetName", "InstanceName", "STATUS", "0", "25.323"]]
    report_dir = "reports/directory"
    cutoff = 60
    configurator.scenario.cutoff_time = cutoff
    configurator.scenario.number_of_runs = 25
    configurator.scenario.wallclock_time = 600
    configurator.scenario.sparkle_objective = test_objective_quality

    mocker.patch("sparkle.about.version", "0.8")
    mocker.patch("sparkle.platform.generate_"
                 "report_for_configuration."
                 "get_average_performance",
                 side_effect=[42.1, 42.2])
    mocker.patch("sparkle.platform.generate_report_for_configuration."
                 "get_features_bool",
                 return_value="\\featuresfalse")
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
    bib_path = Path("tex/bib.bib")
    common_dict = sgrch.get_dict_variable_to_value_common(
        solver, configurator, validator, ablation_scenario, bib_path, train_instance,
        report_dir)

    mock_figure.assert_called_once_with(solver, train_instance.name, validation_data,
                                        validation_data, report_dir, "QUALITY",
                                        float(cutoff), test_objective_quality)
    mock_timeouts.assert_called_once_with(
        solver, train_instance, configurator, validator, 60)
    mock_ablation_bool.assert_called_once_with(ablation_scenario)
    mock_ablation_table.assert_called_once_with(ablation_scenario)

    assert common_dict == {
        "performanceMeasure": "ACCURACY",
        "runtimeBool": "\\runtimefalse",
        "solver": solver.name,
        "instanceSetTrain": train_instance.name,
        "sparkleVersion": "0.8",
        "numInstanceInTrainingInstanceSet": 1,
        "numSmacRuns": 25,
        "smacObjective": "QUALITY",
        "smacWholeTimeBudget": 600,
        "smacEachRunCutoffTime": cutoff,
        "optimisedConfiguration": "123",
        "optimisedConfigurationTrainingPerformancePAR": 42.1,
        "defaultConfigurationTrainingPerformancePAR": 42.2,
        "figure-configured-vs-default-train": "figure-string",
        "timeoutsTrainDefault": 3,
        "timeoutsTrainConfigured": 2,
        "timeoutsTrainOverlap": 1,
        "ablationBool": "ablationtrue",
        "ablationPath": "ablation/path",
        "bibliographypath": bib_path.absolute(),
        "featuresBool": "\\featuresfalse"
    }


def test_get_dict_variable_to_value_test(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value_test creates the correct dictionary.

    Test that all needed functions are called to retrieve values and that these
    values are added to the common dictionary.
    """
    train_set = instance_set(Path("tests/test_files/Instances/Train-Instance-Set"))
    test_set = instance_set(Path("tests/test_files/Instances/Test-Instance-Set"))
    validation_data = [
        ["SolverName", "{}", "InstanceSetName", "InstanceName", "STATUS", "0", "25.323"]]
    cutoff = "60"

    mocker.patch("sparkle.platform.generate_"
                 "report_for_configuration."
                 "get_average_performance",
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
    configurator.scenario.cutoff_time = 60
    configurator.scenario.sparkle_objective = test_objective_quality
    test_dict = sgrch.get_dict_variable_to_value_test(Path("configuration/report"),
                                                      solver,
                                                      configurator,
                                                      validator,
                                                      ablation_scenario,
                                                      train_set,
                                                      test_set)

    mock_figure.assert_called_once_with(
        solver, test_set.name, validation_data, validation_data,
        Path("configuration/report"), "QUALITY", float(cutoff),
        test_objective_quality, data_type="test")
    mock_timeouts.assert_called_once_with(
        solver, test_set, configurator, validator, 60)
    mock_ablation_bool.assert_called_once_with(ablation_scenario)
    mock_ablation_table.assert_called_once_with(ablation_scenario)
    assert test_dict == {
        "instanceSetTest": test_set.name,
        "numInstanceInTestingInstanceSet": 1,
        "optimisedConfigurationTestingPerformancePAR": 42.1,
        "defaultConfigurationTestingPerformancePAR": 42.2,
        "figure-configured-vs-default-test": "figure-string",
        "timeoutsTestDefault": 3,
        "timeoutsTestConfigured": 2,
        "timeoutsTestOverlap": 1,
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
        "bibliographypath": ""
    }

    report_dir = Path("configuration/report")

    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "configuration_report_variables",
                             return_value=value_dict)
    mock_generate_report = mocker.patch("sparkle.platform.latex.generate_report",
                                        return_value=None)

    sgrch.generate_report_for_configuration(solver,
                                            configurator,
                                            validator,
                                            Path(),
                                            report_dir,
                                            Path(),
                                            Path(),
                                            1.0,
                                            train_instance,
                                            ablation=True)
    mock_dict.assert_called_once_with(report_dir, solver,
                                      configurator, validator, Path(),
                                      Path(), 1.0, train_instance, None, True)
    mock_generate_report.assert_called_once()


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

    report_dir = Path("configuration/report")

    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "configuration_report_variables",
                             return_value=value_dict)
    mock_generate_report = mocker.patch("sparkle.platform.latex.generate_report",
                                        return_value=None)

    sgrch.generate_report_for_configuration(solver,
                                            configurator,
                                            validator,
                                            Path(),
                                            report_dir,
                                            Path(),
                                            Path(),
                                            1.0,
                                            train_instance,
                                            test_instance, ablation)

    mock_dict.assert_called_once_with(
        report_dir, solver, configurator, validator,
        Path(), Path(), 1.0, train_instance, test_instance, ablation)
    mock_generate_report.assert_called_once()
