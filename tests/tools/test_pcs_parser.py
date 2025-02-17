"""Test methods for the PCS parser classes."""
from pathlib import Path

import ConfigSpace

from sparkle.tools.pcsparser import PCSConverter, PCSConvention


def test_from_configspace_file() -> None:
    """Test reading a ConfigSpace file with PCSParser."""
    configspace_file = Path("tests/test_files/pcs/test_pcs_hd.json")
    configspace = PCSConverter.parse(configspace_file)
    assert len(configspace) == 17


def test_smac2_pcs_to_configspace() -> None:
    """Test converting a SMAC2 pcs file to ConfigSpace."""
    smac2_file = Path("tests/test_files/pcs/Test-Solver_SMAC2.pcs")
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.txt")
    configspace = PCSConverter.parse(smac2_file)
    lines_configspace = set(str(configspace).splitlines())
    expected_lines = set(configspace_file.open().read().splitlines())
    assert lines_configspace == expected_lines


def test_irace_pcs_to_configspace() -> None:
    """Test converting a IRACE pcs file to ConfigSpace."""
    irace_file = Path("tests/test_files/pcs/Test-Solver_IRACE.pcs")
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    configspace = PCSConverter.parse(irace_file)

    # IRACE does not support default values, replace with whatever is in the output
    expected = ConfigSpace.ConfigurationSpace.from_yaml(configspace_file)
    assert configspace.keys() == expected.keys()
    for param in list(expected.keys()):
        expected[param].default_value = configspace[param].default_value
    assert str(configspace) == str(expected)


def test_configspace_to_smac2() -> None:
    """Test converting a ConfigSpace to SMAC2 pcs file."""
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    smac2_file = Path("tests/test_files/pcs/Test-Solver_SMAC2.pcs")
    configspace = PCSConverter.parse(configspace_file)
    smac2_export = PCSConverter.export(configspace,
                                       pcs_format=PCSConvention.SMAC,
                                       file=None).splitlines()
    Path("test.txt").open("w+").write("\n".join(smac2_export))
    expected_lines = smac2_file.open().read().splitlines()
    for index in range(len(smac2_export)):
        assert smac2_export[index] == expected_lines[index]


def test_configspace_to_irace() -> None:
    """Test converting a ConfigSpace pcs file to IRACE."""
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.yaml")
    irace_file = Path("tests/test_files/pcs/Test-Solver_IRACE.pcs")
    configspace = PCSConverter.parse(configspace_file)
    irace_export = PCSConverter.export(configspace,
                                       pcs_format=PCSConvention.IRACE,
                                       file=None).splitlines()
    expected_lines = irace_file.open().read().splitlines()
    for index in range(len(irace_export)):
        assert irace_export[index] == expected_lines[index]
