"""Tests for the check command."""
from pathlib import Path
import pytest

from sparkle.CLI import check


@pytest.mark.integration
def test_check_command() -> None:
    """Test check command."""
    # Test failure
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check.main([])  # Test without arguments
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 2

    # TODO: None of these tests actually check the output of the command
    # Test solver
    solver_path = Path("Examples") / "Resources" / "Solvers" / "PbO-CCSAT-Generic"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check.main(["solver", str(solver_path)])  # Test without arguments
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test for instance set
    instance_set_path = Path("Examples") / "Resources" / "Instances" / "PTN"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check.main(["instance-set", str(instance_set_path)])  # Test without arguments
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Test for feature extractor
    extractor_path = Path("Examples") / "Resources" / "Extractors" /\
        "SAT-features-competition2012_revised_without_SatELite"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check.main(["feature-extractor", str(extractor_path)])  # Test without arguments
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # TODO: Test for incorrect/faulty input that warns the user
