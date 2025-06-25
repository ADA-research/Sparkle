"""Tests for the feature extractor CLI entry points."""
import pytest
from pathlib import Path

from sparkle.CLI import add_feature_extractor, remove_feature_extractor


@pytest.mark.integration
def test_add_remove_solver_command(tmp_path: Path,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    """Test initialise command."""
    extractor_path = (Path("Examples") / "Resources" / "Extractors"
                      / "SAT-features-competition2012_"
                        "revised_without_SatELite").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    expected_target = Path("Extractors") / extractor_path.name
    # Smoke test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_feature_extractor.main([str(extractor_path)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert expected_target.exists()
    assert expected_target.is_dir()

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        remove_feature_extractor.main([extractor_path.name])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert not expected_target.exists()

    # Test with symbolic link
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_feature_extractor.main([str(extractor_path.absolute()),
                                    "--no-copy"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert expected_target.is_symlink()
    assert expected_target.is_dir()

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        remove_feature_extractor.main([extractor_path.name])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert not expected_target.exists()

# TODO: Test removing with extractor directory path
# TODO: Test adding / removing with nicknames
# TODO: Test removing with non extractor name/paths for failure
