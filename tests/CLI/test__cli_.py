"""Test for CLI parsing entry point of Sparkle."""

from pathlib import Path
import sys
import pytest
from unittest.mock import patch

from sparkle.CLI import _cli_


def test_commands() -> None:
    """Test if Sparkle correctly resolves the possible command files."""
    commands = _cli_.commands()
    assert set(commands) == set(
        [
            "run_ablation",
            "save_snapshot",
            "check",
            "add_solver",
            "cleanup",
            "remove_instances",
            "generate_report",
            "remove_feature_extractor",
            "jobs",
            "run_solvers",
            "add_feature_extractor",
            "configure_solver",
            "status",
            "initialise",
            "about",
            "run_parallel_portfolio",
            "remove_solver",
            "add_instances",
            "run_portfolio_selector",
            "construct_portfolio_selector",
            "compute_features",
            "load_snapshot",
        ]
    )


def test_main() -> None:
    """Test if Sparkle correctly resolves the right CLI file to run."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, "argv", ["sparkle"]):
            _cli_.main()  # Test without args, should yield usage error
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, "argv", ["sparkle", "about"]):
            _cli_.main()  # Test with about
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, "argv", ["sparkle", "load", "snapshot"]):
            with patch("os.system", new=lambda *args, **kwargs: None):
                _cli_.main()  # Test with two word command
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, "argv", ["sparkle", "aabout"]):
            _cli_.main()  # Test with typo in about
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -2


def test_suggestions(capfd: pytest.CaptureFixture) -> None:
    """Test if Sparkle correctly suggests commands."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, "argv", ["sparkle", "aabout"]):
            _cli_.main()  # Test with typo in about
    out, _ = capfd.readouterr()
    assert "Did you mean <about>?" in out
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -2


@patch("pathlib.Path.home")
def test_auto_complete_install(
    mock_home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test if Sparkle correctly installs autocompletion commands."""
    monkeypatch.chdir(tmp_path)
    profile_path = Path(".bash_profile")
    mock_home.return_value = tmp_path

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, "argv", ["sparkle", "install", "autocomplete"]):
            _cli_.main()
    assert profile_path.exists()
    assert "#----- Sparkle AutoComplete ----" in profile_path.read_text()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
