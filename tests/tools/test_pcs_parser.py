"""Test methods for the PCS parser classes."""
from pathlib import Path

from sparkle.tools.pcsparser import PCSParser


def test_from_configspace_file() -> None:
    """Test reading a ConfigSpace file with PCSParser."""
    configspace_file = Path("tests/test_files/pcs/test_pcs_hd.json")
    parser = PCSParser()
    parser.load(str(configspace_file), convention="configspace")
    assert len(parser.pcs) == 17


def test_pcs_to_configspace() -> None:
    """Test converting a SMAC2 pcs file to ConfigSpace."""
    smac2_file = Path("tests/test_files/pcs/Test-Solver.pcs")
    configspace_file = Path("tests/test_files/pcs/Test-Solver_configspace.txt")
    parser = PCSParser()
    parser.load(str(smac2_file), convention="smac")
    for p in parser.pcs.params:
        if p["type"] == "forbidden":
            print(p)
    configspace = parser.get_configspace()
    lines_configspace = set(str(configspace).splitlines())
    expected_lines = set(configspace_file.open().read().splitlines())
    assert lines_configspace == expected_lines
