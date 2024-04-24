"""Tests for all helper functions in sparkle_generate_report_for_configuration_help."""

import pytest
from pathlib import Path

from pytest_mock import MockFixture

from sparkle.platform import generate_report_for_configuration as sgrch
import global_variables as sgh
from sparkle.platform import settings_help
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.solver.solver import Solver

global settings
sgh.settings = settings_help.Settings()

configurator = sgh.settings.get_general_sparkle_configurator()
configurator_path = configurator.configurator_path
solver_name = "test-solver"
train_instance = "train-instance"
test_instance = "test-instance"


def setup_conf() -> None:
    """Set up the configurator for the tests."""
    configurator = sgh.settings.get_general_sparkle_configurator()
    configurator_path = configurator.configurator_path
    configurator.scenario =\
        ConfigurationScenario(Solver(Path(solver_name)), Path(train_instance))
    configurator.scenario._set_paths(configurator_path)


def test_get_num_in_instance_set_reference_list_exists(mocker: MockFixture) -> None:
    """Test get_num_in_instance_set_smac_dir for correct return and call of functions.

    Check that number of instances is retrieved from reference list when it exists.
    """
    mock_check_existence = mocker.patch("sparkle.instance.instances_help."
                                        "check_existence_of_reference_instance_list",
                                        return_value=True)
    mock_count_instances = mocker.patch("sparkle.instance.instances_help."
                                        "count_instances_in_reference_list",
                                        return_value=3)
    instance_set_name = "test-instance"

    number = sgrch.get_num_instance_for_configurator(instance_set_name)

    mock_check_existence.assert_called_once_with(instance_set_name)
    mock_count_instances.assert_called_once_with(instance_set_name)
    assert number == "3"


def test_get_num_in_instance_set_reference_list_not_exists(mocker: MockFixture) -> None:
    """Test get_num_in_instance_set_smac_dir for correct return and call of functions.

    Check that number of instances is retrieved by counting all files in instance
    directory when no reference list exists.
    """
    mock_check_existence = mocker.patch("sparkle.instance.instances_help."
                                        "check_existence_of_reference_instance_list",
                                        return_value=False)
    mock_count_instances = mocker.patch("sparkle.instance.instances_help."
                                        "count_instances_in_reference_list",
                                        return_value=3)
    mock_list_filename = mocker.patch("sparkle.platform.file_help."
                                      "get_list_all_filename_recursive",
                                      return_value=[Path("instance-1"),
                                                    Path("instance-2")])
    instance_set_name = "test-instance"

    number = sgrch.get_num_instance_for_configurator(instance_set_name)

    mock_check_existence.assert_called_once_with(instance_set_name)
    mock_count_instances.assert_not_called()

    instance_directory = configurator.instances_path / instance_set_name
    mock_list_filename.assert_called_once_with(instance_directory)
    assert number == "2"


def test_get_par_performance(mocker: MockFixture) -> None:
    """Test get_par_performance returns correct PAR value.

    A performance list should be retrieved from results file.
    The mean of the performance values should be computed and returned.
    """
    results_file = "example_file"
    cutoff = 42
    mock_get_list = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                 "get_instance_performance_from_csv",
                                 return_value=[("one", 10), ("two", 5)])

    par = sgrch.get_par_performance(results_file, cutoff)

    mock_get_list.assert_called_once_with(results_file, cutoff)
    assert par == 7.5


def test_get_instance_performance_from_csv(mocker: MockFixture) -> None:
    """Test get_instance_performance_from_csv creates list from file content."""
    file_content_mock = ('"Problem Instance","Seed",'
                         '"Objective of validation config #1"\n'
                         '"../../instances/instances/instance-1.cnf","null","0.001"\n'
                         '"../../instances/instances/instance-2.cnf","null","1.0"\n'
                         '"../../instances/instances/instance-3.cnf","null","15"\n')
    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data=file_content_mock))
    mocker.patch("CLI.support.configure_solver_help.get_smac_settings",
                 return_value=("RUNTIME", "", "", "", "", ""))

    result_file = ""
    cutoff = 10.0
    list = sgrch.get_instance_performance_from_csv(result_file, cutoff)
    assert list == [("instance-1.cnf", 0.001),
                    ("instance-2.cnf", 1.0),
                    ("instance-3.cnf", 100.0)]


def test_get_dict_instance_to_performance(mocker: MockFixture) -> None:
    """Test get_dict_instance_to_performance creates dict from performance list."""
    instance_list = [("instance-1.cnf", 0.01001),
                     ("instance-2.cnf", 1.0),
                     ("instance-3.cnf", 100)]
    mock_construct = mocker.patch("sparkle.platform.generate_report_"
                                  "for_configuration."
                                  "get_instance_performance_from_csv",
                                  return_value=instance_list)

    result_file = "results.file"
    cutoff = 10
    instance_dict = sgrch.get_dict_instance_to_performance(result_file, cutoff)

    mock_construct.assert_called_once_with(result_file, cutoff)
    assert instance_dict == {
        "instance-1.cnf": 0.01001,
        "instance-2.cnf": 1.0,
        "instance-3.cnf": 100
    }


def test_get_performance_measure_par10(mocker: MockFixture) -> None:
    """Test get_performance_measure returns correct measure.

    Return `PAR10` for RUNTIME with default penalty multiplier of 10.
    """
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("RUNTIME", "", "", "", "", ""))
    mock_multiplier = mocker.patch("sparkle.platform.settings_help."
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
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("RUNTIME", "", "", "", "", ""))
    mock_multiplier = mocker.patch("sparkle.platform.settings_help."
                                   "get_general_penalty_multiplier",
                                   return_value=5)

    measure = sgrch.get_performance_measure()

    mock_settings.assert_called_once_with()
    mock_multiplier.assert_called_once_with()
    assert measure == "PAR5"


def test_get_performance_measure_performance(mocker: MockFixture) -> None:
    """Test get_performance_measure returns correct measure for QUALITY."""
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("QUALITY", "", "", "", "", ""))

    measure = sgrch.get_performance_measure()

    mock_settings.assert_called_once_with()
    assert measure == "performance"


def test_get_runtime_bool(mocker: MockFixture) -> None:
    """Test get_runtime_bool returns correct string for objective RUNTIME."""
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("RUNTIME", "", "", "", "", ""))

    runtime_bool = sgrch.get_runtime_bool()

    mock_settings.assert_called_once_with()
    assert runtime_bool == r"\runtimetrue"

    # Quality
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("QUALITY", "", "", "", "", ""))

    runtime_bool = sgrch.get_runtime_bool()

    mock_settings.assert_called_once_with()
    assert runtime_bool == r"\runtimefalse"

    # Other
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("ERROR", "", "", "", "", ""))

    runtime_bool = sgrch.get_runtime_bool()

    mock_settings.assert_called_once_with()
    assert runtime_bool == ""


def test_get_ablation_bool_true(mocker: MockFixture) -> None:
    """Test get_ablation_bool returns correct string if get_ablation_bool is True."""
    mock_check = mocker.patch("sparkle.configurator.ablation."
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
    mock_check = mocker.patch("sparkle.configurator.ablation."
                              "check_for_ablation",
                              return_value=False)

    ablation_bool = sgrch.get_ablation_bool("test-solver",
                                            "train-instance",
                                            "test-instance")

    mock_check.assert_called_once_with("test-solver",
                                       "train-instance",
                                       "test-instance")
    assert ablation_bool == r"\ablationfalse"


def test_get_features_bool_false(mocker: MockFixture) -> None:
    """Test get_features_bool returns correct string if no feature file is given.

    The function should check the scenario file for a link to the feature file.
    """
    setup_conf()
    file_content_mock = ""
    mock_open = mocker.patch("pathlib.Path.open",
                             mocker.mock_open(read_data=file_content_mock))

    features_bool = sgrch.get_features_bool(solver_name, train_instance)

    mock_open.assert_called_once_with("r")
    assert features_bool == r"\featuresfalse"


def test_get_features_bool_true(mocker: MockFixture) -> None:
    """Test get_features_bool returns correct string if feature file is given.

    The function should check the scenario file for a link to the feature file.
    """
    file_content_mock = "feature_file = some/file"
    mock_open = mocker.patch("pathlib.Path.open",
                             mocker.mock_open(read_data=file_content_mock))

    features_bool = sgrch.get_features_bool(solver_name, train_instance)

    mock_open.assert_called_once_with("r")
    assert features_bool == r"\featurestrue"


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
    reports_dir = sgh.configuration_output_analysis
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
    reports_dir = sgh.configuration_output_analysis
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
    mock_plot = mocker.patch("sparkle.platform.generate_report_help."
                             "generate_comparison_plot")
    mock_penalised = mocker.patch("sparkle.platform.settings_help."
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


def test_get_figure_configured_vs_default_on_test_instance_set(mocker: MockFixture)\
        -> None:
    """Test get_figure_configured_vs_default_on_test_instance_set returns correct string.

    This should call `get_figure_configure_vs_default()` with correct values and return
    its return value.
    """
    setup_conf()
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = "test-instance"
    cutoff = 0
    mock_get_figure = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                   "get_figure_configure_vs_default",
                                   return_value="includegraphics")

    figure_string = sgrch.get_figure_configured_vs_default_on_test_instance_set(
        sgh.configuration_output_analysis,
        solver_name,
        train_instance,
        test_instance,
        cutoff)

    smac_solver_dir = configurator.scenarios_path / (f"{solver_name}_{train_instance}")

    configured_results_file = (
        "validationObjectiveMatrix-configuration_for_validation-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    configured_results_dir = (f"{smac_solver_dir}/outdir_{test_instance}"
                              f"_test_configured/{configured_results_file}")
    default_results_dir = (f"{smac_solver_dir}/outdir_{test_instance}"
                           f"_test_default/{default_results_file}")
    data_plot_filename = (f"data_{solver_name}_configured_vs_default_on_"
                          f"{test_instance}_test")
    mock_get_figure.assert_called_once_with(configured_results_dir,
                                            default_results_dir,
                                            sgh.configuration_output_analysis,
                                            data_plot_filename,
                                            cutoff)
    assert figure_string == "includegraphics"


def test_get_figure_configured_vs_default_on_train_instance_set(mocker: MockFixture)\
        -> None:
    """Test get_figure_configured_vs_default_on_train_instance_set return correct string.

    This should call `get_figure_configure_vs_default()` with correct values and return
    its return value.
    """
    seed = 3
    solver_name = "test-solver"
    train_instance = "train-instance"
    configuration_reports_directory = "reports/"
    cutoff = 0
    mock_config = mocker.patch("CLI.support.configure_solver_help."
                               "get_optimised_configuration",
                               return_value=("", "", seed))
    mock_get_figure = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                   "get_figure_configure_vs_default",
                                   return_value="includegraphics")

    figure_string = sgrch.get_figure_configured_vs_default_on_train_instance_set(
        solver_name,
        train_instance,
        configuration_reports_directory,
        cutoff)

    mock_config.assert_called_once_with(solver_name, train_instance)

    configured_results_file = ("validationObjectiveMatrix-traj-run-"
                               f"{seed}-walltime.csv")
    smac_solver_dir = (
        f"{configurator_path}/scenarios/{solver_name}_{train_instance}/")
    configured_results_dir = (f"{smac_solver_dir}outdir_train_configuration/"
                              f"{solver_name}_{train_instance}_scenario/"
                              f"{configured_results_file}")

    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    default_results_dir = f"{smac_solver_dir}outdir_train_default/{default_results_file}"

    data_plot_filename = (
        f"data_{solver_name}_configured_vs_default_on_{train_instance}_train")

    mock_get_figure.assert_called_once_with(configured_results_dir,
                                            default_results_dir,
                                            configuration_reports_directory,
                                            data_plot_filename,
                                            cutoff)
    assert figure_string == "includegraphics"


def test_get_timeouts_test(mocker: MockFixture) -> None:
    """Test get_timeouts_test returns correct number of timeouts from test set."""
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = "test-instance"
    cutoff = 3
    dict_configured = {
        "instance-2.cnf": 1.0
    }
    dict_default = {
        "instance-1.cnf": 0.01
    }
    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_instance_to_performance",
                             side_effect=[dict_configured, dict_default])
    mock_timeouts = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                 "get_timeouts",
                                 return_value=(0, 1, 2))

    configured, default, overlapping = sgrch.get_timeouts_test(test_instance,
                                                               cutoff)

    configured_results_file = (
        "validationObjectiveMatrix-configuration_for_validation-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    smac_solver_dir = (
        f"{configurator_path}/scenarios/{solver_name}_{train_instance}/")
    configured_results_dir = (f"{smac_solver_dir}outdir_{test_instance}"
                              f"_test_configured/{configured_results_file}")
    default_results_dir = (f"{smac_solver_dir}outdir_{test_instance}"
                           f"_test_default/{default_results_file}")

    mock_dict.assert_any_call(configured_results_dir, cutoff)
    mock_dict.assert_any_call(default_results_dir, cutoff)
    mock_timeouts.assert_called_once_with(dict_configured, dict_default, cutoff)
    assert configured == 0
    assert default == 1
    assert overlapping == 2


def test_get_timeouts_train(mocker: MockFixture) -> None:
    """Test get_timeouts_test returns correct number of timeouts from train set."""
    optimised_configuration_seed = "3"
    solver_name = "test-solver"
    instance_set = "train-instance"
    cutoff = 3
    dict_configured = {
        "instance-2.cnf": 1.0
    }
    dict_default = {
        "instance-1.cnf": 0.01
    }
    mock_config = mocker.patch("CLI.support.configure_solver_help."
                               "get_optimised_configuration",
                               return_value=("", "", optimised_configuration_seed))
    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "get_dict_instance_to_performance",
                             side_effect=[dict_configured, dict_default])
    mock_timeouts = mocker.patch("sparkle.platform.generate_report_for_configuration."
                                 "get_timeouts",
                                 return_value=(0, 1, 2))

    configured, default, overlapping = sgrch.get_timeouts_train(solver_name,
                                                                instance_set,
                                                                cutoff)

    configured_results_file = ("validationObjectiveMatrix-traj-run-"
                               f"{optimised_configuration_seed}-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    smac_solver_dir = (
        f"{configurator_path}/scenarios/{solver_name}_{instance_set}/")
    configured_results_dir = (f"{smac_solver_dir}outdir_train_configuration/"
                              f"{solver_name}_{instance_set}_scenario/"
                              f"{configured_results_file}")
    default_results_dir = f"{smac_solver_dir}outdir_train_default/{default_results_file}"

    mock_config.assert_called_once_with(solver_name, instance_set)
    mock_dict.assert_any_call(configured_results_dir, cutoff)
    mock_dict.assert_any_call(default_results_dir, cutoff)
    mock_timeouts.assert_called_once_with(dict_configured, dict_default, cutoff)
    assert configured == 0
    assert default == 1
    assert overlapping == 2


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
    mock_table = mocker.patch("sparkle.configurator.ablation."
                              "read_ablation_table",
                              return_value=sah_ablation_table)

    table_string = sgrch.get_ablation_table(solver_name, train_instance, test_instance)

    mock_table.assert_called_once_with(solver_name, train_instance, test_instance)
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
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = sgh.configuration_output_analysis
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
        sgh.configuration_output_analysis, solver_name, train_instance,
        test_instance, ablation)

    mock_common.assert_called_once_with(solver_name, train_instance,
                                        test_instance, output_dir)
    mock_test.assert_called_once_with(output_dir, solver_name,
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
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = None
    output_dir = sgh.configuration_output_analysis
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
        output_dir, solver_name, train_instance, test_instance,
        ablation)

    mock_common.assert_called_once_with(solver_name, train_instance,
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
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = sgh.configuration_output_analysis
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
        sgh.configuration_output_analysis, solver_name, train_instance,
        test_instance, ablation)

    mock_common.assert_called_once_with(solver_name, train_instance,
                                        test_instance, output_dir)
    mock_test.assert_called_once_with(output_dir, solver_name,
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
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = "test-instance"
    output_dir = sgh.configuration_output_analysis
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
    mock_extractor_list = mocker.patch("sparkle.platform.generate_report_help."
                                       "get_feature_extractor_list",
                                       return_value="43")

    full_dict = sgrch.configuration_report_variables(
        sgh.configuration_output_analysis, solver_name, train_instance,
        test_instance, ablation)

    mock_common.assert_called_once_with(solver_name, train_instance,
                                        test_instance, output_dir)
    mock_test.assert_called_once_with(output_dir, solver_name,
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
    solver_name = "test-solver"
    train_instance = "train-instance"
    test_instance = "test-instance"
    report_dir = "reports/directory"
    seed = 13
    cutoff = "10"
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("OBJ", 100, cutoff, "", 11, ""))
    mock_config = mocker.patch("CLI.support.configure_solver_help."
                               "get_optimised_configuration",
                               return_value=("123", "", seed))
    mock_perf = mocker.patch("sparkle.platform.generate_"
                             "report_for_configuration."
                             "get_performance_measure",
                             return_value="PERF")
    mock_runtime = mocker.patch("sparkle.platform.generate_"
                                "report_for_configuration."
                                "get_runtime_bool",
                                return_value="runtimetrue")
    mocker.patch("global_variables."
                 "sparkle_version", "0.7")
    mock_instance_num = mocker.patch("sparkle.platform.generate_"
                                     "report_for_configuration."
                                     "get_num_instance_for_configurator",
                                     return_value="4")
    mock_par_perf = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_par_performance",
                                 side_effect=[42.1, 42.2])
    mock_figure = mocker.patch("sparkle.platform.generate_"
                               "report_for_configuration."
                               "get_figure_configured_vs_default_on_train_"
                               "instance_set",
                               return_value="figure-string")
    mock_timeouts = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_timeouts_train",
                                 return_value=(2, 3, 1))
    mock_ablation_bool = mocker.patch("sparkle.platform.generate_"
                                      "report_for_configuration."
                                      "get_ablation_bool",
                                      return_value="ablationtrue")
    mock_ablation_table = mocker.patch("sparkle.platform.generate_"
                                       "report_for_configuration."
                                       "get_ablation_table",
                                       return_value="ablation/path")
    mock_features = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_features_bool",
                                 return_value="featurestrue")

    common_dict = sgrch.get_dict_variable_to_value_common(solver_name, train_instance,
                                                          test_instance, report_dir)

    smac_solver_dir = (
        f"{configurator_path}/scenarios/{solver_name}_{train_instance}/")
    configured_results_train_file = ("validationObjectiveMatrix-traj-run-" + str(seed)
                                     + "-walltime.csv")
    configured_results_train_dir = (f"{smac_solver_dir}outdir_train_configuration/"
                                    f"{solver_name}_{train_instance}_scenario/"
                                    f"{configured_results_train_file}")

    default_results_train_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    default_results_train_dir = (
        smac_solver_dir + "outdir_train_default/" + default_results_train_file)

    mock_settings.assert_called_once_with()
    mock_config.assert_called_with(solver_name, train_instance)
    mock_perf.assert_called_once_with()
    mock_runtime.assert_called_once_with()
    mock_instance_num.assert_called_once_with(train_instance)
    mock_par_perf.assert_has_calls([
        mocker.call(configured_results_train_dir, cutoff),
        mocker.call(default_results_train_dir, cutoff)
    ])
    mock_figure.assert_called_once_with(solver_name, train_instance, report_dir,
                                        float(cutoff))
    mock_timeouts.assert_called_once_with(solver_name, train_instance, float(cutoff))
    mock_ablation_bool.assert_called_once_with(solver_name, train_instance,
                                               test_instance)
    mock_ablation_table.assert_called_once_with(solver_name, train_instance,
                                                test_instance)
    mock_features.assert_called_once_with(solver_name, train_instance)
    assert common_dict == {
        "performanceMeasure": "PERF",
        "runtimeBool": "runtimetrue",
        "solver": solver_name,
        "instanceSetTrain": train_instance,
        "sparkleVersion": "0.7",
        "numInstanceInTrainingInstanceSet": "4",
        "numSmacRuns": "11",
        "smacObjective": "OBJ",
        "smacWholeTimeBudget": "100",
        "smacEachRunCutoffTime": "10",
        "optimisedConfiguration": "123",
        "optimisedConfigurationTrainingPerformancePAR": "42.1",
        "defaultConfigurationTrainingPerformancePAR": "42.2",
        "figure-configured-vs-default-train": "figure-string",
        "timeoutsTrainDefault": "3",
        "timeoutsTrainConfigured": "2",
        "timeoutsTrainOverlap": "1",
        "ablationBool": "ablationtrue",
        "ablationPath": "ablation/path",
        "bibliographypath": str(sgh.sparkle_report_bibliography_path.absolute()),
        "featuresBool": "featurestrue"
    }


def test_get_dict_variable_to_value_test(mocker: MockFixture) -> None:
    """Test get_dict_variable_to_value_test creates the correct dictionary.

    Test that all needed functions are called to retrieve values and that these
    values are added to the common dictionary.
    """
    setup_conf()
    test_instance = "test-instance"
    cutoff = "10"

    mock_instance_num = mocker.patch("sparkle.platform.generate_"
                                     "report_for_configuration."
                                     "get_num_instance_for_configurator",
                                     return_value="4")
    mock_settings = mocker.patch("CLI.support.configure_solver_help."
                                 "get_smac_settings",
                                 return_value=("OBJ", 100, cutoff, "", 11, ""))
    mock_par_perf = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_par_performance",
                                 side_effect=[42.1, 42.2])
    mock_figure = mocker.patch("sparkle.platform.generate_"
                               "report_for_configuration."
                               "get_figure_configured_vs_default_on_test_"
                               "instance_set",
                               return_value="figure-string")
    mock_timeouts = mocker.patch("sparkle.platform.generate_"
                                 "report_for_configuration."
                                 "get_timeouts_test",
                                 return_value=(2, 3, 1))
    mock_ablation_bool = mocker.patch("sparkle.platform.generate_"
                                       "report_for_configuration."
                                      "get_ablation_bool",
                                      return_value="ablationtrue")
    mock_ablation_table = mocker.patch("sparkle.platform.generate_"
                                       "report_for_configuration."
                                       "get_ablation_table",
                                       return_value="ablation/path")

    test_dict = sgrch.get_dict_variable_to_value_test(sgh.configuration_output_analysis,
                                                      solver_name,
                                                      train_instance,
                                                      test_instance)

    smac_solver_dir = (
        f"{configurator_path}/scenarios/{solver_name}_{train_instance}/")

    configured_results_test_file = (
        "validationObjectiveMatrix-configuration_for_validation-walltime.csv")
    configured_results_test_dir = (f"{smac_solver_dir}outdir_{test_instance}"
                                   f"_test_configured/{configured_results_test_file}")

    default_results_test_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    default_results_test_dir = (f"{smac_solver_dir}outdir_{test_instance}"
                                f"_test_default/{default_results_test_file}")

    mock_instance_num.assert_called_once_with(test_instance)
    mock_settings.assert_called_once_with()
    mock_par_perf.assert_has_calls([
        mocker.call(configured_results_test_dir, cutoff),
        mocker.call(default_results_test_dir, cutoff)
    ])
    mock_figure.assert_called_once_with(sgh.configuration_output_analysis,
                                        solver_name, train_instance, test_instance,
                                        float(cutoff))
    mock_timeouts.assert_called_once_with(test_instance, float(cutoff))
    mock_ablation_bool.assert_called_once_with(solver_name, train_instance,
                                               test_instance)
    mock_ablation_table.assert_called_once_with(solver_name, train_instance,
                                                test_instance)
    assert test_dict == {
        "instanceSetTest": test_instance,
        "numInstanceInTestingInstanceSet": "4",
        "optimisedConfigurationTestingPerformancePAR": "42.1",
        "defaultConfigurationTestingPerformancePAR": "42.2",
        "figure-configured-vs-default-test": "figure-string",
        "timeoutsTestDefault": "3",
        "timeoutsTestConfigured": "2",
        "timeoutsTestOverlap": "1",
        "ablationBool": "ablationtrue",
        "ablationPath": "ablation/path"
    }


def test_check_results_exist_all_good(mocker: MockFixture) -> None:
    """Test check_results_exist does not produce an error if all paths exist."""
    mock_exists = mocker.patch("pathlib.Path.exists", return_value=True)

    sgrch.check_results_exist(solver_name, train_instance, test_instance)

    mock_exists.assert_called()


def test_check_results_exist_all_error(mocker: MockFixture) -> None:
    """Test check_results_exist produces the correct error if no path exists.

    If none of the tested paths exist, test that a SystemExit is raised.
    Also, test that the correct error string is printed, explaining each missing path.
    """
    mock_exists = mocker.patch("pathlib.Path.exists", return_value=False)
    mock_print = mocker.patch("builtins.print")

    with pytest.raises(SystemExit):
        sgrch.check_results_exist(solver_name, train_instance, test_instance)

    mock_print.assert_called_once_with(
        "Error: Results not found for the given solver and instance set(s) combination. "
        'Make sure the "configure_solver" and "validate_configured_vs_default" commands '
        "were correctly executed. \nDetected errors:\n training set not found in "
        "configuration directory Components/smac-v2.10.03-master-778/scenarios/"
        "instances/train-instance; configured parameter results on the training set not "
        "found in Components/smac-v2.10.03-master-778/scenarios/test-solver_train-"
        "instance/outdir_train_configuration/test-solver_train-instance_scenario/; "
        "default parameter results on the training set not found in Components/"
        "smac-v2.10.03-master-778/scenarios/test-solver_train-instance/"
        "outdir_train_default/; testing set not found in configuration directory "
        "Components/smac-v2.10.03-master-778/scenarios/instances/test-instance; "
        "configured parameter results on the testing set not found in Components/"
        "smac-v2.10.03-master-778/scenarios/test-solver_train-instance/outdir_test-"
        "instance_test_configured/; default parameter results on the testing set not "
        "found in Components/smac-v2.10.03-master-778/scenarios/test-solver_train-"
        "instance/outdir_test-instance_test_default/;")

    mock_exists.assert_called()


def test_get_most_recent_test_run_full(mocker: MockFixture) -> None:
    """Test get_most_recent_test_run returns the correct tuple if present in file.

    If the last test file contains information on train and test instances, return the
    corresponding information and set the flags to True.
    """
    file_content_mock = ("solver Solvers/PbO-CCSAT-Generic\n"
                         "train Instances/PTN\n"
                         "test Instances/PTN2")

    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data=file_content_mock))

    (train_instance, test_instance, train_flag, test_flag) = (
        sgrch.get_most_recent_test_run())

    assert train_instance == "Instances/PTN"
    assert test_instance == "Instances/PTN2"
    assert train_flag
    assert test_flag


def test_get_most_recent_test_run_empty(mocker: MockFixture) -> None:
    """Test get_most_recent_test_run returns empyt strings if values not present in file.

    If the last test file contains no information on train and test instances, return the
    empty strings and set the flags to False.
    """
    file_content_mock = ("solver Solvers/PbO-CCSAT-Generic\n")

    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data=file_content_mock))

    (train_instance, test_instance, train_flag, test_flag) = (
        sgrch.get_most_recent_test_run())

    assert train_instance == ""
    assert test_instance == ""
    assert not train_flag
    assert not test_flag


def test_generate_report_for_configuration_train(mocker: MockFixture) -> None:
    """Test generate_report_for_configuration_train generates report.

    The function should call functions to prepare report generation and call
    `generate_report_for_configuration_common` with the right parameters.
    """
    solver_name = "solver-name"
    train_instance = "train-instance"

    value_dict = {
        "key-1": "value-1",
        "key-2": "value-2",
        "bibliographypath": str(sgh.sparkle_report_bibliography_path.absolute())
    }

    mock_dict = mocker.patch("sparkle.platform.generate_report_for_configuration."
                             "configuration_report_variables",
                             return_value=value_dict)
    mock_generate_report = mocker.patch("sparkle.platform.generate_report"
                                        "_help.generate_report", return_value=None)
    mock_log = mocker.patch("sparkle_logging.add_output",
                            return_value=None)

    sgrch.generate_report_for_configuration(solver_name, train_instance, ablation=True)
    mock_dict.assert_called_once_with(sgh.configuration_output_analysis, solver_name,
                                      train_instance, None, True)
    mock_generate_report.assert_called_once()
    mock_log.assert_called_once()


def test_generate_report_for_configuration(mocker: MockFixture) -> None:
    """Test generate_report_for_configuration generates report.

    The function should call functions to prepare report generation and call
    `generate_report_for_configuration_common` with the right parameters.
    """
    solver_name = "solver-name"
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
    mock_generate_report = mocker.patch("sparkle.platform.generate_report"
                                        "_help.generate_report", return_value=None)
    mock_log = mocker.patch("sparkle_logging.add_output",
                            return_value=None)

    sgrch.generate_report_for_configuration(solver_name, train_instance,
                                            test_instance, ablation)

    mock_dict.assert_called_once_with(
        sgh.configuration_output_analysis,
        solver_name, train_instance, test_instance, ablation)
    mock_generate_report.assert_called_once()
    mock_log.assert_called_once()
