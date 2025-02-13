"""Test methods for the PCS parser classes."""
from pathlib import Path

from sparkle.tools.pcsparser import PCSConverter


def test_from_configspace_file() -> None:
    """Test reading a ConfigSpace file with PCSParser."""
    configspace_file = Path("tests/test_files/pcs/test_pcs_hd.json")
    configspace = PCSConverter.parse(configspace_file)
    assert len(configspace) == 17


def test_smac2_pcs_to_configspace() -> None:
    """Test converting a SMAC2 pcs file to ConfigSpace."""
    smac2_file = Path("tests/test_files/pcs/Test-Solver.pcs")
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.txt")
    configspace = PCSConverter.parse(smac2_file)
    lines_configspace = set(str(configspace).splitlines())
    expected_lines = set(configspace_file.open().read().splitlines())
    assert lines_configspace == expected_lines
