"""Test for CLI parsing entry point of Sparkle."""

from pathlib import Path
import sys
import pytest
from unittest import mock

from sparkle.CLI import _cli_


def test_commands() -> None:
    """Test if Sparkle correctly resolves the possible command files."""
    commands = _cli_.commands()
    assert set(commands) == set(
        [
            "about",
            "add_solver",
            "add_feature_extractor",
            "add_instances",
            "cleanup",
            "configure_solver",
            "compute_features",
            "construct_portfolio_selector",
            "check",
            "generate_report",
            "jobs",
            "initialise",
            "load_snapshot",
            "remove_instances",
            "run_ablation",
            "remove_feature_extractor",
            "run_solvers",
            "run_parallel_portfolio",
            "remove_solver",
            "run_portfolio_selector",
            "status",
            "save_snapshot",
            "wrap",
        ]
    )


def test_main() -> None:
    """Test if Sparkle correctly resolves the right CLI file to run."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with mock.patch.object(sys, "argv", ["sparkle"]):
            _cli_.main()  # Test without args, should yield usage error
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with mock.patch.object(sys, "argv", ["sparkle", "about"]):
            _cli_.main()  # Test with about
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with mock.patch.object(sys, "argv", ["sparkle", "load", "snapshot"]):
            with mock.patch("os.system", new=lambda *args, **kwargs: None):
                _cli_.main()  # Test with two word command
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with mock.patch.object(sys, "argv", ["sparkle", "aabout"]):
            _cli_.main()  # Test with typo in about
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -2


def test_suggestions(capfd: pytest.CaptureFixture) -> None:
    """Test if Sparkle correctly suggests commands."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with mock.patch.object(sys, "argv", ["sparkle", "aabout"]):
            _cli_.main()  # Test with typo in about
    out, _ = capfd.readouterr()
    assert "Did you mean <about>?" in out
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == -2


def test_auto_complete_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test if Sparkle correctly installs autocompletion commands."""
    monkeypatch.chdir(tmp_path)
    profile_path = Path("bin/activate")
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.touch()

    # sys_prefix.return_value = tmp_path
    with mock.patch("sys.prefix", ""):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            with mock.patch.object(sys, "argv", ["sparkle", "install", "autocomplete"]):
                _cli_.main()
        assert profile_path.exists()
        assert (
            "# -------------------------------- Sparkle Venv Autocomplete ---------------------------------"
            in profile_path.read_text()
        )
        assert pytest_wrapped_e.type is SystemExit
        assert pytest_wrapped_e.value.code == 0
