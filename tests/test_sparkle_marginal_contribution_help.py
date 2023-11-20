"""Test functionalities related to the compute marginal contribution help module."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path

from Commands.sparkle_help import sparkle_compute_marginal_contribution_help as scmch
from Commands.sparkle_help.sparkle_feature_data_csv_help import SparkleFeatureDataCSV
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure


class TestMarginalContribution(TestCase):
    """Tests function of Marginal Contribution help."""
    def test_read_marginal_contribution_csv(self: TestCase) -> None:
        """Test for method read_marginal_contribution_csv."""
        pth = Path("Test_data/test_marginal_contribution.csv")
        Path.write_text(pth, "Solvers/CSCCSat,2.068482775510204\nSolvers/MiniSAT,0.0")

        result = [('Solvers/CSCCSat', 2.068482775510204), ('Solvers/MiniSAT', 0.0)]
        output = scmch.read_marginal_contribution_csv(pth)
        assert result == output

    def test_write_marginal_contribution_csv(self: TestCase) -> None:
        """Test for method write_marginal_contribution_csv."""
        pth = Path("Test_Data/test_marginal_contribution.csv")
        object = [('Solvers/CSCCSat', 2.068482775510204), ('Solvers/MiniSAT', 0.0)]
        result = "Solvers/CSCCSat,2.068482775510204\nSolvers/MiniSAT,0.0\n"

        scmch.write_marginal_contribution_csv(pth, object)

        output = ""
        with pth.open("r") as file:
            output = file.read()

        assert result == output

    def test_get_cap_value_list(self: TestCase) -> None:
        """Test for method get_cap_value_list."""
        csv_obj = None
        output = scmch.get_capvalue_list(csv_obj, PerformanceMeasure.RUNTIME)
        assert output == None

        csv_data = ",Solvers/MiniSAT,Solvers/CSCCSat\n"\
                    "Instances/PTN/Ptn-7824-b03.cnf,3000.0,3000.0\n"\
                    "Instances/PTN/Ptn-7824-b15.cnf,3000.0,28.1747\n"\
                    "Instances/PTN/Ptn-7824-b05.cnf,3000.0,3000.0\n"\
                    "Instances/PTN/Ptn-7824-b13.cnf,3000.0,9.98625\n"\
                    "Instances/PTN/Ptn-7824-b21.cnf,117.589,0.107158\n"\
                    "Instances/PTN/Ptn-7824-b19.cnf,3000.0,183.437\n"\
                    "Instances/PTN/Ptn-7824-b17.cnf,3000.0,0.537186\n"\
                    "Instances/PTN/bce7824.cnf,3000.0,3000.0\n"\
                    "Instances/PTN/Ptn-7824-b01.cnf,3000.0,3000.0\n"\
                    "Instances/PTN/Ptn-7824-b11.cnf,3000.0,3000.0\n"\
                    "Instances/PTN/Ptn-7824-b09.cnf,3000.0,196.792\n"\
                    "Instances/PTN/Ptn-7824-b07.cnf,3000.0,3000.0\n"
        csv_path = Path("Test_Data/test_sparkle_performance_data.csv")
        Path.write_text(csv_path, csv_data)
        csv_obj = spdcsv.SparklePerformanceDataCSV(csv_path)
        assert csv_obj.get_column_size() == 2
        result = [3000.0, 3000.0, 3000.0, 3000.0, 117.589, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0]
        output = scmch.get_capvalue_list(csv_obj, PerformanceMeasure.QUALITY_ABSOLUTE)

        assert output == result

    def test_compute_perfect_selector_marginal_contribution(self: TestCase) -> None:
        """Test for method compute_perfect_selector_marginal_contribution."""
        pth = Path("Path to Performance Data")
        result = [('Solvers/CSCCSat', 2.068482775510204), ('Solvers/MiniSAT', 0.0)]  # The expected output
        output = scmch.compute_perfect_selector_marginal_contribution(pth, True)

        self.assertIs(output, result)

    def test_get_list_predict_schedule(self: TestCase) -> None:
        """Test for method get_list_predict_schedule.
        Works on Linux but not Mac due to AutoFolio version
        """
        pth = "Sparkle_Portfolio_Selector/sparkle_portfolio_selector__@@SPARKLE@@__"
        featurecsv = SparkleFeatureDataCSV("Feature_Data/sparkle_feature_data.csv")
        instance_ids = ["Instances/PTN/Ptn-7824-b03.cnf", "Instances/PTN/Ptn-7824-b15.cnf",
                        "Instances/PTN/Ptn-7824-b05.cnf", "Instances/PTN/Ptn-7824-b13.cnf",
                        "Instances/PTN/Ptn-7824-b21.cnf", "Instances/PTN/Ptn-7824-b19.cnf",
                        "Instances/PTN/Ptn-7824-b17.cnf", "Instances/PTN/bce7824.cnf",
                        "Instances/PTN/Ptn-7824-b01.cnf", "Instances/PTN/Ptn-7824-b11.cnf",
                        "Instances/PTN/Ptn-7824-b09.cnf", "Instances/PTN/Ptn-7824-b07.cnf"]
        result = [('Solvers/MiniSAT', 3.0)]

        for instance in instance_ids:
            output = scmch.get_list_predict_schedule(pth, featurecsv, instance)
            assert output == result

    def test_compute_actual_selector_performance(self: TestCase) -> None:
        """Test for method compute_actual_selector_performance."""
        portfiolio_path = "actual_portfolio_selector_path"
        performance_path = "performance_data_csv_path"
        feature_csv_path = "feature_data_csv_path"
        num_instances = -1
        num_solvers = -1
        capvalue_list = list[float] | None

        result = -1.0  # Expected Actual Performance result

        output = scmch.compute_actual_selector_performance(portfiolio_path,
                                                           performance_path,
                                                           feature_csv_path,
                                                           num_instances,
                                                           num_solvers,
                                                           capvalue_list)

        self.assertIs(output, result)

    def test_compute_actual_performance_for_instance(self: TestCase) -> None:
        """Test for method compute_actual_performance_for_instance."""
        # TODO: Write test
        pass

    def test_compute_actual_used_time_for_instance(self: TestCase) -> None:
        """Test for method compute_actual_used_time_for_instance."""
        # TODO: Write test
        pass

    def test_compute_actual_selector_marginal_contribution(self: TestCase) -> None:
        """Test for method compute_actual_selector_marginal_contribution."""
        # TODO: Write test
        pass

    def test_print_rank_list(self: TestCase) -> None:
        """Test for method print_rank_list. Could be irrelevant."""
        # TODO: Write test
        pass

    def test_compute_actual(self: TestCase) -> None:
        """Test for method compute_actual. Could be irrelevant."""
        # TODO: Write test
        pass

    def test_compute_marginal_contribution(self: TestCase) -> None:
        """Test for method compute_marginal_contribution. Could be irrelevant."""
        # TODO: Write test
        pass
