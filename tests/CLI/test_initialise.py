"""Test the initiliase CLI entry point."""
import pytest
from pathlib import Path

from sparkle.CLI import initialise
from sparkle.CLI.help import global_variables as gv


@pytest.mark.integration
def test_initialise_command(tmp_path: Path,
                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    # Fix input calls
    monkeypatch.setattr("builtins.input", lambda _: "Y")

    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # Call the command
        initialise.main([])
        # Check the exit status
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    # Check RunSolver is compiled
    assert gv.settings().DEFAULT_runsolver_exec.exists()
    # TODO: Check with/without specific input to the install questions
