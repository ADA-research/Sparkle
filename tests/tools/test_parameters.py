"""Test methods for the PCS parser classes."""

from pathlib import Path

import ConfigSpace

from sparkle.tools.parameters import PCSConverter, PCSConvention


def test_from_configspace_file() -> None:
    """Test reading a ConfigSpace file with PCSParser."""
    configspace_file = Path("tests/test_files/pcs/test_pcs_hd.json")
    configspace = PCSConverter.parse(configspace_file)
    assert len(configspace) == 17


def test_smac2_pcs_to_configspace() -> None:
    """Test converting a SMAC2 pcs file to ConfigSpace."""
    smac2_file = Path("tests/test_files/pcs/Test-Solver_SMAC2.pcs")
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    configspace = PCSConverter.parse(smac2_file)
    expected = ConfigSpace.ConfigurationSpace.from_yaml(configspace_file)
    expected.name = configspace.name
    assert str(configspace) == str(expected)


def test_irace_pcs_to_configspace() -> None:
    """Test converting a IRACE pcs file to ConfigSpace."""
    irace_file = Path("tests/test_files/pcs/Test-Solver_IRACE.pcs")
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    configspace = PCSConverter.parse(irace_file)

    expected = ConfigSpace.ConfigurationSpace.from_yaml(configspace_file)
    # IRACE does not support default values, replace with whatever is in the output
    assert configspace.keys() == expected.keys()
    expected.name = configspace.name
    for param in list(expected.keys()):
        expected[param].default_value = configspace[param].default_value
    assert str(configspace) == str(expected)


def test_configspace_to_smac2() -> None:
    """Test converting a ConfigSpace to SMAC2 pcs file."""
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    smac2_file = Path("tests/test_files/pcs/Test-Solver_SMAC2.pcs")
    configspace = PCSConverter.parse(configspace_file)
    smac2_export = PCSConverter.export(
        configspace, pcs_format=PCSConvention.SMAC, file=None
    ).splitlines()
    expected_lines = smac2_file.open().read().splitlines()
    for index in range(len(smac2_export)):
        assert smac2_export[index] == expected_lines[index]


def test_configspace_to_irace() -> None:
    """Test converting a ConfigSpace pcs file to IRACE."""
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    irace_file = Path("tests/test_files/pcs/Test-Solver_IRACE.pcs")
    configspace = PCSConverter.parse(configspace_file)
    irace_export = PCSConverter.export(
        configspace, pcs_format=PCSConvention.IRACE, file=None
    ).splitlines()
    expected_lines = irace_file.open().read().splitlines()
    for index in range(len(irace_export)):
        assert irace_export[index] == expected_lines[index]


def test_paramils_pcs_to_configspace() -> None:
    """Test converting a ParamILS pcs file to ConfigSpace."""
    paramils_file = Path("tests/test_files/pcs/clasp-params-paramils.pcs")
    configspace = PCSConverter.parse(paramils_file)
    assert configspace.name == paramils_file.name
    assert len(list(configspace.values())) == 75
